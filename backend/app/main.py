"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging, get_logger
from backend.app.api import rss
from backend.app.api import groups
from backend.app.api import items
from backend.app.api import sources
from backend.app.api import persons
from backend.app.api import bookmarks
from backend.app.api import watch_rules
from backend.app.api import insights
from backend.app.api import constants
from backend.app.core.scheduler import start_scheduler, stop_scheduler, is_scheduler_running

# Configure logging (development/production aware)
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Trend Monitor API...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down AI Trend Monitor API...")
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS 설정
cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(rss.router, prefix="/api/rss")
app.include_router(groups.router)
app.include_router(items.router)
app.include_router(sources.router)
app.include_router(persons.router)
app.include_router(bookmarks.router)
app.include_router(watch_rules.router)
app.include_router(insights.router)
app.include_router(constants.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Trend Monitor API",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        dict: Health status including:
            - status: "healthy" or "unhealthy"
            - scheduler_running: Whether the scheduler is running
            - database_connected: Whether the database connection is active
    """
    from sqlalchemy import text
    from backend.app.core.database import get_engine
    
    db_status = "connected"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    overall_status = "healthy" if db_status == "connected" and is_scheduler_running() else "unhealthy"
    
    return {
        "status": overall_status,
        "scheduler_running": is_scheduler_running(),
        "database_connected": db_status == "connected",
    }

