"""
Chat Schemas
Pydantic models for chat and messaging
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern="^(user|assistant|system)$")


class MessageCreate(MessageBase):
    """Schema for creating a message"""
    conversation_id: UUID
    agent_id: Optional[str] = None
    message_metadata: Optional[Dict[str, Any]] = {}  # Changed from metadata


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: UUID
    conversation_id: UUID
    agent_id: Optional[str] = None
    message_metadata: Dict[str, Any] = {}  # Changed from metadata
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: str = Field(default="New Conversation", max_length=200)


class ConversationCreate(ConversationBase):
    """Schema for creating conversation"""
    pass


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages"""
    messages: List[MessageResponse] = []


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Schema for chat response"""
    message: MessageResponse
    agent_id: str
    agent_name: str