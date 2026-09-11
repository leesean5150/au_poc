from collections import Counter
from datetime import date

from app.config import get_settings
from app.core.constants import STATUS_ORDER
from app.core.errors import NotFoundError
from app.core.models import Invitation
from app.features.stats.repository import StatsRepository
from app.features.stats.schemas import (
    ComplianceBreakdown,
    LogisticsBreakdown,
    NextEvent,
    StatsEvent,
    StatsOverview,
    UpcomingEvent,
)


def _today() -> date:
    raw = get_settings().app_now.strip()
    if raw:
        try:
            return date.fromisoformat(raw[:10])
        except ValueError:
            pass
    return date.today()


class StatsService:
    def __init__(self, repo: StatsRepository) -> None:
        self.repo = repo

    def overview(self, event_id: int | None) -> StatsOverview:
        event = self.repo.event(event_id)
        if event is None:
            raise NotFoundError("no event to report on")

        invitations = self.repo.invitations_for_event(event.id)
        today = _today()

        by_status = {s: 0 for s in STATUS_ORDER}
        for inv in invitations:
            by_status[inv.status] = by_status.get(inv.status, 0) + 1

        decided = by_status["accepted"] + by_status["declined"]
        next_event, upcoming = self._events(today)

        return StatsOverview(
            event=StatsEvent.model_validate(event),
            total_guests=len(invitations),
            by_status=by_status,
            invites_sent=by_status["invite_sent"]
            + by_status["accepted"]
            + by_status["declined"],
            invites_outstanding=by_status["waiting_for_information"]
            + by_status["to_send_invite"],
            ready_to_send=by_status["to_send_invite"],
            blocked_on_info=by_status["waiting_for_information"],
            acceptance_rate=(by_status["accepted"] / decided) if decided else None,
            compliance=self._compliance(invitations),
            logistics=self._logistics(invitations),
            next_event=next_event,
            upcoming_events=upcoming[:5],
            guests_by_department=self._group(
                invitations, lambda i: i.host.department
            ),
            guests_by_type=self._group(
                invitations, lambda i: i.person.guest_type
            ),
        )

    @staticmethod
    def _compliance(invitations: list[Invitation]) -> ComplianceBreakdown:
        return ComplianceBreakdown(
            approved=sum(1 for i in invitations if i.compliance_approved is True),
            rejected=sum(1 for i in invitations if i.compliance_approved is False),
            pending=sum(1 for i in invitations if i.compliance_approved is None),
        )

    @staticmethod
    def _logistics(invitations: list[Invitation]) -> LogisticsBreakdown:
        return LogisticsBreakdown(
            need_flights=sum(1 for i in invitations if i.requires_flights),
            need_accommodation=sum(
                1 for i in invitations if i.requires_accommodation
            ),
            need_transfer=sum(
                1 for i in invitations if i.requires_airport_transfer
            ),
        )

    @staticmethod
    def _group(invitations: list[Invitation], key) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for inv in invitations:
            value = key(inv)
            if value:
                counter[value] += 1
        return dict(counter)

    def _events(
        self, today: date
    ) -> tuple[NextEvent | None, list[UpcomingEvent]]:
        upcoming = sorted(
            (e for e in self.repo.all_events() if (e.starts_on - today).days >= 0),
            key=lambda e: e.starts_on,
        )
        if not upcoming:
            return None, []
        first = upcoming[0]
        next_event = NextEvent(
            name=first.name,
            starts_on=first.starts_on,
            days_until=(first.starts_on - today).days,
            event_type=first.event_type,
        )
        rows = [
            UpcomingEvent(
                name=e.name,
                starts_on=e.starts_on,
                days_until=(e.starts_on - today).days,
            )
            for e in upcoming
        ]
        return next_event, rows
