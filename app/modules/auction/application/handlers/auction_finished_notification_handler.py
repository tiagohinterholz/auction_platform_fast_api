import logging
from decimal import Decimal

from app.core.email.email_service_interface import IEmailService
from app.modules.auction.domain.events.auction_events import AuctionFinishedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.users.infrastructure.repository.users_repository import UserRepository

logger = logging.getLogger(__name__)


class AuctionFinishedNotificationHandler:
    """Notifies the winner (highest bid) and every other bidder (losers) by
    e-mail when an auction finishes. No bids at all: nothing to send.
    """

    def __init__(
        self,
        auction_read_repository: AuctionReadRepository,
        bid_read_repository: BidReadRepository,
        users_repository: UserRepository,
        email_service: IEmailService,
    ):
        self.auction_read_repository = auction_read_repository
        self.bid_read_repository = bid_read_repository
        self.users_repository = users_repository
        self.email_service = email_service

    async def handle(self, event: AuctionFinishedEvent) -> None:
        auction_id = str(event.payload["id"])

        auction = await self.auction_read_repository.get_by_id(auction_id)
        if not auction:
            return

        bids = await self.bid_read_repository.find_all_by_auction_id(auction_id)
        if not bids:
            return

        best_per_user: dict[str, Decimal] = {}
        for bid in bids:
            user_id = str(bid.user_id)
            if user_id not in best_per_user or bid.amount > best_per_user[user_id]:
                best_per_user[user_id] = bid.amount

        winner_id = max(best_per_user, key=lambda uid: best_per_user[uid])
        winner_amount = best_per_user[winner_id]
        loser_ids = [uid for uid in best_per_user if uid != winner_id]

        await self._notify_winner(auction.title, winner_id, winner_amount)
        for loser_id in loser_ids:
            await self._notify_loser(auction.title, loser_id, winner_amount)

    async def _notify_winner(self, auction_title: str, winner_id: str, amount: Decimal) -> None:
        try:
            winner = await self.users_repository.get_by_id(winner_id)
            if not winner:
                return
            await self.email_service.send(
                to=winner.email,
                subject=f'Você venceu o leilão "{auction_title}"!',
                body=(
                    f"Parabéns, {winner.name}! Seu lance de R$ {amount} venceu o "
                    f'leilão "{auction_title}".'
                ),
            )
        except Exception:
            logger.exception(f"Failed to notify auction winner user_id={winner_id}")

    async def _notify_loser(
        self, auction_title: str, loser_id: str, winner_amount: Decimal
    ) -> None:
        try:
            loser = await self.users_repository.get_by_id(loser_id)
            if not loser:
                return
            await self.email_service.send(
                to=loser.email,
                subject=f'O leilão "{auction_title}" terminou',
                body=(
                    f"Olá {loser.name}, o leilão \"{auction_title}\" foi encerrado. "
                    f"O lance vencedor foi R$ {winner_amount}. Você não venceu desta vez."
                ),
            )
        except Exception:
            logger.exception(f"Failed to notify auction loser user_id={loser_id}")
