from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import RolesEnum, UserModel
from logic.jwt_functions import get_user_by_jwt


def check_role(role: RolesEnum):
    async def check_specific_role(user: UserModel = Depends(get_user_by_jwt_dep)):
        role_in_service_result = user.roles_in_services
        role_in_service = role_in_service_result[0]
        if role_in_service.role == role:
            return role_in_service
        else:
            raise HTTPException(
                status_code=403,
                detail="User is not allowed to access this service, admin must add role first"
            )

    return check_specific_role


bearer_scheme = HTTPBearer()


async def get_user_by_jwt_dep(
        creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db)
):
    jwt = creds.credentials
    user = await get_user_by_jwt(jwt, db)
    return user
