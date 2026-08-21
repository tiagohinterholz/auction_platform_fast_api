import uuid
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.core.email.email_service_interface import IEmailService
from app.modules.auction.application.handlers.auction_finished_notification_handler import (
    AuctionFinishedNotificationHandler,
)
from app.modules.auction.domain.events.auction_events import AuctionFinishedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.users.infrastructure.repository.users_repository import UserRepository


def _bid(user_id: uuid.UUID, amount: str) -> SimpleNamespace:
    return SimpleNamespace(user_id=user_id, amount=Decimal(amount))


def _user(email: str, name: str) -> SimpleNamespace:
    return SimpleNamespace(email=email, name=name)


class TestAuctionFinishedNotificationHandler:

    def setup_method(self):
        self.auction_id = uuid.uuid4()
        self.auction_repo = AsyncMock(spec=AuctionReadRepository)
        self.bid_repo = AsyncMock(spec=BidReadRepository)
        self.users_repo = AsyncMock(spec=UserRepository)
        self.email_service = AsyncMock(spec=IEmailService)
        self.handler = AuctionFinishedNotificationHandler(
            auction_read_repository=self.auction_repo,
            bid_read_repository=self.bid_repo,
            users_repository=self.users_repo,
            email_service=self.email_service,
        )
        self.auction_repo.get_by_id.return_value = SimpleNamespace(
            id=self.auction_id, title="iPhone 15"
        )

    def _event(self) -> AuctionFinishedEvent:
        return AuctionFinishedEvent(payload={"id": str(self.auction_id), "end_time": ""})

    async def test_notifies_winner_and_losers_by_highest_bid_per_user(self):
        winner_id, loser_id = uuid.uuid4(), uuid.uuid4()
        self.bid_repo.find_all_by_auction_id.return_value = [
            _bid(loser_id, "100.00"),
            _bid(winner_id, "150.00"),
            _bid(loser_id, "120.00"),  # loser's best bid, still below winner
        ]
        self.users_repo.get_by_id.side_effect = lambda uid: {
            str(winner_id): _user("winner@test.com", "Ana"),
            str(loser_id): _user("loser@test.com", "Bia"),
        }[uid]

        await self.handler.handle(self._event())

        assert self.email_service.send.call_count == 2
        recipients = {call.kwargs["to"] for call in self.email_service.send.call_args_list}
        assert recipients == {"winner@test.com", "loser@test.com"}

    async def test_does_nothing_when_there_are_no_bids(self):
        self.bid_repo.find_all_by_auction_id.return_value = []

        await self.handler.handle(self._event())

        self.email_service.send.assert_not_called()
        self.users_repo.get_by_id.assert_not_called()

    async def test_does_nothing_when_auction_is_not_found(self):
        self.auction_repo.get_by_id.return_value = None

        await self.handler.handle(self._event())

        self.bid_repo.find_all_by_auction_id.assert_not_called()
        self.email_service.send.assert_not_called()

    async def test_one_recipient_lookup_failing_does_not_block_the_others(self):
        winner_id, loser_id = uuid.uuid4(), uuid.uuid4()
        self.bid_repo.find_all_by_auction_id.return_value = [
            _bid(winner_id, "150.00"),
            _bid(loser_id, "100.00"),
        ]
        self.users_repo.get_by_id.side_effect = lambda uid: (
            (_ for _ in ()).throw(RuntimeError("db down"))
            if uid == str(winner_id)
            else _user("loser@test.com", "Bia")
        )

        await self.handler.handle(self._event())

        self.email_service.send.assert_called_once()
        assert self.email_service.send.call_args.kwargs["to"] == "loser@test.com"
