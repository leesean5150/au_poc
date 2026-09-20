"""Idempotent seed: import the bundled xlsx when the DB has no invitations —
each row's own "Allocated Tennis Session" label produces its event, so no
synthetic event data is fabricated here. Also seeds the RBAC tables (roles)
and a handful of demo login accounts so the JWT/RBAC path can be exercised
without a registration flow.
"""

from __future__ import annotations

import sys

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.db import SessionLocal
from app.core.models import AdminProfile, GuestProfile, HostProfile, Invitation, Role, User, UserRole
from app.core.security import hash_password
from app.features.imports.importer import import_workbook

# Seeded roles — kept coarse; new permissions/finer roles are added when a
# concrete need for them shows up, not speculatively.
ROLES = ["super_admin", "ops_admin", "host", "guest"]

# POC-only demo accounts so the JWT/RBAC path can be exercised end-to-end.
# Bulk-imported guests/hosts get no password (see importer.py) — these three
# are the only accounts that can actually log in.
DEMO_PASSWORD = "password123"
DEMO_ACCOUNTS = [
    {
        "email": "demo.admin@poc.local",
        "first_name": "Demo",
        "last_name": "Admin",
        "role": "super_admin",
        "profile": AdminProfile,
    },
    {
        "email": "demo.host@poc.local",
        "first_name": "Demo",
        "last_name": "Host",
        "role": "host",
        "profile": HostProfile,
    },
    {
        "email": "demo.guest@poc.local",
        "first_name": "Demo",
        "last_name": "Guest",
        "role": "guest",
        "profile": GuestProfile,
    },
]


def seed(*, force: bool = False) -> None:
    settings = get_settings()
    with SessionLocal() as db:
        _seed_roles(db)
        _seed_demo_accounts(db)
        existing = db.scalar(select(func.count()).select_from(Invitation)) or 0
        if existing and not force:
            db.commit()
            print(f"[seed] {existing} invitations present — skipping xlsx import")
            return
        result = import_workbook(db, settings.data_file)
        db.commit()
        print(f"[seed] {result}")


def _seed_roles(db: Session) -> None:
    for name in ROLES:
        if db.scalar(select(Role).where(Role.name == name)) is None:
            db.add(Role(name=name))
    db.flush()


def _seed_demo_accounts(db: Session) -> None:
    for spec in DEMO_ACCOUNTS:
        user = db.scalar(select(User).where(User.email == spec["email"]))
        if user is None:
            user = User(
                email=spec["email"],
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                password_hash=hash_password(DEMO_PASSWORD),
                status="active",
            )
            db.add(user)
            db.flush()

            profile_cls = spec["profile"]
            if profile_cls is GuestProfile:
                db.add(GuestProfile(user_id=user.id, guest_type="staff"))
            elif profile_cls is HostProfile:
                db.add(HostProfile(user_id=user.id, department="Executive"))
            else:
                db.add(AdminProfile(user_id=user.id))

        role = db.scalar(select(Role).where(Role.name == spec["role"]))
        if role is not None and db.get(UserRole, (user.id, role.id)) is None:
            db.add(UserRole(user_id=user.id, role_id=role.id))
    db.flush()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
