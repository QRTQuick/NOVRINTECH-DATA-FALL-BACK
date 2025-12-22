from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routes import data_routes, file_routes, health
from app.middleware.api_key_auth import APIKeyMiddleware

app = FastAPI(
    title="Novrintech Data Fall Back API",
    description="Universal backend API for data storage and retrieval",
    version="1.0.0"
)

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
    init_db()

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(data_routes.router, prefix="/data", tags=["Data"])
app.include_router(file_routes.router, prefix="/file", tags=["Files"])

@app.get("/")
async def root():
    return {
        "service": "Novrintech Data Fall Back API",
        "status": "active",
        "version": "1.0.0"
    }
