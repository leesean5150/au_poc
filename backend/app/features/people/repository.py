from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.models import Event, GuestProfile, HostProfile, Invitation, User
from app.features.people.schemas import PersonFilters

_SORTABLE: dict[str, tuple] = {
    "name": (User.first_name, User.last_name),
    "company": (GuestProfile.company,),
    "job_title": (GuestProfile.job_title,),
    "guest_type": (GuestProfile.guest_type,),
    "city": (GuestProfile.city_of_residence,),
    "invitation_count": (func.count(Invitation.id),),
}


class PeopleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _search(self, stmt: Select, f: PersonFilters) -> Select:
        if not f.search:
            return stmt
        like = f"%{f.search.lower()}%"
        name = func.lower(func.concat_ws(" ", User.first_name, User.last_name))
        return stmt.where(
            or_(
                name.like(like),
                func.lower(User.email).like(like),
                func.lower(GuestProfile.company).like(like),
            )
        )

    def fetch(
        self, filters: PersonFilters, *, limit: int, offset: int
    ) -> "tuple[list[GuestProfile], int]":
        base = select(GuestProfile).join(GuestProfile.user)
        total = self.db.scalar(
            self._search(select(func.count()).select_from(base.subquery()), filters)
        ) or 0

        cols = _SORTABLE.get(filters.sort, _SORTABLE["name"])
        step = (lambda c: c.desc()) if filters.order == "desc" else (lambda c: c.asc())
        stmt = (
            self._search(
                select(GuestProfile, func.count(Invitation.id))
                .join(GuestProfile.user)
                .outerjoin(
                    Invitation, Invitation.guest_user_id == GuestProfile.user_id
                ),
                filters,
            )
            .group_by(GuestProfile.user_id, User.id)
            .order_by(*[step(c) for c in cols], GuestProfile.user_id.asc())
            .limit(limit)
            .offset(offset)
        )

        rows = []
        for guest, count in self.db.execute(stmt).all():
            guest.invitation_count = count
            rows.append(guest)
        return rows, int(total)

    def get(self, user_id: int) -> GuestProfile | None:
        return self.db.get(GuestProfile, user_id)

    def invitations_for(self, user_id: int) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .join(Invitation.event)
            .where(Invitation.guest_user_id == user_id)
            .options(
                selectinload(Invitation.guest).selectinload(GuestProfile.user),
                selectinload(Invitation.host).selectinload(HostProfile.user),
                selectinload(Invitation.event),
            )
            .order_by(Event.starts_on.asc(), Invitation.id.asc())
        )
        return list(self.db.scalars(stmt))

    def apply_changes(self, guest: GuestProfile, changes: dict) -> GuestProfile:
        user_changes = {
            k: changes.pop(k) for k in ("first_name", "last_name", "email") if k in changes
        }
        if user_changes:
            for key, value in user_changes.items():
                setattr(guest.user, key, value)
        for key, value in changes.items():
            setattr(guest, key, value)
        self.db.commit()
        self.db.refresh(guest)
        return guest
