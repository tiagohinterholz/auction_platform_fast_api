from datetime import UTC, datetime


def as_utc(value: datetime | None) -> datetime | None:
    """Tags a naive datetime as UTC before it leaves the API as JSON.

    Every datetime stored in this database is naive (TIMESTAMP WITHOUT TIME
    ZONE) but is implicitly UTC everywhere it's computed/compared internally
    (see Auction._as_aware()). Serializing it naive drops the "Z"/UTC offset
    from the JSON string, and clients - browsers especially - parse an
    offset-less ISO datetime as LOCAL time, shifting it by the client's own
    timezone instead of leaving it as the UTC instant it actually is.
    """
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
