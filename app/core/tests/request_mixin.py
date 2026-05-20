from httpx import AsyncClient, Response


class RequestMixin:
    base_url = "/api/v1"
    client: AsyncClient
    token: str | None = None

    def _headers(self) -> dict:
        token = getattr(self, "token", None)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    async def get(self, path: str, **kwargs) -> Response:
        return await self.client.get(f"{self.base_url}{path}", headers=self._headers(), **kwargs)

    async def post(self, path: str, json: dict | None = None, **kwargs) -> Response:
        return await self.client.post(f"{self.base_url}{path}", json=json, headers=self._headers(), **kwargs)

    async def patch(self, path: str, json: dict | None = None, **kwargs) -> Response:
        return await self.client.patch(f"{self.base_url}{path}", json=json, headers=self._headers(), **kwargs)

    async def delete(self, path: str, **kwargs) -> Response:
        return await self.client.delete(f"{self.base_url}{path}", headers=self._headers(), **kwargs)

    @classmethod
    def create(cls, client: AsyncClient, token: str | None = None) -> "RequestMixin":
        instance = object.__new__(RequestMixin)
        instance.client = client
        instance.token = token
        return instance

    @classmethod
    async def authenticated(cls, client: AsyncClient, email: str, password: str) -> "RequestMixin":
        response = await client.post(
            f"{cls.base_url}/auth/login",
            json={"email": email, "password": password},
        )
        token = response.json()["access_token"]
        return cls.create(client, token)
