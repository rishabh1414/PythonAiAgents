"""
Agent Configuration Model - Owner can customize agents
"""
from sqlalchemy import Column, String, JSON, Boolean, Text, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.database import Base


class AgentConfig(Base):
    """Agent configuration (Owner managed)"""
    __tablename__ = "agent_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, unique=True, nullable=False)  # e.g., "jasmine"
    
    # Display information
    name = Column(String, nullable=False)  # e.g., "Jasmine Thompson"
    display_name = Column(String)  # Optional custom display name
    avatar = Column(String)  # Emoji or URL
    role = Column(String)  # e.g., "Email Specialist"
    description = Column(Text)
    
    # System prompt (Owner can customize)
    system_prompt = Column(Text)
    
    # Personality and behavior
    personality = Column(Text)
    tone = Column(String)  # professional, casual, friendly, etc.
    temperature = Column(Float, default=0.7)
    
    # Capabilities
    capabilities = Column(JSON)  # List of what agent can do
    
    # Tool access
    allowed_tools = Column(JSON)  # List of tool IDs this agent can use
    
    # Status
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)  # Show to users
    
    # Order for display
    display_order = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)