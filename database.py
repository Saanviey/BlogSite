from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import  DeclarativeBase

db_url = "sqlite+aiosqlite:///./blog.db"

engine= create_async_engine(db_url )

SessionLocal = async_sessionmaker( engine , class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
   async with SessionLocal() as session:
       yield session

