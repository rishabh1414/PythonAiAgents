"""
Tool Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.tool import Tool, UserTool, ToolExecution
from app.schemas.tool import (
    ToolCreate, ToolUpdate, ToolResponse,
    UserToolConfig, UserToolResponse,
    ToolExecutionRequest, ToolExecutionResponse
)
from app.core.dependencies import get_current_user, require_owner
from app.services.tool_service import tool_service
from app.utils.logger import logger

router = APIRouter(prefix="/tools", tags=["Tools"])


# ========== OWNER ENDPOINTS ==========

@router.post("", response_model=ToolResponse, dependencies=[Depends(require_owner)])
async def create_tool(
    tool_data: ToolCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new tool (Owner only)"""
    
    # Convert parameters_schema to dict
    params_schema = {
        key: value.dict() for key, value in tool_data.parameters_schema.items()
    }
    
    tool = Tool(
        name=tool_data.name,
        description=tool_data.description,
        logo_url=tool_data.logo_url,
        category=tool_data.category,
        default_webhook_url=tool_data.default_webhook_url,
        requires_auth=tool_data.requires_auth,
        parameters_schema=params_schema,
        available_to_agents=tool_data.available_to_agents,
        is_active=tool_data.is_active,
        created_by=current_user.id
    )
    
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    logger.info(f"Tool created: {tool.name} by {current_user.email}")
    
    return tool


@router.get("", response_model=List[ToolResponse])
async def get_all_tools(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tools (filtered by role)"""
    
    if current_user.role == UserRole.OWNER:
        # Owner sees all tools
        tools = db.query(Tool).all()
    else:
        # Users see only active tools
        tools = db.query(Tool).filter(Tool.is_active == True).all()
    
    return tools


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tool by ID"""
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    return tool


@router.put("/{tool_id}", response_model=ToolResponse, dependencies=[Depends(require_owner)])
async def update_tool(
    tool_id: UUID,
    tool_data: ToolUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update tool (Owner only)"""
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Update fields
    update_data = tool_data.dict(exclude_unset=True)
    
    if "parameters_schema" in update_data and update_data["parameters_schema"]:
        update_data["parameters_schema"] = {
            key: value.dict() if hasattr(value, 'dict') else value
            for key, value in update_data["parameters_schema"].items()
        }
    
    for field, value in update_data.items():
        setattr(tool, field, value)
    
    db.commit()
    db.refresh(tool)
    
    logger.info(f"Tool updated: {tool.name}")
    
    return tool


@router.delete("/{tool_id}", dependencies=[Depends(require_owner)])
async def delete_tool(
    tool_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete tool (Owner only)"""
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    db.delete(tool)
    db.commit()
    
    logger.info(f"Tool deleted: {tool.name}")
    
    return {"message": "Tool deleted successfully"}


# ========== USER ENDPOINTS ==========

@router.get("/my-tools", response_model=List[UserToolResponse])
async def get_my_tools(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's configured tools"""
    
    user_tools = db.query(UserTool).filter(
        UserTool.user_id == current_user.id
    ).all()
    
    result = []
    for ut in user_tools:
        tool = db.query(Tool).filter(Tool.id == ut.tool_id).first()
        if tool:
            result.append({
                "id": ut.id,
                "tool_id": tool.id,
                "tool_name": tool.name,
                "tool_logo": tool.logo_url,
                "webhook_url": ut.webhook_url,
                "is_enabled": ut.is_enabled,
                "tool_description": tool.description,
                "parameters_schema": tool.parameters_schema,
                "created_at": ut.created_at
            })
    
    return result


@router.post("/configure", response_model=UserToolResponse)
async def configure_tool(
    config: UserToolConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure tool webhook URL (User can do this)"""
    
    # Check if tool exists
    tool = db.query(Tool).filter(Tool.id == config.tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Check if user already has this tool
    user_tool = db.query(UserTool).filter(
        UserTool.user_id == current_user.id,
        UserTool.tool_id == config.tool_id
    ).first()
    
    if user_tool:
        # Update existing
        user_tool.webhook_url = config.webhook_url
        user_tool.config = config.config
        user_tool.is_enabled = config.is_enabled
    else:
        # Create new
        user_tool = UserTool(
            user_id=current_user.id,
            tool_id=config.tool_id,
            webhook_url=config.webhook_url,
            config=config.config,
            is_enabled=config.is_enabled
        )
        db.add(user_tool)
    
    db.commit()
    db.refresh(user_tool)
    
    logger.info(f"Tool configured: {tool.name} for user {current_user.email}")
    
    return {
        "id": user_tool.id,
        "tool_id": tool.id,
        "tool_name": tool.name,
        "tool_logo": tool.logo_url,
        "webhook_url": user_tool.webhook_url,
        "is_enabled": user_tool.is_enabled,
        "tool_description": tool.description,
        "parameters_schema": tool.parameters_schema,
        "created_at": user_tool.created_at
    }


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    execution_request: ToolExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a tool"""
    
    try:
        execution = await tool_service.execute_tool(
            db=db,
            tool_id=execution_request.tool_id,
            user_id=current_user.id,
            parameters=execution_request.parameters,
            agent_id="manual",  # Manual execution
            conversation_id=execution_request.conversation_id,
            message_id=execution_request.message_id
        )
        
        # Wait for execution
        execution = await tool_service.wait_for_execution(db, execution.id)
        
        tool = db.query(Tool).filter(Tool.id == execution.tool_id).first()
        
        return {
            "id": execution.id,
            "tool_id": execution.tool_id,
            "tool_name": tool.name if tool else "Unknown",
            "status": execution.status,
            "request_payload": execution.request_payload,
            "response_data": execution.response_data,
            "error_message": execution.error_message,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/executions/{execution_id}", response_model=ToolExecutionResponse)
async def get_execution_status(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tool execution status"""
    
    execution = db.query(ToolExecution).filter(
        ToolExecution.id == execution_id,
        ToolExecution.user_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    tool = db.query(Tool).filter(Tool.id == execution.tool_id).first()
    
    return {
        "id": execution.id,
        "tool_id": execution.tool_id,
        "tool_name": tool.name if tool else "Unknown",
        "status": execution.status,
        "request_payload": execution.request_payload,
        "response_data": execution.response_data,
        "error_message": execution.error_message,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at
    }