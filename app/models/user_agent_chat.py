"""
User-Agent Chat History - Separate conversations per agent
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.database import Base


class UserAgentChat(Base):
    """Separate chat thread for each user-agent pair"""
    __tablename__ = "user_agent_chats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_id = Column(String, nullable=False)  # e.g., "jasmine"
    
    title = Column(String)  # Chat title
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime)
    
    # Chat metadata
    status = Column(String, default="active")  # active, archived, deleted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    messages = relationship("AgentChatMessage", back_populates="chat", cascade="all, delete-orphan")


class AgentChatMessage(Base):
    """Messages in user-agent chats"""
    __tablename__ = "agent_chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("user_agent_chats.id"), nullable=False)
    
    role = Column(String, nullable=False)  # user, assistant
    content = Column(String, nullable=False)
    
    # Tool execution reference
    tool_execution_id = Column(UUID(as_uuid=True), ForeignKey("tool_executions.id"))
    
    # Metadata - RENAMED FROM metadata to meta_data
    meta_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat = relationship("UserAgentChat", back_populates="messages")
    tool_execution = relationship("ToolExecution")