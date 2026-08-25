# API Contracts

> This document describes the shape of the public API in prose. The generated OpenAPI schema
> (`/docs`, `/redoc` on a running instance) is the authoritative source for exact field
> constraints — this is a narrative companion, not a generated spec.

Base URL: `/api/v1`

General rules:
- JSON-based, ISO 8601 timestamps.
- **Monetary values (`start_price`, `minimum_increment`, `highest_bid`, `amount`) are `Decimal`,
  serialized as JSON strings** (e.g. `"100.00"`, not `100.0`) — deliberate, to avoid float
  precision loss on money.
- Authentication via JWT bearer token (`Authorization: Bearer <token>`), obtained from
  `/api/v1/auth/login` or `/api/v1/auth/register`.
- `user_id`/`status` are never accepted from the client on writes — always derived from the
  authenticated token or computed server-side.

---

## Auction

### Create — `POST /auctions`
```json
// request
{
  "title": "Vintage Watch",
  "description": "A rare vintage watch from the 1960s.",
  "start_price": "100.00",
  "minimum_increment": "10.00",
  "images": []
}
```
```json
// response (201)
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Vintage Watch",
  "description": "A rare vintage watch from the 1960s.",
  "status": "created",
  "start_price": "100.00",
  "minimum_increment": "10.00",
  "highest_bid": null,
  "start_time": null,
  "end_time": null,
  "images": []
}
```

### Schedule — `PATCH /auctions/{auction_id}/schedule`
```json
{ "start_date": "2026-01-20T18:00:00Z", "end_date": "2026-01-20T19:00:00Z" }
```
Accepts a value with or without a timezone offset; naive values are treated as UTC.

### List — `GET /auctions`, `GET /auctions/me`, `GET /auctions/{auction_id}`

### Cancel — `PATCH /auctions/{auction_id}/cancel`
```json
{ "reason": "Item no longer available." }
```

---

## Bidding

### Place a bid — `POST /auctions/{auction_id}/bids`
```json
{ "amount": "130.00" }
```
```json
// response (201)
{ "id": "uuid", "auction_id": "uuid", "user_id": "uuid", "amount": "130.00", "timestamp": "..." }
```

### List bids — `GET /auctions/{auction_id}/bids`

---

## WebSocket (real-time notifications)

**Endpoint**: `WS /api/v1/ws/auctions/{auction_id}` — one connection per auction, no
subscribe/unsubscribe message needed; the room is the URL itself.

Every message has the shape:
```json
{ "event": "<eventName>", "payload": { ... } }
```

Events pushed (camelCase, matches the underlying domain event's payload):
`bidPlaced`, `auctionStarted`, `auctionScheduled`, `auctionExtended`, `auctionFinished`,
`auctionCancelled`.

---

## Error responses

Two shapes exist depending on where the error originates:
- Domain/business errors (`DomainException` subclasses, unique-constraint violations):
  `{"message": "...", "error_type": "..."}`.
- Framework-level errors (auth failures, request validation): FastAPI's default
  `{"detail": "..."}` (or a list of validation errors for 422s).

---

## Out of scope (current state)

- Payment API (see `docs/architecture.md` roadmap).
- Admin dashboards, fraud detection, analytics endpoints.
