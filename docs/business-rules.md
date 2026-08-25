# Auction Business Rules

## Purpose

An **Auction** represents a competitive process where multiple participants place bids on an
item within a defined time window. The system must guarantee **fairness**, **consistency**, and
**correctness**, even under high concurrency.

## Core concepts

**Auction** — defined by a starting price, a minimum bid increment, a start/end time, a current
highest bid (if any), and a lifecycle state. Exists independently of bids; bids don't define an
auction, they only interact with it.

**Bid** — an offer to buy the auctioned item for a given amount. Belongs to exactly one auction,
is immutable once accepted, evaluated against the current auction state.

**Participant** — a user eligible to place bids. Identity/auth rules are out of scope here.

## Lifecycle states

`CREATED` → `SCHEDULED` → `ACTIVE` → `FINISHED`, with `CANCELLED` reachable from `CREATED` or
`SCHEDULED`. See `docs/state-diagram.md` for the full transition table.

## Bid rules

- A bid can only be placed while the auction is `ACTIVE`; otherwise rejected.
- A bid is valid only if it's strictly greater than the starting price (no previous bids) or the
  current highest bid **plus** the minimum increment (bids exist).
- **Concurrency (critical)**: under concurrent bids, only one may become the highest — enforced
  by a Redis distributed lock per auction, not by application-level checks alone.

## Anti-sniping (time extension)

If a valid bid lands within the final **30 seconds**, the auction end time extends by **60
seconds**. Applies only to valid bids.

## Completion

An auction becomes `FINISHED` automatically once the current time exceeds its end time (driven
by a Celery task scheduled when the auction was scheduled). No further bids accepted afterward.
An auction with no bids still finishes normally — no winner is assigned.

## Cancellation

Only allowed from `CREATED` or `SCHEDULED`. Existing bids (if any, from a scheduled-but-not-yet-
active auction) remain stored for audit purposes.

## Invariants (must always hold)

- An auction has at most one highest bid, and it always satisfies the minimum increment rule.
- A bid belongs to exactly one auction.
- `FINISHED`/`CANCELLED` auctions never accept bids.
- Time-based rules are enforced consistently.

Violating any of these is a system bug, not an edge case to special-case around.

## Out of scope (this document)

Payment processing, authn/authz, notification delivery mechanics, fraud detection — each has (or
will have) its own doc/module.
