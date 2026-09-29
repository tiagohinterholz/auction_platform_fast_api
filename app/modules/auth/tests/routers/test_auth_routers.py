from app.core.tests.request_mixin import RequestMixin


class TestAuthRouters(RequestMixin):

    async def test_register_returns_201(self, client, register_payload):
        request = RequestMixin.create(client)

        response = await request.post("/auth/register", json=register_payload)

        assert response.status_code == 201
        assert "access_token" in response.json()

    async def test_register_rejects_password_too_short(self, client, register_payload):
        request = RequestMixin.create(client)
        payload = {**register_payload, "password": "Ab1@ab1"}  # 7 chars

        response = await request.post("/auth/register", json=payload)

        assert response.status_code == 422

    async def test_register_rejects_password_without_uppercase(self, client, register_payload):
        request = RequestMixin.create(client)
        payload = {**register_payload, "password": "lowercase123"}

        response = await request.post("/auth/register", json=payload)

        assert response.status_code == 422

    async def test_register_rejects_password_without_lowercase(self, client, register_payload):
        request = RequestMixin.create(client)
        payload = {**register_payload, "password": "UPPERCASE123"}

        response = await request.post("/auth/register", json=payload)

        assert response.status_code == 422

    async def test_register_rejects_password_without_digit(self, client, register_payload):
        request = RequestMixin.create(client)
        payload = {**register_payload, "password": "NoDigitsHere"}

        response = await request.post("/auth/register", json=payload)

        assert response.status_code == 422

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

    async def test_refresh_returns_200_with_new_tokens(self, client, register_payload):
        request = RequestMixin.create(client)
        register_response = await request.post("/auth/register", json=register_payload)
        old_tokens = register_response.json()

        response = await request.post(
            "/auth/refresh", json={"refresh_token": old_tokens["refresh_token"]}
        )

        assert response.status_code == 200
        new_tokens = response.json()
        assert new_tokens["access_token"] != old_tokens["access_token"]
        assert new_tokens["refresh_token"] != old_tokens["refresh_token"]

    async def test_refresh_rejects_an_already_used_refresh_token(self, client, register_payload):
        request = RequestMixin.create(client)
        register_response = await request.post("/auth/register", json=register_payload)
        refresh_token = register_response.json()["refresh_token"]
        await request.post("/auth/refresh", json={"refresh_token": refresh_token})

        response = await request.post("/auth/refresh", json={"refresh_token": refresh_token})

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

    async def test_unauthenticated_error_uses_the_standard_envelope(self, client):
        request = RequestMixin.create(client)

        response = await request.post("/auth/logout", json={"refresh_token": "irrelevant"})

        assert response.json() == {
            "message": "Not authenticated",
            "error_type": "UnauthorizedError",
        }
        assert response.headers["www-authenticate"] == "Bearer"

    async def test_validation_error_uses_the_standard_envelope(self, client, register_payload):
        request = RequestMixin.create(client)
        payload = {**register_payload, "password": "NoDigitsHere"}

        response = await request.post("/auth/register", json=payload)

        body = response.json()
        assert response.status_code == 422
        assert body["error_type"] == "ValidationError"
        assert body["message"] == "password: Password must contain at least one digit."
        assert body["errors"] == [
            {"field": "password", "message": "Password must contain at least one digit."}
        ]

    async def test_validation_error_lists_every_invalid_field(self, client):
        request = RequestMixin.create(client)

        response = await request.post("/auth/register", json={})

        body = response.json()
        assert response.status_code == 422
        assert isinstance(body["message"], str)
        assert {error["field"] for error in body["errors"]} == {"name", "email", "cpf", "password"}
