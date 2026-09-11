from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.models import Host, Invitation, Person
from app.core.scoping import default_event_id
from app.features.guests.schemas import GuestFilters

# sort key -> the column(s) it orders by
_SORTABLE: dict[str, tuple] = {
    "name": (Person.first_name, Person.last_name),
    "company": (Person.company,),
    "guest_type": (Person.guest_type,),
    "status": (Invitation.status,),
    "registration_type": (Invitation.registration_type,),
    "check_in_date": (Invitation.check_in_date,),
    "department": (Host.department,),
    "host": (Host.first_name, Host.last_name),
}

_COMPLIANCE = {"yes": True, "no": False, "pending": None}


class GuestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def default_event_id(self) -> int | None:
        return default_event_id(self.db)

    def _filtered(self, f: GuestFilters) -> Select:
        stmt = select(Invitation).join(Invitation.person).join(Invitation.host)
        if f.event_id is not None:
            stmt = stmt.where(Invitation.event_id == f.event_id)
        if f.status:
            stmt = stmt.where(Invitation.status == f.status)
        if f.guest_type:
            stmt = stmt.where(Person.guest_type == f.guest_type)
        if f.registration_type:
            stmt = stmt.where(Invitation.registration_type == f.registration_type)
        if f.department:
            stmt = stmt.where(Host.department == f.department)
        if f.host_id is not None:
            stmt = stmt.where(Invitation.host_id == f.host_id)
        if f.person_id is not None:
            stmt = stmt.where(Invitation.person_id == f.person_id)
        if f.compliance_approved in _COMPLIANCE:
            stmt = stmt.where(
                Invitation.compliance_approved.is_(_COMPLIANCE[f.compliance_approved])
            )
        if f.search:
            like = f"%{f.search.lower()}%"
            haystack = func.lower(
                func.concat_ws(" ", Person.first_name, Person.last_name)
            )
            stmt = stmt.where(
                or_(
                    haystack.like(like),
                    func.lower(Person.work_email).like(like),
                    func.lower(Person.company).like(like),
                )
            )
        return stmt

    def list(
        self, filters: GuestFilters, *, limit: int, offset: int
    ) -> tuple[list[Invitation], int]:
        stmt = self._filtered(filters)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        cols = _SORTABLE.get(filters.sort, _SORTABLE["name"])
        step = (lambda c: c.desc()) if filters.order == "desc" else (lambda c: c.asc())
        stmt = (
            stmt.order_by(*[step(c) for c in cols], Invitation.id.asc())
            .options(
                selectinload(Invitation.person),
                selectinload(Invitation.host),
                selectinload(Invitation.event),
            )
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt)), int(total)

    def get(self, invitation_id: int) -> Invitation | None:
        stmt = (
            select(Invitation)
            .where(Invitation.id == invitation_id)
            .options(
                selectinload(Invitation.person),
                selectinload(Invitation.host),
                selectinload(Invitation.event),
            )
        )
        return self.db.scalars(stmt).first()

    def apply_changes(self, inv: Invitation, changes: dict) -> Invitation:
        for key, value in changes.items():
            setattr(inv, key, value)
        self.db.commit()
        self.db.refresh(inv)
        return inv
