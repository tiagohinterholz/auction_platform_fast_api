from app.modules.auth.domain.ports.refresh_token_repository_interface import IRefreshTokenRepository


class LogoutUseCase:
    def __init__(self, refresh_token_repository: IRefreshTokenRepository):
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, jti: str) -> None:
        await self.refresh_token_repository.revoke(jti)
