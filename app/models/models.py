import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class EventStatus(str, Enum):
    DRAFT = "DRAFT"
    LIVE = "LIVE"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Gestion du stock
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Fenêtres temporelles (RM-01)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus),
        default=EventStatus.DRAFT,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relation vers les réservations
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="event",
        cascade="all, delete-orphan"
    )

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus),
        default=ReservationStatus.PENDING,
        nullable=False
    )
    
    # Idempotence (RM-05) : Clé unique fournie par le client pour éviter les doublons
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # TTL de 10 minutes (RM-03)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relation vers l'événement
    event: Mapped[Event] = relationship("Event", back_populates="reservations")