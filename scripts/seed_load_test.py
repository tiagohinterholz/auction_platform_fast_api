"""Bulk-seeds fake users + auctions directly into Postgres, for load-testing
the bidding flow before payments exist.

Why direct DB insert instead of the real HTTP API: creating hundreds of
thousands of users/auctions through /auth/register and /auctions would take
hours (bcrypt alone is deliberately slow) and wouldn't exercise anything we
actually care about here. The thing worth stress-testing is *bidding*
(concurrency, the Redis lock, RabbitMQ, the event handlers) — that part
still goes through the real API, in loadtest_bidding.py. This script only
builds the fixtures that script needs.

Run from the host (same localhost port pattern as pytest/the E2E scripts in
this repo — the .env hostnames like "postgres" only resolve inside Docker):

    uv run python scripts/seed_load_test.py --num-users 500 --num-auctions 2000

Writes two files into --out-dir (default scripts/loadtest_data/) for
loadtest_bidding.py to read without touching the DB again:
  - users_tokens.json    [{"user_id": "...", "token": "..."}, ...]
  - active_auctions.json [{"id": "...", "start_price": "...",
                            "minimum_increment": "..."}, ...]

Re-running against a DB that already has load-test data in it will hit the
unique constraints on users.email/users.cpf and fail loudly — pass
--truncate to wipe every table this script (and bidding) touches first.
Never does that by default: this is a destructive statement and the DB URL
you pass could, in principle, be pointed anywhere.
"""

import argparse
import asyncio
import json
import random
import sys
import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import asyncpg
import bcrypt
from faker import Faker

# Allows `from app...` when this file is run directly as a script (not
# installed as a package) — same trick the app itself doesn't need since it
# always runs via `uv run uvicorn main:app` from the repo root, but a script
# under scripts/ is one directory deeper.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security.jwt_service import JWTService

fake = Faker("pt_BR")
CHUNK_SIZE = 5000

# Every seeded user shares this exact same bcrypt hash. Nobody ever logs in
# with it for real — access tokens are minted directly below, bypassing
# /auth/login entirely — so hashing a unique password per user would just
# burn CPU (bcrypt is deliberately slow) for zero benefit. Hashing it once
# here is the difference between seconds and hours for 100k users.
SHARED_PASSWORD_HASH = bcrypt.hashpw(b"loadtest-password-not-real", bcrypt.gensalt()).decode()

# Weighted so most seeded auctions are ACTIVE (there's something to bid on
# right away) while still having some variety for realism/UI browsing.
STATUS_WEIGHTS = [
    ("active", 0.70),
    ("scheduled", 0.15),
    ("finished", 0.10),
    ("cancelled", 0.05),
]

TRUNCATE_TABLES = ["bids_history", "bidding", "auctions_read", "auctions", "users"]


def normalize_db_url(url: str) -> str:
    """asyncpg's connect() wants a plain postgresql:// URL — the app's own
    DATABASE_URL setting is in SQLAlchemy's postgresql+asyncpg:// form."""
    return url.replace("postgresql+asyncpg://", "postgresql://")


def pick_status() -> str:
    r = random.random()
    acc = 0.0
    for status, weight in STATUS_WEIGHTS:
        acc += weight
        if r <= acc:
            return status
    return STATUS_WEIGHTS[-1][0]


def _naive(dt: datetime) -> datetime:
    """auctions.start_time/end_time are TIMESTAMP WITHOUT TIME ZONE — the
    same naive-vs-aware split that bit Auction.start()/finish()/schedule()
    in the app itself. asyncpg's codec for that column type flat-out
    rejects a tz-aware datetime, so strip it here (still computed in UTC,
    just not tagged as such on the wire)."""
    return dt.replace(tzinfo=None)


