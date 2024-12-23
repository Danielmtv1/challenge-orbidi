import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import get_settings
from src.api.v1.router import api_router
from src.core.database import engine, Base, init_db_pool

settings = get_settings()

print("Loading config settings from the environment...")
print("Database URL:", settings.DATABASE_URL)
print("Redis URL:", settings.REDIS_URL)
print("API Key Header:", settings.API_KEY_HEADER)
print("Review Expiration Days:", settings.REVIEW_EXPIRATION_DAYS)

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de vida de la aplicación para setup y cleanup
    """
    # Setup
    app.state.pool = await init_db_pool()
    
    # create tables in development
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO in production, change to a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
