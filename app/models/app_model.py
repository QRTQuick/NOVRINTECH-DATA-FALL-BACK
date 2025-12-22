from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from app.core.database import Base

class AppStatus(str, enum.Enum):
    active = "active"
    revoked = "revoked"

class App(Base):
    __tablename__ = "apps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False, index=True)
    status = Column(Enum(AppStatus), default=AppStatus.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
