from app.modules.auth.domain.ports.jwt_service_interface import IJWTService
from app.modules.auth.domain.ports.refresh_token_repository_interface import IRefreshTokenRepository


class LogoutUseCase:
    def __init__(self, refresh_token_repository: IRefreshTokenRepository, jwt_service: IJWTService):
        self.refresh_token_repository = refresh_token_repository
        self.jwt_service = jwt_service

    async def execute(self, refresh_token: str) -> None:
        payload = self.jwt_service.decode_refresh_token(refresh_token)
        await self.refresh_token_repository.revoke(payload["jti"])
