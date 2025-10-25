"""
Task Schemas
Pydantic models for task management
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: str = Field(..., pattern="^(email|social|content|research)$")
    priority: int = Field(default=1, ge=1, le=3)


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    conversation_id: Optional[UUID] = None
    webhook_url: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    result: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: UUID
    user_id: UUID
    conversation_id: Optional[UUID] = None
    status: str
    assigned_agent: Optional[str] = None
    result: Dict[str, Any] = {}
    error_message: Optional[str] = None
    webhook_status: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    """Schema for task status update"""
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$")
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None