"""
Agent Configuration Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.agent_config import AgentConfig
from app.schemas.agent import (
    AgentConfigCreate, AgentConfigUpdate, AgentConfigResponse
)
from app.core.dependencies import get_current_user, require_owner
from app.utils.logger import logger
from app.agents.registry import agent_registry

router = APIRouter(prefix="/agent-config", tags=["Agent Configuration"])


# ========== OWNER ENDPOINTS ==========

@router.post("", response_model=AgentConfigResponse, dependencies=[Depends(require_owner)])
async def create_agent_config(
    agent_data: AgentConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new agent configuration (Owner only)"""
    
    # Check if agent_id already exists
    existing = db.query(AgentConfig).filter(
        AgentConfig.agent_id == agent_data.agent_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with ID '{agent_data.agent_id}' already exists"
        )
    
    agent_config = AgentConfig(**agent_data.dict())
    
    db.add(agent_config)
    db.commit()
    db.refresh(agent_config)
    
    # RELOAD AGENT IN REGISTRY
    agent_registry.reload_agent(db, agent_config.agent_id)
    
    logger.info(f"Agent config created and loaded: {agent_config.name} by {current_user.email}")
    
    return agent_config


@router.get("", response_model=List[AgentConfigResponse])
async def get_all_agent_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all agent configurations"""
    
    if current_user.role == UserRole.OWNER:
        # Owner sees all agents
        agents = db.query(AgentConfig).order_by(AgentConfig.display_order).all()
    else:
        # Users see only visible and active agents
        agents = db.query(AgentConfig).filter(
            AgentConfig.is_visible == True,
            AgentConfig.is_active == True
        ).order_by(AgentConfig.display_order).all()
    
    return agents


@router.get("/{agent_id}", response_model=AgentConfigResponse)
async def get_agent_config(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent configuration by agent_id"""
    
    agent = db.query(AgentConfig).filter(
        AgentConfig.agent_id == agent_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Users can only see visible agents
    if current_user.role != UserRole.OWNER and not agent.is_visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentConfigResponse, dependencies=[Depends(require_owner)])
async def update_agent_config(
    agent_id: str,
    agent_data: AgentConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update agent configuration (Owner only)"""
    
    agent = db.query(AgentConfig).filter(
        AgentConfig.agent_id == agent_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Update fields
    update_data = agent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    
    # RELOAD AGENT IN REGISTRY
    agent_registry.reload_agent(db, agent.agent_id)
    
    logger.info(f"Agent config updated and reloaded: {agent.name}")
    
    return agent


@router.delete("/{agent_id}", dependencies=[Depends(require_owner)])
async def delete_agent_config(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete agent configuration (Owner only)"""
    
    agent = db.query(AgentConfig).filter(
        AgentConfig.agent_id == agent_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    db.delete(agent)
    db.commit()
    
    # REMOVE AGENT FROM REGISTRY
    agent_registry.unregister_agent(agent_id)
    
    logger.info(f"Agent deleted and unregistered: {agent.name}")
    
    return {"message": "Agent configuration deleted successfully"}


@router.post("/{agent_id}/toggle", response_model=AgentConfigResponse, dependencies=[Depends(require_owner)])
async def toggle_agent_status(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle agent active status (Owner only)"""
    
    agent = db.query(AgentConfig).filter(
        AgentConfig.agent_id == agent_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent.is_active = not agent.is_active
    db.commit()
    db.refresh(agent)
    
    logger.info(f"Agent {agent.name} status toggled to: {agent.is_active}")
    
    return agent