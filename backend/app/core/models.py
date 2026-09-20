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


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    guest_profile: Mapped[GuestProfile | None] = relationship(back_populates="user")
    host_profile: Mapped[HostProfile | None] = relationship(back_populates="user")
    admin_profile: Mapped[AdminProfile | None] = relationship(back_populates="user")
    roles: Mapped[list[UserRole]] = relationship(back_populates="user")


class GuestProfile(Base):
    __tablename__ = "guest_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(16))
    company: Mapped[str | None] = mapped_column(String(255))
    job_title: Mapped[str | None] = mapped_column(String(255))
    guest_type: Mapped[str] = mapped_column(String(32), default="other")
    city_of_residence: Mapped[str | None] = mapped_column(String(120))

    user: Mapped[User] = relationship(back_populates="guest_profile")
    invitations: Mapped[list[Invitation]] = relationship(back_populates="guest")


class HostProfile(Base):
    __tablename__ = "host_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    department: Mapped[str | None] = mapped_column(String(64))
    city_of_residence: Mapped[str | None] = mapped_column(String(120))

    user: Mapped[User] = relationship(back_populates="host_profile")
    invitations: Mapped[list[Invitation]] = relationship(back_populates="host")


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    user: Mapped[User] = relationship(back_populates="admin_profile")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(Text)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str | None] = mapped_column(Text)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)

    user: Mapped[User] = relationship(back_populates="roles")
    role: Mapped[Role] = relationship()


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    location: Mapped[str | None] = mapped_column(String(255))


class Invitation(Base):
    __tablename__ = "invitations"
    __table_args__ = (
        UniqueConstraint(
            "guest_user_id", "event_id", name="uq_invitation_guest_event"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    guest_user_id: Mapped[int] = mapped_column(
        ForeignKey("guest_profiles.user_id"), index=True
    )
    host_user_id: Mapped[int] = mapped_column(
        ForeignKey("host_profiles.user_id"), index=True
    )
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

    guest: Mapped[GuestProfile] = relationship(back_populates="invitations")
    host: Mapped[HostProfile] = relationship(back_populates="invitations")
    event: Mapped[Event] = relationship()
