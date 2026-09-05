import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed import seed_database
from backend.app.routers import events, vehicles, cameras, traffic, alerts, blacklist, prediction, websocket

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("anpr.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and deterministic initial seed
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Checking & seeding checkpoint cameras, arterial roads, and blacklist data...")
        seed_database(db)
    finally:
        db.close()
    
    logger.info(f"{settings.PROJECT_NAME} startup completed.")
    yield
    logger.info("Shutting down backend service.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Centralized ANPR Vehicle Tracking, Trajectory Reconstruction & Traffic Analytics Engine",
    version="1.0.0",
    lifespan=lifespan
)

# 1. Request Timing & Structured Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Standardized Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "detail": "An unexpected server error occurred."}
    )

# 4. Health and Readiness Probes
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "ANPR Traffic Intelligence Engine",
        "database": "CONNECTED",
        "prototype_mode": True
    }

@app.get("/ready", tags=["Health"])
@app.get("/api/ready", tags=["Health"])
def readiness_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "READY", "database": "OPERATIONAL"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "NOT_READY", "error": str(e)}
        )

# 5. Register Routers under /api and /api/v1
for prefix in ["/api", "/api/v1"]:
    app.include_router(events.router, prefix=prefix)
    app.include_router(vehicles.router, prefix=prefix)
    app.include_router(cameras.router, prefix=prefix)
    app.include_router(traffic.router, prefix=prefix)
    app.include_router(alerts.router, prefix=prefix)
    app.include_router(blacklist.router, prefix=prefix)
    app.include_router(prediction.router, prefix=prefix)

# WebSocket Router
app.include_router(websocket.router)
