from app.core.tests.request_mixin import RequestMixin


class TestErrorEnvelope(RequestMixin):

    async def test_unknown_route_returns_404_in_the_standard_envelope(self, client):
        request = RequestMixin.create(client)

        response = await request.get("/does-not-exist")

        assert response.status_code == 404
        assert response.json() == {"message": "Not Found", "error_type": "NotFoundError"}

    async def test_invalid_path_param_returns_422_naming_the_param(self, client):
        request = RequestMixin.create(client)

        response = await request.get("/auctions/not-a-uuid")

        body = response.json()
        assert response.status_code == 422
        assert body["error_type"] == "ValidationError"
        assert body["errors"][0]["field"] == "auction_id"
        assert body["message"].startswith("auction_id: ")
