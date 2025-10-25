"""
Task Model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.database import Base


class Task(Base):
    """Task model for agent work"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    # Task details
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(String)  # email, research, analysis, etc.
    
    # Assignment
    assigned_agent = Column(String)  # Agent ID
    
    # Status
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    priority = Column(String, default="medium")  # low, medium, high
    
    # Results
    result = Column(JSON)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="tasks")