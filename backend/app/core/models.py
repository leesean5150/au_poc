from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None] = mapped_column(String(16))
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    work_email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    company: Mapped[str | None] = mapped_column(String(255))
    job_title: Mapped[str | None] = mapped_column(String(255))
    guest_type: Mapped[str] = mapped_column(String(32), default="other")
    city_of_residence: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    invitations: Mapped[list[Invitation]] = relationship(back_populates="person")


class Host(Base):
    __tablename__ = "hosts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    city_of_residence: Mapped[str | None] = mapped_column(String(120))
    department: Mapped[str | None] = mapped_column(String(64))

    invitations: Mapped[list[Invitation]] = relationship(back_populates="host")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    event_type: Mapped[str] = mapped_column(String(32))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    location: Mapped[str | None] = mapped_column(String(255))


class Invitation(Base):
    __tablename__ = "invitations"
    __table_args__ = (
        UniqueConstraint("person_id", "event_id", name="uq_invitation_person_event"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id"), index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)

    registration_type: Mapped[str | None] = mapped_column(String(32))
    group_name: Mapped[str | None] = mapped_column(String(255))
    business_case: Mapped[str | None] = mapped_column(Text)
    compliance_approved: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String(48), default="waiting_for_information")

    requires_flights: Mapped[bool | None] = mapped_column(Boolean)
    flight_class: Mapped[str | None] = mapped_column(String(16))
    departure_city: Mapped[str | None] = mapped_column(String(120))
    requires_airport_transfer: Mapped[bool | None] = mapped_column(Boolean)
    transfer_type: Mapped[str | None] = mapped_column(String(16))
    requires_accommodation: Mapped[bool | None] = mapped_column(Boolean)
    check_in_date: Mapped[date | None] = mapped_column(Date)
    check_out_date: Mapped[date | None] = mapped_column(Date)

    allocated_tennis_session: Mapped[str | None] = mapped_column(String(64))
    workshop: Mapped[str | None] = mapped_column(String(120))
    additional_experience: Mapped[str | None] = mapped_column(String(120))
    sightseeing_contact_email: Mapped[str | None] = mapped_column(String(255))
    additional_information: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    person: Mapped[Person] = relationship(back_populates="invitations")
    host: Mapped[Host] = relationship(back_populates="invitations")
    event: Mapped[Event] = relationship()
