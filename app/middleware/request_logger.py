from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.file_model import RequestLog
import time
import uuid

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get app_id if available
        app_id = getattr(request.state, 'app_id', None)
        
        response = await call_next(request)
        
        # Log the request
        try:
            db: Session = SessionLocal()
            log_entry = RequestLog(
                app_id=uuid.UUID(app_id) if app_id else None,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=str(response.status_code)
            )
            db.add(log_entry)
            db.commit()
            db.close()
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Logging error: {e}")
        
        # Add response time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response