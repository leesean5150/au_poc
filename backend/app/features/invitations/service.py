from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.core.schemas import InvitationOut
from app.features.invitations.repository import InvitationRepository
from app.features.invitations.schemas import InvitationFilters, InvitationPatch


class InvitationService:
    def __init__(self, repo: InvitationRepository) -> None:
        self.repo = repo

    def list_invitations(
        self, filters: InvitationFilters, page: PageParams
    ) -> Page[InvitationOut]:
        # List endpoints scope to the default (earliest) event unless told otherwise.
        if filters.event_id is None:
            filters = filters.model_copy(
                update={"event_id": self.repo.default_event_id()}
            )

        rows, total = self.repo.list(
            filters, limit=page.page_size, offset=page.offset
        )
        return Page[InvitationOut](
            items=[InvitationOut.model_validate(row) for row in rows],
            total=total,
            page=page.page,
            page_size=page.page_size,
        )

    def get_invitation(self, invitation_id: int) -> InvitationOut:
        inv = self.repo.get(invitation_id)
        if inv is None:
            raise NotFoundError(f"invitation {invitation_id} not found")
        return InvitationOut.model_validate(inv)

    def update_invitation(
        self, invitation_id: int, patch: InvitationPatch
    ) -> InvitationOut:
        inv = self.repo.get(invitation_id)
        if inv is None:
            raise NotFoundError(f"invitation {invitation_id} not found")
        changes = patch.model_dump(exclude_unset=True)
        if changes:
            inv = self.repo.apply_changes(inv, changes)
        return InvitationOut.model_validate(inv)
