from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.users.domain.users_aggregate import User
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.infrastructure.persistence.users_model import UserModel


class UserRepository(IUsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        user = User.__new__(User)
        user._id = model.id
        user._name = model.name
        user._email = model.email
        user._cpf = model.cpf
        user._password_hash = model.password_hash
        user._role = model.role
        user.events = []
        return user

    async def get_by_cpf(self, cpf: str) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.cpf == cpf)
        )
        user_model = result.scalars().first()
        if not user_model:
            return None
        return self._to_domain(user_model)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalars().first()
        if not user_model:
            return None
        return self._to_domain(user_model)

    async def create(self, user: User) -> None:
        user_model = UserModel(
            id=user.id,
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            password_hash=user.password_hash,
            role=user.role,
        )
        self.session.add(user_model)
        await self.session.commit()

    async def get_by_id(self, id: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.id == id))
        user_model = result.scalars().first()
        if not user_model:
            return None
        return self._to_domain(user_model)

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(UserModel))
        user_models = result.scalars().all()
        return [self._to_domain(model) for model in user_models]

    async def delete(self, user: User) -> None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        user_model = result.scalars().first()
        if not user_model:
            return
        await self.session.delete(user_model)
        await self.session.commit()

    async def update(self, user: User) -> None:
        user_model = await self.session.get(UserModel, user.id)
        if not user_model:
            return
        user_model.name = user.name
        user_model.email = user.email
        await self.session.commit()
