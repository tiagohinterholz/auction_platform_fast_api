# Auction State Diagram

## States

- **CREATED** — created, not yet scheduled.
- **SCHEDULED** — has start/end times; Celery tasks enqueued for automatic start and finish.
- **ACTIVE** — open, accepts bids.
- **FINISHED** — ended, no longer accepts bids.
- **CANCELLED** — terminated before completion.

## Allowed transitions

| From | To | Trigger |
|---|---|---|
| CREATED | SCHEDULED | Owner schedules with start/end times |
| SCHEDULED | ACTIVE | `start_time` reached (Celery) |
| ACTIVE | FINISHED | `end_time` reached (Celery) |
| CREATED | CANCELLED | Cancelled by owner |
| SCHEDULED | CANCELLED | Cancelled by owner |

## Forbidden transitions

`ACTIVE → CANCELLED`, `FINISHED → ACTIVE`, `CANCELLED → ACTIVE`, `FINISHED → CANCELLED`,
`CANCELLED → FINISHED`. `FINISHED`/`CANCELLED` are terminal.

## Rules

- Transitions are atomic; time-based transitions are deterministic (see `Auction.start()`/
  `finish()`/`schedule()` — they normalize naive/aware datetimes before comparing, so a
  transition never depends on which timezone a client or the DB happened to use).
- Invalid transitions are rejected (`InvalidAuctionStatusException` and friends).
- No manual override exists for terminal states.
- Bids are accepted only while `ACTIVE`.
