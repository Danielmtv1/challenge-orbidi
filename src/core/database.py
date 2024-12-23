from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from fastapi import FastAPI
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import get_settings


settings = get_settings()

# SQLAlchemy async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development"
)

class Base(DeclarativeBase):
    pass


# Async session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db_pool() -> asyncpg.Pool:
    """Initialize the asyncpg connection pool with detailed logging"""
    try:
        # Parce URL original to get credentials
        sql_url = make_url(settings.DATABASE_URL)
        
        # Build URL with credentials
        asyncpg_url = f"postgresql://{sql_url.username}:{sql_url.password}@{sql_url.host}:{sql_url.port}/{sql_url.database}"
        
        
        # try to connect to the database
        return await asyncpg.create_pool(
            asyncpg_url,
            min_size=5,
            max_size=20,
            max_inactive_connection_lifetime=300,
            command_timeout=60.0,
            timeout=60.0
        )
    except asyncpg.InvalidPasswordError as e:
        print(f"Authentication failed. Please verify your database credentials.")
        raise
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # try to initialize the database pool
        print("Initializing database pool...")
        app.state.pool = await init_db_pool()
        print("Database pool initialized successfully")
        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory

        async with engine.begin() as conn:
            context = MigrationContext.configure(conn)
            script = ScriptDirectory.from_config(Config("alembic.ini"))

            if context.get_current_revision() != script.get_current_head():
                print("Warning: Database is not up-to-date. Running migrations...")
            else:
                print("Database is up-to-date")
        print("Starting application...")            

        yield
    except Exception as e:
        print(f"Error in lifespan: {str(e)}")
        raise
    finally:
        if hasattr(app.state, 'pool'):
            await app.state.pool.close()

async def get_pool_conn(app: FastAPI):
    """
    Dependency for getting raw asyncpg connections.
    Usage:
        @router.get("/")
        async def handler(conn = Depends(get_pool_conn)):
            ...
    """
    async with app.state.pool.acquire() as conn:
        yield conn