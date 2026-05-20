import pytest


@pytest.fixture
def create_bid_payload():
    return {
        "amount": 150.0,
    }
