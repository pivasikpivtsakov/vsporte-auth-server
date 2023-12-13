import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import UserModel, RoleInService, RolesEnum
from database.queries import UserQueries, ServiceRolesQueries
from logic import get_jwt_for_user, are_passwords_equal, get_user_by_jwt_dep, check_role, hash_password

logging.basicConfig(level=logging.INFO)
# reconfigure actually exists on sys.stderr object
# noinspection PyUnresolvedReferences
sys.stderr.reconfigure(encoding="utf-8")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app):
    # seed the db
    async for db in get_db():
        user_queries = UserQueries(db)
        await user_queries.seed_db()
    yield


app = FastAPI(lifespan=lifespan)

# user


class GetJwtByUsernameRequest(BaseModel):
    username: str
    password: str
    service: str


class GetJwtByEmailRequest(BaseModel):
    email: str
    password: str
    service: str


@app.post("/jwt")
async def auth_jwt(
        body: GetJwtByUsernameRequest | GetJwtByEmailRequest,
        db: AsyncSession = Depends(get_db)
):
    """
    Get user jwt if user is at least a client of the service. Otherwise, deny request.
    """

    user_queries = UserQueries(db)
    if isinstance(body, GetJwtByUsernameRequest):
        user = await user_queries.get_user_by_username_if_has_role(body.username, body.service)
    else:
        user = await user_queries.get_user_by_email_if_has_role(body.email, body.service)

    if user:
        username = user.username
    else:
        raise HTTPException(status_code=404, detail="Unable to find user by username")

    if not are_passwords_equal(body.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # token is issued for user + service!
    jwt = get_jwt_for_user(username, body.service)
    return {"jwt": jwt}


# admin
class UserListResponseElement(BaseModel):
    username: str
    email: str | None
    role: str


class UserListResponse(BaseModel):
    users: list[UserListResponseElement]
    is_final_page: bool


@app.get("/users")
async def get_users_by_service(
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=0),
        db: AsyncSession = Depends(get_db),
        role: RoleInService = Depends(check_role(RolesEnum.admin))
):
    """
    Get users with pagination
    :param page_size: how many items in page starting with 0
    :param db:
    :param role:
    :param page: page number starting with 1
    """

    user_queries = UserQueries(db)

    limit = page_size
    offset = (page - 1) * page_size
    count_all_users = await user_queries.count_users(role.service)
    is_final_page = offset + limit >= count_all_users

    target_service_users = await user_queries.list_users(limit, offset, role.service)
    target_service_users_list = UserListResponse(
        users=[
            UserListResponseElement(username=u.username, email=u.email, role=u.roles_in_services[0].role)
            for u in target_service_users
        ],
        is_final_page=is_final_page,
    )

    return target_service_users_list


class CreateUserRequest(BaseModel):
    username: str
    password: str


@app.post("/users")
async def create_user(
        body: CreateUserRequest,
        db: AsyncSession = Depends(get_db),
        role: RoleInService = Depends(check_role(RolesEnum.admin))
):
    """
    Create user in this service by username and password
    """

    user_queries = UserQueries(db)
    hashed_pwd = hash_password(body.password)
    await user_queries.create_user(body.username, hashed_pwd, role.service)

    return {"created": True}


class AddAccessToUserRequest(BaseModel):
    username: str
    access: RolesEnum


@app.put("/users/access")
async def change_user_access(
        body: AddAccessToUserRequest,
        db: AsyncSession = Depends(get_db),
        role: RoleInService = Depends(check_role(RolesEnum.admin))
):
    """
    Edit roles of user in your service
    """

    user_queries = UserQueries(db)
    roles_queries = ServiceRolesQueries(db)

    target_user = await user_queries.get_user_by_username(body.username)
    if not target_user:
        raise HTTPException(status_code=404, detail="Unable to find user by username")

    await roles_queries.change_user_access(target_user.id, body.access, role.service)
    return {"updated": True}


class DeleteUserRequest(BaseModel):
    username: str


@app.delete("/users")
async def delete_user(
        body: DeleteUserRequest,
        db: AsyncSession = Depends(get_db),
        role: RoleInService = Depends(check_role(RolesEnum.admin))
):
    """
    Delete user if they belong to your service
    """

    user_queries = UserQueries(db)
    target_user = await user_queries.get_user_by_username_if_has_role(body.username, role.service)
    if not target_user:
        raise HTTPException(status_code=400, detail="You can delete users only from your service")
    await user_queries.delete_user(body.username)
    return {"deleted": True}
