from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData()


async def init_db():
    # создаёт все таблицы, описанные в metadata
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
