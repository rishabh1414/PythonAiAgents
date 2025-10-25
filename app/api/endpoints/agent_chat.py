"""
User-Agent Chat Endpoints
Each user has separate chat with each agent
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.user import User
from app.models.user_agent_chat import UserAgentChat, AgentChatMessage
from app.models.agent_config import AgentConfig
from app.schemas.agent import (
    AgentChatCreate, AgentChatResponse,
    AgentChatMessageCreate, AgentChatMessageResponse
)
from app.core.dependencies import get_current_user
from app.agents.registry import agent_registry
from app.services.tool_service import tool_service
from app.utils.logger import logger

router = APIRouter(prefix="/agent-chats", tags=["Agent Chats"])


@router.post("", response_model=AgentChatResponse)
async def create_agent_chat(
    chat_data: AgentChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat with an agent"""
    
    # Verify agent exists
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.agent_id == chat_data.agent_id,
        AgentConfig.is_active == True
    ).first()
    
    if not agent_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or inactive"
        )
    
    # Check if user already has a chat with this agent
    existing_chat = db.query(UserAgentChat).filter(
        UserAgentChat.user_id == current_user.id,
        UserAgentChat.agent_id == chat_data.agent_id,
        UserAgentChat.status == "active"
    ).first()
    
    if existing_chat:
        # Return existing chat
        return {
            "id": existing_chat.id,
            "agent_id": existing_chat.agent_id,
            "agent_name": agent_config.name,
            "agent_avatar": agent_config.avatar,
            "title": existing_chat.title,
            "message_count": existing_chat.message_count,
            "last_message_at": existing_chat.last_message_at,
            "created_at": existing_chat.created_at
        }
    
    # Create new chat
    chat = UserAgentChat(
        user_id=current_user.id,
        agent_id=chat_data.agent_id,
        title=f"Chat with {agent_config.name}"
    )
    
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    # Send initial message if provided
    if chat_data.initial_message:
        await send_message_to_agent(
            chat.id,
            AgentChatMessageCreate(content=chat_data.initial_message),
            current_user,
            db
        )
    
    logger.info(f"Agent chat created: {current_user.email} with {chat_data.agent_id}")
    
    return {
        "id": chat.id,
        "agent_id": chat.agent_id,
        "agent_name": agent_config.name,
        "agent_avatar": agent_config.avatar,
        "title": chat.title,
        "message_count": chat.message_count,
        "last_message_at": chat.last_message_at,
        "created_at": chat.created_at
    }


@router.get("", response_model=List[AgentChatResponse])
async def get_my_agent_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user's agent chats"""
    
    chats = db.query(UserAgentChat).filter(
        UserAgentChat.user_id == current_user.id,
        UserAgentChat.status == "active"
    ).order_by(UserAgentChat.last_message_at.desc()).all()
    
    result = []
    for chat in chats:
        agent_config = db.query(AgentConfig).filter(
            AgentConfig.agent_id == chat.agent_id
        ).first()
        
        if agent_config:
            result.append({
                "id": chat.id,
                "agent_id": chat.agent_id,
                "agent_name": agent_config.name,
                "agent_avatar": agent_config.avatar,
                "title": chat.title,
                "message_count": chat.message_count,
                "last_message_at": chat.last_message_at,
                "created_at": chat.created_at
            })
    
    return result


