from app.core.tests.request_mixin import RequestMixin


class TestAuctionRouters(RequestMixin):
    
    async def test_create_auction_returns_201(self, client, user_obj, create_auction_payload):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.post(
            "/auctions", 
            json=create_auction_payload
        )
        assert response.status_code == 201

    async def test_list_auctions_returns_200(self, client):
        request_auth = RequestMixin.create(client)
        response = await request_auth.get("/auctions")
        assert response.status_code == 200

    async def test_schedule_auction_returns_202(
        self, client, user_obj, auction_obj_created, schedule_auction_payload
    ):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.patch(
            f"/auctions/{auction_obj_created.id}/schedule", 
            json=schedule_auction_payload
        )
        assert response.status_code == 202
        
    async def test_cancel_auction_returns_202(
        self, client, user_obj, auction_obj_scheduled, cancel_auction_payload
    ):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.patch(
            f"/auctions/{auction_obj_scheduled.id}/cancel", 
            json=cancel_auction_payload
        )
        assert response.status_code == 202
    
    async def test_get_auction_by_id_returns_200(self, client, auction_obj_created):
        request = RequestMixin.create(client)
        response = await request.get(f"/auctions/{auction_obj_created.id}")
        assert response.status_code == 200
    
    async def test_create_auction_returns_401_when_unauthenticated(self, client, create_auction_payload):
        request = RequestMixin.create(client)
        response = await request.post("/auctions", json=create_auction_payload)
        assert response.status_code == 401