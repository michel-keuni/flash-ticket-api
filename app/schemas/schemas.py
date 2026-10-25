import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.models import EventStatus, ReservationStatus

# --- SCHÉMAS EVENT ---

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    total_capacity: int = Field(..., gt=0, description="Capacité totale de la vente flash")
    price: float = Field(..., ge=0, description="Prix unitaire du billet")
    start_time: datetime
    end_time: datetime

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: uuid.UUID
    available_stock: int
    status: EventStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- SCHÉMAS RESERVATION ---

class ReservationCreate(BaseModel):
    quantity: int = Field(..., gt=0, le=4, description="Nombre de billets (max 4 selon RM-02)")

class ReservationResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    user_id: str
    quantity: int
    status: ReservationStatus
    idempotency_key: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)