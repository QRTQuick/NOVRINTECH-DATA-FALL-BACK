from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.app_model import App, AppStatus

# Public endpoints that don't require API key
PUBLIC_ENDPOINTS = ["/", "/docs", "/redoc", "/openapi.json", "/health"]

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in PUBLIC_ENDPOINTS:
            return await call_next(request)
        
        # Get API key from header
        api_key = request.headers.get("X-API-KEY")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key missing. Include X-API-KEY header."
            )
        
        # Validate API key
        db: Session = SessionLocal()
        try:
            app = db.query(App).filter(
                App.api_key == api_key,
                App.status == AppStatus.active
            ).first()
            
            if not app:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or revoked API key"
                )
            
            # Attach app_id to request state
            request.state.app_id = str(app.id)
            request.state.app_name = app.app_name
            
        finally:
            db.close()
        
        response = await call_next(request)
        return response
