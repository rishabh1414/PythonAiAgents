"""
Tool Schemas
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class ToolParameterSchema(BaseModel):
    """Schema for tool parameter definition"""
    type: str  # email, string, number, boolean, etc.
    required: bool = True
    description: Optional[str] = None
    format: Optional[str] = None  # html, markdown, etc.
    default: Optional[Any] = None
    enum: Optional[List[str]] = None  # For dropdown options


class ToolCreate(BaseModel):
    """Create new tool (Owner only)"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    category: Optional[str] = None
    default_webhook_url: Optional[str] = None
    requires_auth: bool = False
    parameters_schema: Dict[str, ToolParameterSchema]
    available_to_agents: List[str] = []
    is_active: bool = True


class ToolUpdate(BaseModel):
    """Update tool (Owner only)"""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    category: Optional[str] = None
    default_webhook_url: Optional[str] = None
    requires_auth: Optional[bool] = None
    parameters_schema: Optional[Dict[str, ToolParameterSchema]] = None
    available_to_agents: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ToolResponse(BaseModel):
    """Tool response"""
    id: UUID
    name: str
    description: Optional[str]
    logo_url: Optional[str]
    category: Optional[str]
    default_webhook_url: Optional[str]
    requires_auth: bool
    parameters_schema: Dict[str, Any]
    available_to_agents: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserToolConfig(BaseModel):
    """User's tool configuration"""
    tool_id: UUID
    webhook_url: str = Field(..., description="User's webhook URL for this tool")
    config: Optional[Dict[str, Any]] = None
    is_enabled: bool = True


class UserToolResponse(BaseModel):
    """User tool response"""
    id: UUID
    tool_id: UUID
    tool_name: str
    tool_logo: Optional[str]
    webhook_url: Optional[str]
    is_enabled: bool
    tool_description: Optional[str]
    parameters_schema: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ToolExecutionRequest(BaseModel):
    """Request to execute a tool"""
    tool_id: UUID
    parameters: Dict[str, Any]
    conversation_id: Optional[UUID] = None
    message_id: Optional[UUID] = None


class ToolExecutionResponse(BaseModel):
    """Tool execution response"""
    id: UUID
    tool_id: UUID
    tool_name: str
    status: str
    request_payload: Dict[str, Any]
    response_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True