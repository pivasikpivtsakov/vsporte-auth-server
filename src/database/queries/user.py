from sqlalchemy import select, insert, delete, func
# task requires to use postgesql only, so we can import specific functions
from sqlalchemy.dialects.postgresql import insert as pinsert
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

    async def seed_db(self):
        await self.db.execute(
            pinsert(UserModel)
            .values({
                "username": "vip",
                "email": "user@mail.rb",
                "password_hash": "$2b$12$djOFvxo9gSgM0hBFEaS89.SgwkdNPQFJhjiXZghEWTt91wbrfSo0O"
            })
            .on_conflict_do_nothing(

            )
            .returning(UserModel.id)
        )
        uid = await self.db.scalar(select(UserModel.id).where(UserModel.username == "vip"))
        await self.db.execute(
            pinsert(RoleInService)
            .values({"user_id": uid, "role": "admin", "service": "someservice"})
            .on_conflict_do_nothing(
                constraint="roles_in_services_user_id_service_key",
            )
        )
        await self.db.commit()
