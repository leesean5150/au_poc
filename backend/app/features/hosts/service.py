from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.core.schemas import GuestOut, HostOut
from app.features.hosts.repository import HostRepository
from app.features.hosts.schemas import HostDetail, HostFilters, HostRow


class HostService:
    def __init__(self, repo: HostRepository) -> None:
        self.repo = repo

    def list_hosts(self, filters: HostFilters, page: PageParams) -> Page[HostRow]:
        event_id = self.repo.resolve_event_id(filters.event_id)
        rows, total = self.repo.fetch(
            filters, event_id, limit=page.page_size, offset=page.offset
        )
        return Page[HostRow](
            items=[HostRow.model_validate(row) for row in rows],
            total=total,
            page=page.page,
            page_size=page.page_size,
        )

    def get_host(self, host_id: int, event_id: int | None) -> HostDetail:
        host = self.repo.get(host_id)
        if host is None:
            raise NotFoundError(f"host {host_id} not found")
        scoped = self.repo.resolve_event_id(event_id)
        invitations = self.repo.invitations_for(host_id, scoped)
        return HostDetail(
            host=HostOut.model_validate(host),
            invitations=[GuestOut.model_validate(i) for i in invitations],
        )
