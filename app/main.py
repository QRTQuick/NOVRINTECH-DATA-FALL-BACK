from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging
from app.routes import data_routes, file_routes, health, admin_routes
from app.middleware.api_key_auth import APIKeyMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.services.keep_alive import keep_alive_service

# Setup logging
setup_logging()

app = FastAPI(
    title="Novrintech Data Fall Back API",
    description="Universal backend API for data storage and retrieval",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Production Middleware Stack (order matters!)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication Middleware
app.add_middleware(APIKeyMiddleware)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        # Start keep-alive service
        keep_alive_service.start()
        print("✅ Novrintech Data Fall Back API started successfully!")
    except Exception as e:
        print(f"❌ Startup error: {e}")

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    try:
        keep_alive_service.stop()
        print("🔄 Novrintech Data Fall Back API shutting down...")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(data_routes.router, prefix="/data", tags=["Data"])
app.include_router(file_routes.router, prefix="/file", tags=["Files"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "service": "Novrintech Data Fall Back API",
        "status": "active",
        "version": "1.0.0"
    }
