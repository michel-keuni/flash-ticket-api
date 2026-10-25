import asyncio
import uuid
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.models import Event, EventStatus  # Ajuste selon tes dossiers
from app.core.database import AsyncSessionLocal
from tests.utils import generate_test_token


@pytest.mark.asyncio
async def test_concurrent_reservations_prevent_overbooking():
    # 1. Création d'un événement réel en BDD avec seulement 2 billets
    # async with AsyncSessionLocal() as db:
    #     test_event = Event(
    #         title="Vente Flash Test Concurrence",
    #         total_capacity=2,
    #         available_stock=2,
    #         price=100.0,
    #         start_time=datetime.now(timezone.utc) - timedelta(minutes=5),
    #         end_time=datetime.now(timezone.utc) + timedelta(hours=1),
    #         status=EventStatus.LIVE,
    #     )
    #     db.add(test_event)
    #     await db.commit()
    #     await db.refresh(test_event)
    #     event_id = str(test_event.id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await  ac.post(
            "api/v1/events",
            json={
                "title":"Vente Flash Test Concurrence",
                "total_capacity":2,
                "available_stock":2,
                "price":100.0,
                "start_time":f"{datetime.now(timezone.utc) - timedelta(minutes=5)}",
                "end_time":f"{datetime.now(timezone.utc) + timedelta(hours=1)}",
                "status":"LIVE",
            },

        )
        data = resp.json()
        event_id = data["id"]
        return resp

    # 2. Exécution de 10 réservations simultanées pour cet événement
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:

        async def make_reservation(i: int):
            # Simulation d'utilisateurs et de clés d'idempotence différents
            headers = {
                "Authorization": f"Bearer {generate_test_token()}",
                "X-Idempotency-Key": str(uuid.uuid4()),
            }
            return await ac.post(
                f"/api/v1/events/{event_id}/reserve",
                json={"quantity": 1},
                headers=headers,
            )

        # Lancement simultané des 10 requêtes
        tasks = [make_reservation(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)

    # 3. Tri des réponses
    successes = [r for r in responses if r.status_code == 201]
    conflicts = [r for r in responses if r.status_code == 409]
    not_founds = [r for r in responses if r.status_code == 404]

    print(f"\n[RÉSULTATS] 201 Created: {len(successes)} | 409 Conflict: {len(conflicts)} | 404 Not Found: {len(not_founds)}")

    # 4. ASSERTIONS STRICTES
    assert len(not_founds) == 0, "Aucune requête ne devrait renvoyer 404"
    assert len(successes) == 2, "Seuls 2 billets étaient disponibles, exactement 2 requêtes doivent réussir"
    assert len(conflicts) == 8, "Les 8 autres requêtes doivent être rejetées avec un conflit (HTTP 409)"