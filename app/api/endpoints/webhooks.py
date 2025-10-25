"""
Webhook Endpoints
Handle Make.com webhook integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.models.task import Task
from app.schemas.webhook import WebhookCallback, WebhookResponse
from app.services.webhook_service import webhook_service
from app.utils.logger import logger
from uuid import UUID

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/make", response_model=Dict[str, Any])
async def receive_make_webhook(
    callback_data: WebhookCallback,
    db: Session = Depends(get_db)
):
    """
    Receive callback from Make.com
    """
    logger.info(f"Received Make.com webhook for task {callback_data.task_id}")
    
    # Find task
    task = db.query(Task).filter(Task.id == callback_data.task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update task status
    task.status = callback_data.status
    task.webhook_status = "received"
    
    if callback_data.result:
        task.result = callback_data.result
    
    if callback_data.error_message:
        task.error_message = callback_data.error_message
    
    if callback_data.status == "completed":
        from datetime import datetime
        task.completed_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Task {callback_data.task_id} updated from webhook")
    
    return {
        "success": True,
        "task_id": str(callback_data.task_id),
        "status": callback_data.status
    }


@router.post("/send/{task_id}", response_model=WebhookResponse)
async def send_webhook(
    task_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send task to Make.com webhook
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Prepare webhook data
    webhook_data = {
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "priority": task.priority
    }
    
    # Send webhook with retry
    result = await webhook_service.send_with_retry(
        task_id=str(task.id),
        task_type=task.task_type,
        data=webhook_data,
        webhook_url=task.webhook_url
    )
    
    # Update task
    task.webhook_status = "sent" if result["success"] else "failed"
    if result["success"]:
        task.status = "processing"
    
    db.commit()
    
    return WebhookResponse(
        success=result["success"],
        task_id=task.id,
        result=result.get("response"),
        error=result.get("error"),
        execution_time=result.get("execution_time")
    )


@router.post("/callback")
async def webhook_callback(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Generic webhook callback handler
    """
    result = await webhook_service.handle_callback(data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result