from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.models import GuestProfile, HostProfile, Invitation, User
from app.core.scoping import default_event_id
from app.features.hosts.schemas import HostFilters

_SORTABLE: dict[str, tuple] = {
    "name": (User.first_name, User.last_name),
    "department": (HostProfile.department,),
    "city": (HostProfile.city_of_residence,),
    "guest_count": (func.count(Invitation.id),),
}


class HostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def resolve_event_id(self, event_id: int | None) -> int | None:
        return event_id if event_id is not None else default_event_id(self.db)

    def _narrow(self, stmt: Select, f: HostFilters) -> Select:
        if f.department:
            stmt = stmt.where(HostProfile.department == f.department)
        if f.search:
            like = f"%{f.search.lower()}%"
            name = func.lower(func.concat_ws(" ", User.first_name, User.last_name))
            stmt = stmt.where(
                or_(name.like(like), func.lower(User.email).like(like))
            )
        return stmt

    def fetch(
        self, filters: HostFilters, event_id: int | None, *, limit: int, offset: int
    ) -> "tuple[list[HostProfile], int]":
        base = select(HostProfile).join(HostProfile.user)
        total = self.db.scalar(
            self._narrow(select(func.count()).select_from(base.subquery()), filters)
        ) or 0

        join_cond = and_(
            Invitation.host_user_id == HostProfile.user_id,
            Invitation.event_id == event_id,
        )
        cols = _SORTABLE.get(filters.sort, _SORTABLE["name"])
        step = (lambda c: c.desc()) if filters.order == "desc" else (lambda c: c.asc())
        stmt = (
            self._narrow(
                select(HostProfile, func.count(Invitation.id))
                .join(HostProfile.user)
                .outerjoin(Invitation, join_cond),
                filters,
            )
            .group_by(HostProfile.user_id, User.id)
            .order_by(*[step(c) for c in cols], HostProfile.user_id.asc())
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(stmt).all()
        host_user_ids = [h.user_id for h, _ in rows]

        breakdown = self._status_breakdown(host_user_ids, event_id)
        hosts = []
        for host, count in rows:
            host.guest_count = count
            host.by_status = breakdown.get(host.user_id, {})
            hosts.append(host)
        return hosts, int(total)

    def _status_breakdown(
        self, host_user_ids: list[int], event_id: int | None
    ) -> dict[int, dict[str, int]]:
        if not host_user_ids:
            return {}
        stmt = (
            select(Invitation.host_user_id, Invitation.status, func.count())
            .where(
                Invitation.host_user_id.in_(host_user_ids),
                Invitation.event_id == event_id,
            )
            .group_by(Invitation.host_user_id, Invitation.status)
        )
        out: dict[int, dict[str, int]] = {}
        for host_user_id, status, n in self.db.execute(stmt).all():
            out.setdefault(host_user_id, {})[status] = n
        return out

    def get(self, host_user_id: int) -> HostProfile | None:
        return self.db.get(HostProfile, host_user_id)

    def invitations_for(
        self, host_user_id: int, event_id: int | None
    ) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .where(
                Invitation.host_user_id == host_user_id,
                Invitation.event_id == event_id,
            )
            .options(
                selectinload(Invitation.guest).selectinload(GuestProfile.user),
                selectinload(Invitation.host).selectinload(HostProfile.user),
                selectinload(Invitation.event),
            )
            .order_by(Invitation.id.asc())
        )
        return list(self.db.scalars(stmt))
