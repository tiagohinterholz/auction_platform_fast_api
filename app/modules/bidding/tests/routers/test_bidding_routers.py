from app.core.tests.request_mixin import RequestMixin


class TestBiddingRouters(RequestMixin):
   
    async def test_create_bid_returns_201(self, client, auction_obj_active, user_obj):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.post(
            f"/auctions/{auction_obj_active.id}/bids", 
            json={"amount": 150.0})
        assert response.status_code == 201

    async def test_list_bids_returns_200(self, client, auction_obj_active):
        request_auth = RequestMixin.create(client)
        response = await request_auth.get(
            f"/auctions/{auction_obj_active.id}/bids"
        )
        assert response.status_code == 200