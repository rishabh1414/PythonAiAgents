"""
Chat Endpoints - Updated with Multi-Agent Collaboration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.chat import (
    ChatRequest, ChatResponse, ConversationResponse,
    ConversationWithMessages, MessageResponse, ConversationCreate
)
from app.core.dependencies import get_current_user
from app.agents.registry import agent_registry
from app.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/send", response_model=dict)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a chat message - with intelligent agent routing and collaboration
    """
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # Get conversation history for context
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()
    
    # Build context from history
    context = {
        "conversation_history": [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]  # Last 10 messages
        ],
        "user_id": str(current_user.id),
        "conversation_id": str(conversation.id)
    }
    
    # Route to appropriate agent(s) with collaboration
    logger.info(f"Routing user query: {request.message[:100]}")
    
    agent_result = await agent_registry.route_task(
        user_query=request.message,
        context=context
    )
    
    # Extract response based on collaboration or single agent
    if agent_result.get("collaboration"):
        # Multi-agent collaboration
        response_content = agent_result.get("final_result", "")
        agents_involved = agent_result.get("agents_involved", [])
        agent_name = f"Team: {', '.join(agents_involved)}"
        agent_id = "collaboration"
        
        # Add metadata about which agents contributed
        message_metadata = {
            "collaboration": True,
            "agents_involved": agents_involved,
            "individual_contributions": agent_result.get("individual_contributions", [])
        }
    else:
        # Single agent response
        result_data = agent_result.get("result", {})
        response_content = result_data.get("content", str(agent_result))
        agent_name = result_data.get("agent", "Marcus Williams")
        agent_id = "marcus"
        message_metadata = {
            "collaboration": False,
            "specialty": result_data.get("specialty", "General")
        }
    
    # Save AI response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_content,
        agent_id=agent_id,
        message_metadata=message_metadata
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    logger.info(f"Chat processed by: {agent_name}")
    
    return {
        "message": {
            "id": str(assistant_message.id),
            "conversation_id": str(assistant_message.conversation_id),
            "role": assistant_message.role,
            "content": assistant_message.content,
            "agent_id": assistant_message.agent_id,
            "message_metadata": message_metadata,
            "created_at": assistant_message.created_at.isoformat()
        },
        "agent_name": agent_name,
        "collaboration": message_metadata.get("collaboration", False),
        "agents_involved": message_metadata.get("agents_involved", [])
    }


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.status == "active"
    ).order_by(Conversation.updated_at.desc()).all()
    
    return conversations


@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return {
        "id": str(conversation.id),
        "user_id": str(conversation.user_id),
        "title": conversation.title,
        "status": conversation.status,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "agent_id": msg.agent_id,
                "message_metadata": msg.message_metadata,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.status = "deleted"
    db.commit()
    
    return {"message": "Conversation deleted successfully"}