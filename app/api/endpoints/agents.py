"""
Agent Endpoints - Updated for Dynamic Agents
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.agents.registry import agent_registry
from app.models.agent_config import AgentConfig
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.utils.logger import logger

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available agents (from database)"""
    
    # Get agent configs from database
    if current_user.role == UserRole.OWNER:
        # Owner sees all agents
        agent_configs = db.query(AgentConfig).order_by(
            AgentConfig.display_order
        ).all()
    else:
        # Users see only visible and active agents
        agent_configs = db.query(AgentConfig).filter(
            AgentConfig.is_visible == True,
            AgentConfig.is_active == True
        ).order_by(AgentConfig.display_order).all()
    
    agents_data = []
    
    for config in agent_configs:
        # Get runtime status from registry
        agent = agent_registry.get_agent(config.agent_id)
        status = agent.get_status() if agent else {
            "status": "offline",
            "tasks_completed": 0,
            "tasks_failed": 0
        }
        
        agents_data.append({
            "agent_id": config.agent_id,
            "name": config.display_name or config.name,
            "full_name": config.name,
            "role": config.role,
            "description": config.description,
            "avatar": config.avatar,
            "personality": config.personality,
            "capabilities": config.capabilities or [],
            "status": status.get("status", "idle"),
            "current_task": status.get("current_task"),
            "tasks_completed": status.get("tasks_completed", 0),
            "tasks_failed": status.get("tasks_failed", 0),
            "is_active": config.is_active,
            "is_visible": config.is_visible,
            "allowed_tools": config.allowed_tools or []
        })
    
    return agents_data


@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific agent details"""
    
    # Get from database
    config = db.query(AgentConfig).filter(
        AgentConfig.agent_id == agent_id
    ).first()
    
    if not config:
        return {"error": "Agent not found"}
    
    # Users can only see visible agents
    if current_user.role != UserRole.OWNER and not config.is_visible:
        return {"error": "Agent not found"}
    
    # Get runtime status
    agent = agent_registry.get_agent(agent_id)
    status = agent.get_status() if agent else {
        "status": "offline",
        "tasks_completed": 0,
        "tasks_failed": 0
    }
    
    return {
        "agent_id": config.agent_id,
        "name": config.display_name or config.name,
        "full_name": config.name,
        "role": config.role,
        "description": config.description,
        "avatar": config.avatar,
        "personality": config.personality,
        "tone": config.tone,
        "capabilities": config.capabilities or [],
        "status": status.get("status", "idle"),
        "current_task": status.get("current_task"),
        "tasks_completed": status.get("tasks_completed", 0),
        "tasks_failed": status.get("tasks_failed", 0),
        "is_active": config.is_active,
        "is_visible": config.is_visible,
        "allowed_tools": config.allowed_tools or [],
        "system_prompt": config.system_prompt if current_user.role == UserRole.OWNER else None
    }


@router.get("/templates/list", response_model=Dict[str, Any])
async def get_agent_templates(
    current_user: User = Depends(get_current_user)
):
    """Get agent creation templates (Owner only)"""
    
    if current_user.role != UserRole.OWNER:
        return {"error": "Owner access required"}
    
    from app.agents.agent_names import AGENT_PROFILE_TEMPLATES
    
    return {
        "templates": AGENT_PROFILE_TEMPLATES,
        "message": "These are suggested templates. You can create agents with any configuration."
    }