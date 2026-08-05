from app.core.tests.request_mixin import RequestMixin


class TestAuthRouters(RequestMixin):

    async def test_register_returns_201(self, client, register_payload):
        request = RequestMixin.create(client)

        response = await request.post("/auth/register", json=register_payload)

        assert response.status_code == 201
        assert "access_token" in response.json()

    async def test_register_duplicate_email_returns_400(self, client, register_payload):
        request = RequestMixin.create(client)
        await request.post("/auth/register", json=register_payload)

        response = await request.post("/auth/register", json=register_payload)

        assert response.status_code == 400

    async def test_register_duplicate_cpf_returns_409(self, client, register_payload):
        request = RequestMixin.create(client)
        await request.post("/auth/register", json=register_payload)

        duplicated_cpf_payload = {**register_payload, "email": "outro@example.com"}
        response = await request.post("/auth/register", json=duplicated_cpf_payload)

        assert response.status_code == 409
        assert response.json()["message"] == "CPF já cadastrado."
