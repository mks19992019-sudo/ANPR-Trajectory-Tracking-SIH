import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed import seed_database
from backend.app.routers import events, vehicles, cameras, traffic, alerts, blacklist, prediction, websocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anpr_platform")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed initial deterministic data
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Seeding initial checkpoints, roads, blacklist, and demo scenarios...")
        seed_database(db)
    finally:
        db.close()
    
    logger.info("Backend service startup completed.")
    yield
    logger.info("Shutting down backend service.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Centralized ANPR Vehicle Tracking, Trajectory Reconstruction & Traffic Analytics Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Checks
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "ANPR Traffic Intelligence Engine",
        "database": "CONNECTED",
        "prototype_mode": True
    }

# Register Routers under /api (and /api/v1 for backwards compatibility)
for prefix in ["/api", "/api/v1"]:
    app.include_router(events.router, prefix=prefix)
    app.include_router(vehicles.router, prefix=prefix)
    app.include_router(cameras.router, prefix=prefix)
    app.include_router(traffic.router, prefix=prefix)
    app.include_router(alerts.router, prefix=prefix)
    app.include_router(blacklist.router, prefix=prefix)
    app.include_router(prediction.router, prefix=prefix)

# Additional alias for /api/v1/anpr/events
app.include_router(events.router, prefix="/api/v1/anpr")

# WebSocket Router
app.include_router(websocket.router)