def times_for_status(status: str) -> tuple[datetime | None, datetime | None]:
    now = datetime.now(UTC)
    if status == "active":
        # Already started, comfortably far from ending — plenty of runway
        # for a load test that might run for a while.
        return (
            _naive(now - timedelta(minutes=random.randint(1, 120))),
            _naive(now + timedelta(hours=random.randint(2, 48))),
        )
    if status == "scheduled":
        start = now + timedelta(minutes=random.randint(5, 600))
        return _naive(start), _naive(start + timedelta(hours=random.randint(2, 48)))
    if status == "finished":
        end = now - timedelta(hours=random.randint(1, 200))
        return _naive(end - timedelta(hours=random.randint(2, 48))), _naive(end)
    return None, None  # cancelled — never had a schedule


async def truncate_all(conn: asyncpg.Connection) -> None:
    tables = ", ".join(TRUNCATE_TABLES)
    print(f"--truncate passed: wiping {tables} ...")
    await conn.execute(f"TRUNCATE {tables} CASCADE")


async def seed_users(conn: asyncpg.Connection, num_users: int) -> list[uuid.UUID]:
    user_ids: list[uuid.UUID] = []
    rows = []
    for i in range(num_users):
        user_id = uuid.uuid4()
        user_ids.append(user_id)
        rows.append(
            (
                user_id,
                fake.name(),
                f"loadtest.user.{i}@example.test",
                str(i).zfill(11),  # CPF here is just "11 chars, non-empty" per the domain rule
                SHARED_PASSWORD_HASH,
                "USER",
                True,
            )
        )

    for start in range(0, len(rows), CHUNK_SIZE):
        chunk = rows[start : start + CHUNK_SIZE]
        await conn.executemany(
            """
            INSERT INTO users (id, name, email, cpf, password_hash, role, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            chunk,
        )
        print(f"  users: {min(start + CHUNK_SIZE, len(rows))}/{len(rows)}")

    return user_ids


async def seed_auctions(
    conn: asyncpg.Connection, num_auctions: int, seller_ids: list[uuid.UUID]
) -> list[dict]:
    active_auctions: list[dict] = []
    rows = []

    for _ in range(num_auctions):
        auction_id = uuid.uuid4()
        status = pick_status()
        start_time, end_time = times_for_status(status)
        start_price = Decimal(random.randint(5000, 500000)) / 100  # R$50,00 a R$5.000,00
        minimum_increment = (
            start_price * Decimal(random.choice([2, 5, 10])) / 100
        ).quantize(Decimal("0.01"))
        images = json.dumps([f"https://picsum.photos/seed/{auction_id}/640/480"])
        reason = "Cancelado para teste de carga" if status == "cancelled" else None

        rows.append(
            (
                auction_id,
                random.choice(seller_ids),
                fake.sentence(nb_words=6)[:100],
                fake.text(max_nb_chars=200)[:255],
                status,
                start_price,
                minimum_increment,
                start_time,
                end_time,
                reason,
                images,
            )
        )

        if status == "active":
            active_auctions.append(
                {
                    "id": str(auction_id),
                    "start_price": str(start_price),
                    "minimum_increment": str(minimum_increment),
                }
            )

    for start in range(0, len(rows), CHUNK_SIZE):
        chunk = rows[start : start + CHUNK_SIZE]
        await conn.executemany(
            """
            INSERT INTO auctions
                (id, user_id, title, description, status, start_price, minimum_increment,
                 start_time, end_time, reason, images)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            chunk,
        )
        # auctions_read mirrors auctions exactly, plus highest_bid (nothing
        # bid yet, so NULL — real bids during the load test will update it
        # via the normal BidPlacedEvent handler, same as production).
        await conn.executemany(
            """
            INSERT INTO auctions_read
                (id, user_id, title, description, status, start_price, minimum_increment,
                 start_time, end_time, reason, images, highest_bid)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NULL)
            """,
            chunk,
        )
        print(f"  auctions: {min(start + CHUNK_SIZE, len(rows))}/{len(rows)}")

    return active_auctions



