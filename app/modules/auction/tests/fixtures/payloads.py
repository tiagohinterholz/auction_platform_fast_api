from datetime import datetime, timedelta

import pytest


@pytest.fixture
def create_auction_payload(user_obj):
    return {
        "title": "Leilão de teste",
        "description": "Descrição do leilão de teste",
        "user_id": str(user_obj.id),
        "start_price": 100.0,
        "minimum_increment": 10.0,
    }


@pytest.fixture
def schedule_auction_payload():
    now = datetime.now()
    return {
        "start_date": (now + timedelta(hours=1)).isoformat(),
        "end_date": (now + timedelta(hours=3)).isoformat(),
    }


@pytest.fixture
def cancel_auction_payload():
    return {
        "reason": "Leilão cancelado para fins de teste.",
    }
