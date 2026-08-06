from app.core.tests.request_mixin import RequestMixin


class TestUserRouters(RequestMixin):

    async def test_get_all_users_returns_200_for_admin(self, client, user_obj_admin):
        request_auth = await self.authenticated(client, user_obj_admin.email, "Pass@123")
        response = await request_auth.get("/users")
        assert response.status_code == 200

    async def test_get_all_users_returns_403_for_regular_user(self, client, user_obj):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.get("/users")
        assert response.status_code == 403

    async def test_get_user_by_id_returns_200(self, client, user_obj):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.get(f"/users/{user_obj.id}")
        assert response.status_code == 200

    async def test_get_user_by_id_returns_401_when_unauthenticated(self, client, user_obj):
        request = self.create(client)
        response = await request.get(f"/users/{user_obj.id}")
        assert response.status_code == 401

    async def test_get_user_by_id_returns_403_for_other_user(self, client, user_obj, user_factory):
        other_user = await user_factory()
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")

        response = await request_auth.get(f"/users/{other_user.id}")

        assert response.status_code == 403

    async def test_get_user_by_id_returns_200_for_admin_viewing_other_user(
        self, client, user_obj, user_obj_admin
    ):
        request_auth = await self.authenticated(client, user_obj_admin.email, "Pass@123")

        response = await request_auth.get(f"/users/{user_obj.id}")

        assert response.status_code == 200

    async def test_update_user_returns_202(self, client, user_obj, update_user_payload):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.patch(f"/users/{user_obj.id}", json=update_user_payload)
        assert response.status_code == 202

    async def test_update_user_returns_403_for_other_user(
        self, client, user_obj, user_factory, update_user_payload
    ):
        other_user = await user_factory()
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")

        response = await request_auth.patch(f"/users/{other_user.id}", json=update_user_payload)

        assert response.status_code == 403

    async def test_delete_user_returns_204_for_admin(self, client, user_obj, user_obj_admin):
        request_auth = await self.authenticated(client, user_obj_admin.email, "Pass@123")
        response = await request_auth.delete(f"/users/{user_obj.id}")
        assert response.status_code == 204

    async def test_delete_user_returns_403_for_regular_user(self, client, user_obj):
        request_auth = await self.authenticated(client, user_obj.email, "Pass@123")
        response = await request_auth.delete(f"/users/{user_obj.id}")
        assert response.status_code == 403
