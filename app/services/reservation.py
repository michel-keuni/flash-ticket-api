import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Event, EventStatus, Reservation, ReservationStatus
from app.schemas.schemas import ReservationCreate


async def create_reservation_service(
    db: AsyncSession,
    event_id: uuid.UUID,
    user_id: str,
    idempotency_key: str,
    payload: ReservationCreate,
) -> Reservation:
    # 1. RM-05 : Gestion de l'idempotence
    existing_reservation = await db.scalar(
        select(Reservation).where(Reservation.idempotency_key == idempotency_key)
    )
    if existing_reservation:
        return existing_reservation

    # 2. RM-04 : Verrouillage strict au niveau de la ligne (SELECT ... FOR UPDATE)
    # Bloque les autres transactions sur cet événement précis jusqu'à la fin de celle-ci
    stmt = (
        select(Event)
        .where(Event.id == event_id)
        .with_for_update()
    )
    event = await db.scalar(stmt)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement introuvable"
        )

    # 3. RM-01 : Validation de la fenêtre temporelle et du statut
    now = datetime.now(timezone.utc)
    if event.status != EventStatus.LIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La vente pour cet événement n'est pas ouverte"
        )
    if not (event.start_time <= now <= event.end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="En dehors de la fenêtre d'ouverture de la vente"
        )

    # 4. RM-02 : Vérification du quota utilisateur (Max 4 billets actifs)
    active_user_tickets_stmt = (
        select(func.coalesce(func.sum(Reservation.quantity), 0))
        .where(Reservation.user_id == user_id)
        .where(Reservation.event_id == event_id)
        .where(Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED]))
    )
    user_ticket_count = await db.scalar(active_user_tickets_stmt)

    if user_ticket_count + payload.quantity > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quota dépassé : vous possédez déjà {user_ticket_count} billets (max 4)"
        )

    # 5. RM-04 : Vérification et décrémentation atomique du stock
    if event.available_stock < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock insuffisant pour satisfaire cette demande"
        )

    event.available_stock -= payload.quantity

    # 6. RM-03 : Création de la réservation avec TTL de 10 minutes
    expires_at = now + timedelta(minutes=10)
    reservation = Reservation(
        event_id=event_id,
        user_id=user_id,
        quantity=payload.quantity,
        status=ReservationStatus.PENDING,
        idempotency_key=idempotency_key,
        expires_at=expires_at,
    )

    db.add(reservation)
    # Le commit sera exécuté automatiquement par le middleware/get_db
    await db.flush()
    await db.refresh(reservation)

    return reservation