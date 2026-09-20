from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, aliased, selectinload

from app.core.models import GuestProfile, HostProfile, Invitation, User
from app.core.scoping import default_event_id
from app.features.invitations.schemas import InvitationFilters

GuestUser = aliased(User)
HostUser = aliased(User)

# sort key -> the column(s) it orders by
_SORTABLE: dict[str, tuple] = {
    "name": (GuestUser.first_name, GuestUser.last_name),
    "company": (GuestProfile.company,),
    "guest_type": (GuestProfile.guest_type,),
    "status": (Invitation.status,),
    "registration_type": (Invitation.registration_type,),
    "check_in_date": (Invitation.check_in_date,),
    "department": (HostProfile.department,),
    "host": (HostUser.first_name, HostUser.last_name),
}

_COMPLIANCE = {"yes": True, "no": False, "pending": None}


class InvitationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def default_event_id(self) -> int | None:
        return default_event_id(self.db)

    def _filtered(self, f: InvitationFilters) -> Select:
        stmt = (
            select(Invitation)
            .join(Invitation.guest)
            .join(GuestUser, GuestProfile.user)
            .join(Invitation.host)
            .join(HostUser, HostProfile.user)
        )
        if f.event_id is not None:
            stmt = stmt.where(Invitation.event_id == f.event_id)
        if f.status:
            stmt = stmt.where(Invitation.status == f.status)
        if f.guest_type:
            stmt = stmt.where(GuestProfile.guest_type == f.guest_type)
        if f.registration_type:
            stmt = stmt.where(Invitation.registration_type == f.registration_type)
        if f.department:
            stmt = stmt.where(HostProfile.department == f.department)
        if f.host_user_id is not None:
            stmt = stmt.where(Invitation.host_user_id == f.host_user_id)
        if f.guest_user_id is not None:
            stmt = stmt.where(Invitation.guest_user_id == f.guest_user_id)
        if f.compliance_approved in _COMPLIANCE:
            stmt = stmt.where(
                Invitation.compliance_approved.is_(_COMPLIANCE[f.compliance_approved])
            )
        if f.search:
            like = f"%{f.search.lower()}%"
            haystack = func.lower(
                func.concat_ws(" ", GuestUser.first_name, GuestUser.last_name)
            )
            stmt = stmt.where(
                or_(
                    haystack.like(like),
                    func.lower(GuestUser.email).like(like),
                    func.lower(GuestProfile.company).like(like),
                )
            )
        return stmt

    def list(
        self, filters: InvitationFilters, *, limit: int, offset: int
    ) -> tuple[list[Invitation], int]:
        stmt = self._filtered(filters)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        cols = _SORTABLE.get(filters.sort, _SORTABLE["name"])
        step = (lambda c: c.desc()) if filters.order == "desc" else (lambda c: c.asc())
        stmt = (
            stmt.order_by(*[step(c) for c in cols], Invitation.id.asc())
            .options(
                selectinload(Invitation.guest).selectinload(GuestProfile.user),
                selectinload(Invitation.host).selectinload(HostProfile.user),
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
                selectinload(Invitation.guest).selectinload(GuestProfile.user),
                selectinload(Invitation.host).selectinload(HostProfile.user),
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
