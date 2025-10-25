"""
Webhook Schemas
Pydantic models for Make.com webhooks
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class WebhookPayload(BaseModel):
    """Schema for outgoing webhook payload"""
    task_id: UUID
    task_type: str
    data: Dict[str, Any]
    user_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebhookResponse(BaseModel):
    """Schema for webhook response from Make.com"""
    success: bool
    task_id: UUID
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class WebhookCallback(BaseModel):
    """Schema for webhook callback"""
    task_id: UUID
    status: str = Field(..., pattern="^(completed|failed|processing)$")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    callback_metadata: Optional[Dict[str, Any]] = {}  # Changed from metadata


class WebhookConfig(BaseModel):
    """Schema for webhook configuration"""
    url: HttpUrl
    enabled: bool = True
    retry_count: int = Field(default=3, ge=0, le=10)
    timeout: int = Field(default=30, ge=5, le=300)
    headers: Optional[Dict[str, str]] = {}


class WebhookLog(BaseModel):
    """Schema for webhook execution log"""
    webhook_id: UUID
    task_id: UUID
    url: str
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None
    created_at: datetime