"""Load-tests the real bidding flow through the HTTP API, using the users
and auctions that scripts/seed_load_test.py already put in the database.

This is the part that's actually meant to stress the system — every request
here goes through the real FastAPI app, PlaceBidUseCase's Redis lock,
RabbitMQEventBus, the works. The seed script only builds fixtures; this file
is where the concurrency actually happens.

Run (after seed_load_test.py has produced scripts/loadtest_data/*.json, and
`docker compose up` is serving the API on :8000):

    uv run locust -f scripts/loadtest_bidding.py --host=http://localhost:8000

Then open http://localhost:8089 — that's Locust's own live dashboard: pick
how many simulated users and how fast to ramp them up, and watch RPS,
latency and failure rate update in real time while it runs. Ctrl+C in the
terminal (or the Stop button on the page) ends the run and shows a summary.

By default, every virtual user bids on one of a small pool of "hot"
auctions (HOT_AUCTIONS_COUNT below) instead of sampling uniformly across
every active auction. That's deliberate: real auction contention is
"sniping" — a burst of bidders racing on ONE item in its last seconds — not
traffic spread evenly across the whole catalog. Spreading 5000 virtual
users across 1000+ auctions barely ever puts two of them on the same
auction at the same instant, so PlaceBidUseCase's Redis lock never actually
gets contested — you'd be measuring general site traffic, not the thing
that lock exists to protect. Set LOADTEST_HOT_AUCTIONS=0 (env var) to go
back to sampling across every active auction instead.
"""

import json
import os
import random
from decimal import Decimal
from pathlib import Path

from locust import HttpUser, between, task

DATA_DIR = Path(__file__).resolve().parent / "loadtest_data"
HOT_AUCTIONS_COUNT = int(os.environ.get("LOADTEST_HOT_AUCTIONS", "8"))

try:
    USERS = json.loads((DATA_DIR / "users_tokens.json").read_text())
    ACTIVE_AUCTIONS = json.loads((DATA_DIR / "active_auctions.json").read_text())
except FileNotFoundError as exc:
    raise RuntimeError(
        "No seeded data found in scripts/loadtest_data/ — run "
        "`uv run python scripts/seed_load_test.py` first."
    ) from exc

if not USERS or not ACTIVE_AUCTIONS:
    raise RuntimeError("Seed data files are empty — re-run scripts/seed_load_test.py.")

# The pool every virtual user picks from. LOADTEST_HOT_AUCTIONS=0 opts back
# into the old "spread across everything" behavior.
TARGET_AUCTIONS = (
    ACTIVE_AUCTIONS[:HOT_AUCTIONS_COUNT] if HOT_AUCTIONS_COUNT > 0 else ACTIVE_AUCTIONS
)
print(
    f"[loadtest_bidding] targeting {len(TARGET_AUCTIONS)} auction(s) "
    f"out of {len(ACTIVE_AUCTIONS)} active "
    f"(LOADTEST_HOT_AUCTIONS={HOT_AUCTIONS_COUNT})"
)


class BidderUser(HttpUser):
    """Each simulated user behaves like a real bidder: reads an auction's
    current price, then tries to outbid it. Locust running hundreds of these
    concurrently is what actually exercises PlaceBidUseCase's Redis lock and
    the RabbitMQ event flow — the seed data by itself doesn't test anything.
    """

    wait_time = between(0.5, 2.0)

    def on_start(self):
        entry = random.choice(USERS)
        self.headers = {"Authorization": f"Bearer {entry['token']}"}

    @task
    def place_bid(self):
        auction = random.choice(TARGET_AUCTIONS)
        auction_id = auction["id"]

        # `name=` groups every /auctions/<uuid> call into one Locust stat
        # row instead of one row per distinct auction ID.
        with self.client.get(
            f"/api/v1/auctions/{auction_id}",
            headers=self.headers,
            name="/api/v1/auctions/[id]",
            catch_response=True,
        ) as get_resp:
            if get_resp.status_code != 200:
                get_resp.failure(f"could not read auction: {get_resp.status_code}")
                return
            current = get_resp.json()
            get_resp.success()

        highest = current.get("highest_bid")
        base = Decimal(str(highest)) if highest is not None else Decimal(auction["start_price"])
        increment = Decimal(auction["minimum_increment"])
        # A bit more than the bare minimum, randomized, so competing virtual
        # users don't all submit the exact same amount on the same auction.
        amount = base + increment + Decimal(random.randint(0, 500)) / 100

        with self.client.post(
            f"/api/v1/auctions/{auction_id}/bids",
            json={"amount": str(amount)},
            headers=self.headers,
            name="/api/v1/auctions/[id]/bids",
            catch_response=True,
        ) as post_resp:
            if post_resp.status_code == 201:
                post_resp.success()
            elif post_resp.status_code in (400, 409):
                # Expected under real contention, not a bug:
                # 409 = another bidder held PlaceBidUseCase's Redis lock at
                #       that exact instant (non-blocking, no retry by design).
                # 400 = the price moved between our GET and this POST, so
                #       our computed amount is no longer high enough.
                # Counting these as failures would make healthy contention
                # look like a broken system.
                post_resp.success()
            else:
                post_resp.failure(f"unexpected status: {post_resp.status_code} {post_resp.text}")
