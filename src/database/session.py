from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from env_config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT or 5432,
    database=DB_NAME,
)

engine = create_async_engine(
    database_url, echo=True
)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    async with SessionLocal() as session:
        yield session
