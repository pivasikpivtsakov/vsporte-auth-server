from sqlalchemy import select, insert, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from database.models import UserModel, RoleInService, RolesEnum


class UserQueries:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str):
        user = await self.db.scalar(
            select(UserModel)
            .where(UserModel.username == username)
        )
        return user

    async def get_user_by_username_if_has_role(self, username: str, service: str):
        user = await self.db.scalar(
            select(UserModel)
            .join(UserModel.roles_in_services)
            # guaranteed that there is only 1 user-to-service combination
            .where((UserModel.username == username) & (RoleInService.service == service))
            .options(contains_eager(UserModel.roles_in_services))
        )
        return user

    async def get_user_by_email_if_has_role(self, email: str, service: str):
        user = await self.db.scalar(
            select(UserModel)
            .join(UserModel.roles_in_services)
            # guaranteed that there is only 1 user-to-service combination
            .where((UserModel.email == email) & (RoleInService.service == service))
            .options(contains_eager(UserModel.roles_in_services))
        )
        return user

    async def count_users(self, service):
        c = await self.db.scalar(
            select(func.count())
            .select_from(UserModel)
            .join(UserModel.roles_in_services)
            # for each service, user has only 1 role
            .where(RoleInService.service == service)
        )
        return c

    async def list_users(self, limit: int, offset: int, service: str):
        user_list = await self.db.scalars(
            select(UserModel)
            .join(UserModel.roles_in_services)
            # for each service, user has only 1 role
            .where(RoleInService.service == service)
            .options(contains_eager(UserModel.roles_in_services))
            .limit(limit)
            .offset(offset)
        )
        unique_user_list = user_list.unique()
        return unique_user_list

    async def create_user(self, username: str, password_hash: str, service: str):
        self.db.add(
            UserModel(
                username=username,
                password_hash=password_hash,
                roles_in_services=[RoleInService(role=RolesEnum.client, service=service)]
            )
        )
        await self.db.commit()

    async def delete_user(self, username: str):
        deletion_result = await self.db.execute(
            delete(UserModel)
            .where(UserModel.username == username)
        )
        await self.db.commit()
        return deletion_result
