# Bounded Contexts

A bounded context is a boundary within which terms, rules, and models have a single meaning.
Contexts communicate via **domain events** (a reaction to a fact) or a **repository interface**
(a query for current state) — never by sharing database tables or importing another context's
internal models. See `docs/architecture.md` for why this matters even though everything runs in
one process today, and `docs/domain-events.md` for the event catalog.

## Auction

- **Owns**: the auction lifecycle (create, schedule, start, extend, finish, cancel), timing
  rules, the state machine.
- **Data**: the auction aggregate/state, `start_price`, `minimum_increment`, `start_time`/
  `end_time`.
- **Publishes**: `AuctionCreatedEvent`, `AuctionScheduledEvent`, `AuctionStartedEvent`,
  `AuctionExtendedEvent`, `AuctionFinishedEvent`, `AuctionCancelledEvent`.
- **Consumes**: `BidPlacedEvent` (from Bidding — updates `highest_bid`, applies anti-sniping).

## Bidding

- **Owns**: bid acceptance and validation (auction must be `ACTIVE`, amount rule), concurrency
  (Redis lock per auction), bid history.
- **Data**: bid records (`bids_history`).
- **Publishes**: `BidPlacedEvent`.
- **Consumes**: `AuctionStartedEvent` (opens the bidding aggregate for that auction).
- **Depends directly on** (not via event — a query, not a reaction): Auction's
  `IAuctionRepository` interface, to check current auction status/pricing before accepting a bid.

## Users

- **Owns**: user profile data, CPF uniqueness, role.
- **Publishes**: `UserCreatedEvent`, `UserUpdatedEvent`, `UserDeletedEvent`.
- **Consumes**: none today.

## Auth

- **Owns**: login, registration orchestration (delegates user creation to Users), JWT issuance,
  refresh token persistence/revocation.
- Not event-driven internally — synchronous by nature (a login request needs an answer now).

## Notifications

- **Owns**: real-time fan-out to WebSocket clients. Stateless beyond the in-memory connection
  registry (`ConnectionManager`) — nothing persisted.
- **Consumes**: `BidPlacedEvent`, `AuctionStartedEvent`, `AuctionScheduledEvent`,
  `AuctionExtendedEvent`, `AuctionFinishedEvent`, `AuctionCancelledEvent`.
- **Publishes**: none.

## Payment (future scope — not implemented)

Planned: handles payment after auction completion, applies retry/idempotency, emits payment
outcome events. See `docs/architecture.md`'s roadmap notes.

## Communication rules (enforced by convention, not by tooling)

- No cross-context table sharing, no cross-context joins.
- No importing another context's domain entities.
- Prefer events for reactions; use a repository interface only for queries a context genuinely
  needs answered synchronously before it can proceed.

## Execution today

All contexts run as modules inside two processes (`api`, `worker`), not as separate services.
Internal communication uses RabbitMQ as the event transport (see `docs/architecture.md`) — the
module boundaries are already drawn as if they were service boundaries, so extracting one for
real later means replacing an interface dependency with a network call, not a rewrite.
