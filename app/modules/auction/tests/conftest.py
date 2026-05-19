from app.modules.users.tests.fixtures.factories import user_factory
from app.modules.users.tests.fixtures.users import user_obj, user_obj_admin
from app.modules.auction.tests.fixtures.factories import auction_factory
from app.modules.auction.tests.fixtures.payloads import (
    create_auction_payload,
    schedule_auction_payload,
    cancel_auction_payload,
)
from app.modules.auction.tests.fixtures.auctions import (
    auction_obj_created,
    auction_obj_scheduled,
    auction_obj_active,
    auction_obj_finished,
    auction_obj_cancelled,
)