@router.get("/{chat_id}", response_model=dict)
async def get_agent_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent chat with messages"""
    
    chat = db.query(UserAgentChat).filter(
        UserAgentChat.id == chat_id,
        UserAgentChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.agent_id == chat.agent_id
    ).first()
    
    messages = db.query(AgentChatMessage).filter(
        AgentChatMessage.chat_id == chat_id
    ).order_by(AgentChatMessage.created_at).all()
    
    return {
        "id": chat.id,
        "agent_id": chat.agent_id,
        "agent_name": agent_config.name if agent_config else "Unknown",
        "agent_avatar": agent_config.avatar if agent_config else "🤖",
        "title": chat.title,
        "message_count": chat.message_count,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "tool_execution_id": msg.tool_execution_id,
                "meta_data": msg.meta_data,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.post("/{chat_id}/messages", response_model=AgentChatMessageResponse)
async def send_message_to_agent(
    chat_id: UUID,
    message_data: AgentChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to agent in chat"""
    
    # Get chat
    chat = db.query(UserAgentChat).filter(
        UserAgentChat.id == chat_id,
        UserAgentChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Save user message
    user_message = AgentChatMessage(
        chat_id=chat_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    
    # Update chat
    chat.message_count += 1
    chat.last_message_at = user_message.created_at
    
    db.commit()
    db.refresh(user_message)
    
    # Get conversation history
    messages = db.query(AgentChatMessage).filter(
        AgentChatMessage.chat_id == chat_id
    ).order_by(AgentChatMessage.created_at).all()
    
    # Build context
    context = {
        "conversation_history": [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]  # Last 10 messages
        ],
        "user_id": str(current_user.id),
        "chat_id": str(chat_id)
    }
    
    # Get agent and process message
    agent = agent_registry.get_agent(chat.agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not available"
        )
    
    logger.info(f"Processing message for agent: {chat.agent_id}")
    
    # Execute agent
    result = await agent.execute({
        "task_id": f"chat-{chat_id}",
        "content": message_data.content,
        "task_type": "chat",
        "data": context
    })
    
    # Check if agent wants to use a tool
    tool_execution_id = None
    response_content = result.get("result", {}).get("content", "")
    
    # Parse if agent is requesting tool execution
    # Format: [TOOL:tool_id:params_json]
    if "[TOOL:" in response_content:
        try:
            tool_execution_id = await _handle_tool_request(
                response_content, 
                current_user.id, 
                chat.agent_id,
                chat_id,
                db
            )
            
            if tool_execution_id:
                # Wait for tool execution
                execution = await tool_service.wait_for_execution(db, tool_execution_id)
                
                if execution.status == "success":
                    response_content = f"✅ Tool executed successfully!\n\n{execution.response_data.get('message', 'Task completed.')}"
                else:
                    response_content = f"❌ Tool execution failed: {execution.error_message}"
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            response_content += f"\n\n⚠️ Tool execution error: {str(e)}"
    
    # Save assistant response
    assistant_message = AgentChatMessage(
        chat_id=chat_id,
        role="assistant",
        content=response_content,
        tool_execution_id=tool_execution_id,
        meta_data={"agent_result": result}
    )
    db.add(assistant_message)
    
    # Update chat
    chat.message_count += 1
    chat.last_message_at = assistant_message.created_at
    
    db.commit()
    db.refresh(assistant_message)
    
    logger.info(f"Agent response saved for chat: {chat_id}")
    
    return assistant_message


async def _handle_tool_request(
    content: str,
    user_id: UUID,
    agent_id: str,
    chat_id: UUID,
    db: Session
) -> UUID:
    """
    Parse and handle tool execution request from agent
    Format: [TOOL:tool_name:params_json]
    """
    import json
    from app.models.tool import Tool, UserTool
    
    # Extract tool request
    start = content.find("[TOOL:")
    end = content.find("]", start)
    
    if start == -1 or end == -1:
        return None
    
    tool_request = content[start+6:end]
    parts = tool_request.split(":", 2)
    
    if len(parts) < 2:
        return None
    
    tool_name = parts[0]  # e.g., "gmail"
    params = json.loads(parts[1])
    
    # Find tool by name
    tool = db.query(Tool).filter(
        Tool.name.ilike(f"%{tool_name}%"),
        Tool.is_active == True
    ).first()
    
    if not tool:
        logger.error(f"Tool not found: {tool_name}")
        return None
    
    # Check if user has configured this tool
    user_tool = db.query(UserTool).filter(
        UserTool.user_id == user_id,
        UserTool.tool_id == tool.id,
        UserTool.is_enabled == True
    ).first()
    
    if not user_tool or not user_tool.webhook_url:
        logger.warning(f"User hasn't configured tool: {tool_name}")
        return None
    
    # Execute tool
    execution = await tool_service.execute_tool(
        db=db,
        tool_id=tool.id,
        user_id=user_id,
        parameters=params,
        agent_id=agent_id,
        conversation_id=chat_id
    )
    
    return execution.id


@router.delete("/{chat_id}")
async def delete_agent_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete agent chat"""
    
    chat = db.query(UserAgentChat).filter(
        UserAgentChat.id == chat_id,
        UserAgentChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    chat.status = "deleted"
    db.commit()
    
    logger.info(f"Agent chat deleted: {chat_id}")
    
    return {"message": "Chat deleted successfully"}