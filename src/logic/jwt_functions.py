import datetime

from fastapi import HTTPException

from jwt import PyJWT, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from database.queries import UserQueries
from env_config import SECRET_KEY


def get_jwt_for_user(username: str, service: str):
    pyjwt = PyJWT()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    return pyjwt.encode(
        {"username": username, "service": service, "exp": expires_at},
        SECRET_KEY,
        algorithm="HS256"
    )


async def get_user_by_jwt(jwt: str | None, db: AsyncSession):
    if jwt is None:
        raise HTTPException(status_code=403, detail="JWT must not be empty")
    pyjwt = PyJWT()
    try:
        payload = pyjwt.decode(jwt, SECRET_KEY, algorithms=["HS256"], leeway=datetime.timedelta(seconds=30))
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="JWT is expired, please get a new one")
    username, service = str(payload.get("username")), str(payload.get("service"))
    if username is None or service is None:
        raise HTTPException(status_code=403, detail=f"Unable to get user by JWT: token is malformed")
    user_queries = UserQueries(db)
    user = await user_queries.get_user_by_username_if_has_role(username, service)
    return user
