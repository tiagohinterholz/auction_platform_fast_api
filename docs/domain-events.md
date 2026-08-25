# Domain Events

Domain events represent **facts that already happened** — always past tense, immutable once
published, never enforce behavior (consumers decide how to react). See `docs/architecture.md`
for how they're transported (RabbitMQ, swappable for in-memory).

Naming: past tense, no return value expected, published only after the state change that caused
them has already been persisted.

---

## Auction events (`app/modules/auction/domain/events/auction_events.py`)

| Event | Triggered by | Payload |
|---|---|---|
| `AuctionCreatedEvent` | `POST /auctions` | `id, user_id, title, description, start_price, minimum_increment, status, images` |
| `AuctionScheduledEvent` | `PATCH .../schedule` | `id, start_time, end_time, starting_price, minimum_increment` |
| `AuctionStartedEvent` | Celery `start_auction` task | `id, start_time, end_time, starting_price, minimum_increment, status` |
| `AuctionExtendedEvent` | Anti-sniping rule, triggered by a bid landing near the deadline | `id, end_time` |
| `AuctionFinishedEvent` | Celery `finish_auction` task | `id, title, end_time` |
| `AuctionCancelledEvent` | `PATCH .../cancel` | `id, cancelled_at, reason` |

## Bidding events (`app/modules/bidding/domain/events/bid_events.py`)

| Event | Triggered by | Payload |
|---|---|---|
| `BidPlacedEvent` | `POST .../bids` | `auction_id, user_id, amount` |

## User events (`app/modules/users/domain/events/users_events.py`)

| Event | Triggered by | Payload | Consumed today? |
|---|---|---|---|
| `UserCreatedEvent` | Registration | `id, name, email, cpf` | Yes — welcome e-mail |
| `UserUpdatedEvent` | Profile update | `id, name, email` | Not yet (published, no subscriber) |
| `UserDeletedEvent` | Account deletion | `id` | Not yet (published, no subscriber) |

Publishing `UserUpdatedEvent`/`UserDeletedEvent` without a subscriber today is deliberate: it's a
real fact worth broadcasting, cheap to keep emitting, and free to react to later (e.g. session
revocation) without touching the aggregate or use case again.

## Payment events (future scope — not implemented)

`PaymentRequestedEvent`, `PaymentCompletedEvent`, `PaymentFailedEvent` — planned once the payment
gateway integration lands (see `docs/architecture.md`).

## Guarantees

- Published only **after** the state change is persisted (never before — see the `pull_events()`
  pattern in each aggregate).
- At-least-once delivery; **consumers must be idempotent**.
- Order is guaranteed only within a single queue/consumer, never globally across event types.

## Out of scope (this document)

Transport technology, retry policy, dead-letter queues — see `docs/architecture.md` and (if it
exists) the maintainer's RabbitMQ migration notes for the current state of those.
