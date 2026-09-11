from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.models import Event, Invitation, Person
from app.features.people.schemas import PersonFilters

_SORTABLE: dict[str, tuple] = {
    "name": (Person.first_name, Person.last_name),
    "company": (Person.company,),
    "job_title": (Person.job_title,),
    "guest_type": (Person.guest_type,),
    "city": (Person.city_of_residence,),
    "invitation_count": (func.count(Invitation.id),),
}


class PeopleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _search(self, stmt: Select, f: PersonFilters) -> Select:
        if not f.search:
            return stmt
        like = f"%{f.search.lower()}%"
        name = func.lower(func.concat_ws(" ", Person.first_name, Person.last_name))
        return stmt.where(
            or_(
                name.like(like),
                func.lower(Person.work_email).like(like),
                func.lower(Person.company).like(like),
            )
        )

    def fetch(
        self, filters: PersonFilters, *, limit: int, offset: int
    ) -> "tuple[list[Person], int]":
        total = self.db.scalar(
            self._search(select(func.count(Person.id)), filters)
        ) or 0

        cols = _SORTABLE.get(filters.sort, _SORTABLE["name"])
        step = (lambda c: c.desc()) if filters.order == "desc" else (lambda c: c.asc())
        stmt = (
            self._search(
                select(Person, func.count(Invitation.id)).outerjoin(
                    Invitation, Invitation.person_id == Person.id
                ),
                filters,
            )
            .group_by(Person.id)
            .order_by(*[step(c) for c in cols], Person.id.asc())
            .limit(limit)
            .offset(offset)
        )

        rows = []
        for person, count in self.db.execute(stmt).all():
            person.invitation_count = count
            rows.append(person)
        return rows, int(total)

    def get(self, person_id: int) -> Person | None:
        return self.db.get(Person, person_id)

    def invitations_for(self, person_id: int) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .join(Invitation.event)
            .where(Invitation.person_id == person_id)
            .options(
                selectinload(Invitation.person),
                selectinload(Invitation.host),
                selectinload(Invitation.event),
            )
            .order_by(Event.starts_on.asc(), Invitation.id.asc())
        )
        return list(self.db.scalars(stmt))

    def apply_changes(self, person: Person, changes: dict) -> Person:
        for key, value in changes.items():
            setattr(person, key, value)
        self.db.commit()
        self.db.refresh(person)
        return person
