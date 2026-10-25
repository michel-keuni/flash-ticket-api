import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Event
from app.schemas.schemas import EventCreate, EventResponse, ReservationCreate, ReservationResponse
from app.services.reservation import create_reservation_service

router = APIRouter()


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
):
    """Créer un événement (utilitaire pour alimenter les ventes flash)."""
    event = Event(
        title=payload.title,
        description=payload.description,
        total_capacity=payload.total_capacity,
        available_stock=payload.total_capacity,
        price=payload.price,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.get("/events", response_model=list[EventResponse])
async def list_events(
    db: AsyncSession = Depends(get_db),
):
    """Lister tous les événements enregistrés."""
    result = await db.execute(select(Event))
    return result.scalars().all()


@router.post(
    "/events/{event_id}/reserve",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def reserve_tickets(
    event_id: uuid.UUID,
    payload: ReservationCreate,
    x_idempotency_key: Annotated[
        str,
        Header(
            alias="X-Idempotency-Key",
            description="UUID unique généré côté client pour garantir l'idempotence",
        ),
    ],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Initier une réservation de billets sous forte charge avec verrouillage anti-race condition."""
    reservation = await create_reservation_service(
        db=db,
        event_id=event_id,
        user_id=user_id,
        idempotency_key=x_idempotency_key,
        payload=payload,
    )
    return reservation