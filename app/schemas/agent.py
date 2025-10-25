"""
Agent Configuration Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class AgentConfigCreate(BaseModel):
    """Create agent configuration (Owner only)"""
    agent_id: str = Field(..., pattern="^[a-z_]+$")
    name: str
    display_name: Optional[str] = None
    avatar: str = "🤖"
    role: str
    description: Optional[str] = None
    system_prompt: str
    personality: Optional[str] = None
    tone: str = "professional"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    capabilities: List[str] = []
    allowed_tools: List[UUID] = []
    is_active: bool = True
    is_visible: bool = True
    display_order: float = 0


class AgentConfigUpdate(BaseModel):
    """Update agent configuration (Owner only)"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    personality: Optional[str] = None
    tone: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    capabilities: Optional[List[str]] = None
    allowed_tools: Optional[List[UUID]] = None
    is_active: Optional[bool] = None
    is_visible: Optional[bool] = None
    display_order: Optional[float] = None


class AgentConfigResponse(BaseModel):
    """Agent configuration response"""
    id: UUID
    agent_id: str
    name: str
    display_name: Optional[str]
    avatar: str
    role: str
    description: Optional[str]
    system_prompt: str
    personality: Optional[str]
    tone: str
    temperature: float
    capabilities: List[str]
    allowed_tools: List[UUID]
    is_active: bool
    is_visible: bool
    display_order: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentChatCreate(BaseModel):
    """Create a new agent chat"""
    agent_id: str
    initial_message: Optional[str] = None


class AgentChatResponse(BaseModel):
    """Agent chat response"""
    id: UUID
    agent_id: str
    agent_name: str
    agent_avatar: str
    title: Optional[str]
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentChatMessageCreate(BaseModel):
    """Send message in agent chat"""
    content: str


class AgentChatMessageResponse(BaseModel):
    """Agent chat message response"""
    id: UUID
    role: str
    content: str
    tool_execution_id: Optional[UUID]
    meta_data: Optional[Dict[str, Any]]  # Changed from metadata
    created_at: datetime
    
    class Config:
        from_attributes = True