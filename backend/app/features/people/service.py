from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError, NotFoundError
from app.core.pagination import Page, PageParams
from app.core.schemas import GuestProfileOut, InvitationOut
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

    def get_person(self, user_id: int) -> PersonDetail:
        guest = self.repo.get(user_id)
        if guest is None:
            raise NotFoundError(f"person {user_id} not found")
        invitations = self.repo.invitations_for(user_id)
        return PersonDetail(
            person=GuestProfileOut.model_validate(guest),
            invitations=[InvitationOut.model_validate(i) for i in invitations],
        )

    def update_person(self, user_id: int, patch: PersonPatch) -> GuestProfileOut:
        guest = self.repo.get(user_id)
        if guest is None:
            raise NotFoundError(f"person {user_id} not found")

        changes = patch.model_dump(exclude_unset=True)
        if changes.get("email"):
            changes["email"] = changes["email"].lower()
        if not changes:
            return GuestProfileOut.model_validate(guest)

        try:
            guest = self.repo.apply_changes(guest, changes)
        except IntegrityError as exc:
            raise ConflictError("email already in use") from exc
        return GuestProfileOut.model_validate(guest)
