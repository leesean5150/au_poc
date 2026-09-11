from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.core.schemas import GuestOut
from app.features.guests.repository import GuestRepository
from app.features.guests.schemas import GuestFilters, GuestPatch


class GuestService:
    def __init__(self, repo: GuestRepository) -> None:
        self.repo = repo

    def list_guests(self, filters: GuestFilters, page: PageParams) -> Page[GuestOut]:
        # List endpoints scope to the default (earliest) event unless told otherwise.
        if filters.event_id is None:
            filters = filters.model_copy(
                update={"event_id": self.repo.default_event_id()}
            )

        rows, total = self.repo.list(
            filters, limit=page.page_size, offset=page.offset
        )
        return Page[GuestOut](
            items=[GuestOut.model_validate(row) for row in rows],
            total=total,
            page=page.page,
            page_size=page.page_size,
        )

    def get_guest(self, invitation_id: int) -> GuestOut:
        inv = self.repo.get(invitation_id)
        if inv is None:
            raise NotFoundError(f"guest {invitation_id} not found")
        return GuestOut.model_validate(inv)

    def update_guest(self, invitation_id: int, patch: GuestPatch) -> GuestOut:
        inv = self.repo.get(invitation_id)
        if inv is None:
            raise NotFoundError(f"guest {invitation_id} not found")
        changes = patch.model_dump(exclude_unset=True)
        if changes:
            inv = self.repo.apply_changes(inv, changes)
        return GuestOut.model_validate(inv)
