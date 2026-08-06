from app.core.tests.request_mixin import RequestMixin


class TestAuthRouters(RequestMixin):

    async def test_register_returns_201(self, client, register_payload):
        request = RequestMixin.create(client)

        response = await request.post("/auth/register", json=register_payload)

        assert response.status_code == 201
        assert "access_token" in response.json()

    async def test_register_duplicate_email_returns_401(self, client, register_payload):
        request = RequestMixin.create(client)
        await request.post("/auth/register", json=register_payload)

        response = await request.post("/auth/register", json=register_payload)

        assert response.status_code == 401

    async def test_register_duplicate_cpf_returns_409(self, client, register_payload):
        request = RequestMixin.create(client)
        await request.post("/auth/register", json=register_payload)

        duplicated_cpf_payload = {**register_payload, "email": "outro@example.com"}
        response = await request.post("/auth/register", json=duplicated_cpf_payload)

        assert response.status_code == 409
        assert response.json()["message"] == "CPF já cadastrado."

    async def test_login_returns_200(self, client, register_payload, login_payload):
        request = RequestMixin.create(client)
        await request.post("/auth/register", json=register_payload)

        response = await request.post("/auth/login", json=login_payload)

        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_invalid_credentials_returns_401(self, client, login_payload):
        request = RequestMixin.create(client)

        response = await request.post("/auth/login", json=login_payload)

        assert response.status_code == 401

    async def test_logout_returns_204_and_revokes_the_refresh_token(self, client, register_payload):
        request = RequestMixin.create(client)
        register_response = await request.post("/auth/register", json=register_payload)
        tokens = register_response.json()
        authenticated = RequestMixin.create(client, token=tokens["access_token"])

        logout_response = await authenticated.post(
            "/auth/logout", json={"refresh_token": tokens["refresh_token"]}
        )
        assert logout_response.status_code == 204

        refresh_response = await request.post(
            "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == 401

    async def test_logout_returns_401_when_unauthenticated(self, client):
        request = RequestMixin.create(client)

        response = await request.post("/auth/logout", json={"refresh_token": "irrelevant"})

        assert response.status_code == 401
