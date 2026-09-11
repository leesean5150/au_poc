from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError, NotFoundError
from app.core.pagination import Page, PageParams
from app.core.schemas import GuestOut, PersonOut
from app.features.people.repository import PeopleRepository
from app.features.people.schemas import PersonDetail, PersonFilters, PersonPatch, PersonRow


class PeopleService:
    def __init__(self, repo: PeopleRepository) -> None:
        self.repo = repo

    def list_people(self, filters: PersonFilters, page: PageParams) -> Page[PersonRow]:
        rows, total = self.repo.fetch(
            filters, limit=page.page_size, offset=page.offset
        )
        return Page[PersonRow](
            items=[PersonRow.model_validate(row) for row in rows],
            total=total,
            page=page.page,
            page_size=page.page_size,
        )

    def get_person(self, person_id: int) -> PersonDetail:
        person = self.repo.get(person_id)
        if person is None:
            raise NotFoundError(f"person {person_id} not found")
        invitations = self.repo.invitations_for(person_id)
        return PersonDetail(
            person=PersonOut.model_validate(person),
            invitations=[GuestOut.model_validate(i) for i in invitations],
        )

    def update_person(self, person_id: int, patch: PersonPatch) -> PersonOut:
        person = self.repo.get(person_id)
        if person is None:
            raise NotFoundError(f"person {person_id} not found")

        changes = patch.model_dump(exclude_unset=True)
        if changes.get("work_email"):
            changes["work_email"] = changes["work_email"].lower()
        if not changes:
            return PersonOut.model_validate(person)

        try:
            person = self.repo.apply_changes(person, changes)
        except IntegrityError as exc:
            raise ConflictError("work_email already in use") from exc
        return PersonOut.model_validate(person)
