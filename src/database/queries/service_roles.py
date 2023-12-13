# task requires to use postgesql only, so we can import specific functions
from sqlalchemy.dialects.postgresql import insert as pinsert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RoleInService, RolesEnum


class ServiceRolesQueries:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def change_user_access(self, user_id: int, role: RolesEnum, service: str):
        access_update_result = await self.db.execute(
            pinsert(RoleInService)
            .values({"user_id": user_id, "role": role, "service": service})
            .on_conflict_do_update(
                constraint="roles_in_services_user_id_service_key",
                set_={"role": role}
            )
        )
        await self.db.commit()
        return access_update_result
