"""
Tool Model - System-wide tools that can be configured per user
"""
from sqlalchemy import Column, String, JSON, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.database import Base


class Tool(Base):
    """System-wide tool configuration (Owner managed)"""
    __tablename__ = "tools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # e.g., "Gmail Sender"
    description = Column(Text)
    logo_url = Column(String)  # Tool icon/logo
    category = Column(String)  # e.g., "email", "calendar", "crm"
    
    # Webhook configuration
    default_webhook_url = Column(String)  # Optional default URL
    requires_auth = Column(Boolean, default=False)
    
    # Tool parameters schema (JSON Schema for validation)
    parameters_schema = Column(JSON)  # Defines what params the tool needs
    
    # Example:
    # {
    #   "to": {"type": "email", "required": true, "description": "Recipient email"},
    #   "subject": {"type": "string", "required": true},
    #   "body": {"type": "string", "required": true, "format": "html"}
    # }
    
    # Which agent can use this tool
    available_to_agents = Column(JSON)  # List of agent IDs
    
    # Tool status
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_tools = relationship("UserTool", back_populates="tool", cascade="all, delete-orphan")
    tool_executions = relationship("ToolExecution", back_populates="tool")


class UserTool(Base):
    """User-specific tool configuration"""
    __tablename__ = "user_tools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    
    # User's webhook URL for this tool
    webhook_url = Column(String)
    
    # User-specific configuration
    config = Column(JSON)  # Additional user settings
    
    is_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_tools")
    tool = relationship("Tool", back_populates="user_tools")


class ToolExecution(Base):
    """Track tool execution and responses"""
    __tablename__ = "tool_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    
    # Execution details
    agent_id = Column(String)  # Which agent triggered this
    webhook_url = Column(String)  # URL that was called
    
    # Request data
    request_payload = Column(JSON)  # What was sent to webhook
    
    # Response data
    status = Column(String, default="pending")  # pending, success, failed, timeout
    response_data = Column(JSON)  # Response from webhook
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    timeout_at = Column(DateTime)  # When to give up waiting
    
    # Relationships
    tool = relationship("Tool", back_populates="tool_executions")
    user = relationship("User")
    conversation = relationship("Conversation")
    message = relationship("Message")