# The real app expires access tokens after ACCESS_TOKEN_EXPIRE_MINUTES (15 in
# .env) - correct for a real login, but a load-test session (seed once, then
# poke at it with Locust over however long) easily outlives that. These
# tokens never represent a real login, so there's no security reason to
# inherit the short-lived setting - mint them with a generous, fixed expiry
# instead so a whole afternoon of experimentation doesn't need a re-seed.
TOKEN_LIFETIME = timedelta(hours=24)


def mint_tokens(user_ids: list[uuid.UUID]) -> list[dict]:
    """Signs real access tokens with the app's own JWTService — same secret,
    same payload shape — so they're accepted by get_current_user exactly
    like a token from a real /auth/login would be. Skips 100k logins (and
    the bcrypt.checkpw() cost that would come with each one) entirely.
    """
    jwt_service = JWTService()
    tokens = []
    for i, user_id in enumerate(user_ids):
        token = jwt_service.create_access_token(
            subject=user_id,
            expires_delta=TOKEN_LIFETIME,
            name=f"Load Test User {i}",
            email=f"loadtest.user.{i}@example.test",
            role="USER",
        )
        tokens.append({"user_id": str(user_id), "token": token})
    return tokens


async def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--database-url",
        default="postgresql://auction_user:auction_password@localhost:5434/auction_db",
        help="Plain postgresql:// URL (asyncpg) — localhost + published port, "
        "not the Docker-internal hostname.",
    )
    parser.add_argument("--num-users", type=int, default=5000)
    parser.add_argument("--num-auctions", type=int, default=4000)
    parser.add_argument(
        "--out-dir", default=str(Path(__file__).resolve().parent / "loadtest_data")
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Wipe users/auctions/bidding tables before seeding. Off by default — destructive.",
    )
    parser.add_argument(
        "--remint-tokens-only",
        action="store_true",
        help=(
            "Skip seeding entirely - just re-sign fresh access tokens for the "
            "already-seeded users and rewrite users_tokens.json. Use this "
            "instead of a full re-seed when tokens expired mid-session but "
            "the users/auctions in the DB are still fine (much faster at "
            "scale than re-inserting everything just to get a new token)."
        ),
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = await asyncpg.connect(normalize_db_url(args.database_url))
    try:
        if args.remint_tokens_only:
            print("Re-reading seeded users from the DB...")
            existing = await conn.fetch(
                "SELECT id, name, email FROM users WHERE email LIKE 'loadtest.user.%'"
            )
            if not existing:
                raise SystemExit(
                    "No load-test users found in the DB - run a normal seed first."
                )
            print(f"Minting fresh tokens for {len(existing)} existing users...")
            jwt_service = JWTService()
            tokens = [
                {
                    "user_id": str(row["id"]),
                    "token": jwt_service.create_access_token(
                        subject=row["id"],
                        expires_delta=TOKEN_LIFETIME,
                        name=row["name"],
                        email=row["email"],
                        role="USER",
                    ),
                }
                for row in existing
            ]
            (out_dir / "users_tokens.json").write_text(json.dumps(tokens))
            print(f"Done. Tokens: {out_dir / 'users_tokens.json'}")
            return

        if args.truncate:
            await truncate_all(conn)

        t0 = time.monotonic()

        print(f"Seeding {args.num_users} users...")
        user_ids = await seed_users(conn, args.num_users)

        print(f"Seeding {args.num_auctions} auctions...")
        active_auctions = await seed_auctions(conn, args.num_auctions, user_ids)

        print("Minting access tokens (no bcrypt/login involved)...")
        tokens = mint_tokens(user_ids)

        (out_dir / "users_tokens.json").write_text(json.dumps(tokens))
        (out_dir / "active_auctions.json").write_text(json.dumps(active_auctions))

        elapsed = time.monotonic() - t0
        print(f"\nDone in {elapsed:.1f}s.")
        print(
            f"  {len(user_ids)} users, {args.num_auctions} auctions "
            f"({len(active_auctions)} active)."
        )
        print(f"  Tokens:          {out_dir / 'users_tokens.json'}")
        print(f"  Active auctions: {out_dir / 'active_auctions.json'}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
