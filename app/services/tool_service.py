"""
Tool Service - Handle tool execution and webhooks
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.tool import Tool, UserTool, ToolExecution
from app.models.user import User
from app.utils.logger import logger


class ToolService:
    """Service for tool execution and webhook handling"""
    
    def __init__(self):
        self.timeout = 60  # Default timeout in seconds
        self.pending_executions = {}  # Store pending executions
    
    async def execute_tool(
        self,
        db: Session,
        tool_id: UUID,
        user_id: UUID,
        parameters: Dict[str, Any],
        agent_id: str,
        conversation_id: Optional[UUID] = None,
        message_id: Optional[UUID] = None
    ) -> ToolExecution:
        """
        Execute a tool by sending webhook request
        
        Args:
            db: Database session
            tool_id: Tool ID
            user_id: User ID
            parameters: Tool parameters
            agent_id: Agent executing the tool
            conversation_id: Optional conversation ID
            message_id: Optional message ID
            
        Returns:
            ToolExecution object
        """
        # Get tool
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise ValueError("Tool not found")
        
        # Get user's tool configuration
        user_tool = db.query(UserTool).filter(
            UserTool.user_id == user_id,
            UserTool.tool_id == tool_id
        ).first()
        
        if not user_tool or not user_tool.webhook_url:
            raise ValueError("User has not configured this tool. Please add webhook URL.")
        
        # Validate parameters against schema
        validated_params = self._validate_parameters(parameters, tool.parameters_schema)
        
        # Create execution record
        execution = ToolExecution(
            tool_id=tool_id,
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            agent_id=agent_id,
            webhook_url=user_tool.webhook_url,
            request_payload=validated_params,
            status="pending",
            timeout_at=datetime.utcnow() + timedelta(seconds=self.timeout)
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        logger.info(f"Tool execution created: {execution.id} for tool {tool.name}")
        
        # Send webhook request asynchronously
        asyncio.create_task(self._send_webhook(execution.id, user_tool.webhook_url, validated_params, db))
        
        return execution
    
    def _validate_parameters(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate parameters against tool schema
        
        Args:
            parameters: Provided parameters
            schema: Tool parameter schema
            
        Returns:
            Validated parameters
        """
        validated = {}
        
        for param_name, param_schema in schema.items():
            value = parameters.get(param_name)
            
            # Check required
            if param_schema.get("required", True) and value is None:
                raise ValueError(f"Required parameter missing: {param_name}")
            
            # Use default if not provided
            if value is None and "default" in param_schema:
                value = param_schema["default"]
            
            # Type validation (basic)
            param_type = param_schema.get("type", "string")
            if value is not None:
                if param_type == "email" and "@" not in str(value):
                    raise ValueError(f"Invalid email: {param_name}")
                elif param_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Invalid number: {param_name}")
            
            validated[param_name] = value
        
        return validated
    
    async def _send_webhook(
        self,
        execution_id: UUID,
        webhook_url: str,
        payload: Dict[str, Any],
        db: Session
    ):
        """
        Send webhook request and wait for response
        
        Args:
            execution_id: Execution ID
            webhook_url: Webhook URL
            payload: Request payload
            db: Database session
        """
        try:
            logger.info(f"Sending webhook to {webhook_url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Get execution
                execution = db.query(ToolExecution).filter(
                    ToolExecution.id == execution_id
                ).first()
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    execution.status = "success"
                    execution.response_data = response_data
                    execution.completed_at = datetime.utcnow()
                    
                    logger.info(f"Webhook successful: {execution_id}")
                else:
                    execution.status = "failed"
                    execution.error_message = f"HTTP {response.status_code}: {response.text}"
                    execution.completed_at = datetime.utcnow()
                    
                    logger.error(f"Webhook failed: {execution.status} - {execution.error_message}")
                
                db.commit()
                
        except asyncio.TimeoutError:
            execution = db.query(ToolExecution).filter(
                ToolExecution.id == execution_id
            ).first()
            execution.status = "timeout"
            execution.error_message = "Webhook request timed out"
            execution.completed_at = datetime.utcnow()
            db.commit()
            
            logger.error(f"Webhook timeout: {execution_id}")
            
        except Exception as e:
            execution = db.query(ToolExecution).filter(
                ToolExecution.id == execution_id
            ).first()
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
            
            logger.error(f"Webhook error: {execution_id} - {str(e)}")
    
    async def wait_for_execution(
        self,
        db: Session,
        execution_id: UUID,
        timeout: int = 60
    ) -> ToolExecution:
        """
        Wait for tool execution to complete
        
        Args:
            db: Database session
            execution_id: Execution ID
            timeout: Timeout in seconds
            
        Returns:
            Completed ToolExecution
        """
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < timeout:
            execution = db.query(ToolExecution).filter(
                ToolExecution.id == execution_id
            ).first()
            
            if execution.status != "pending":
                return execution
            
            await asyncio.sleep(1)  # Check every second
        
        # Timeout
        execution = db.query(ToolExecution).filter(
            ToolExecution.id == execution_id
        ).first()
        execution.status = "timeout"
        execution.error_message = "Execution timeout"
        execution.completed_at = datetime.utcnow()
        db.commit()
        
        return execution
    
    def get_execution_status(
        self,
        db: Session,
        execution_id: UUID
    ) -> Optional[ToolExecution]:
        """Get execution status"""
        return db.query(ToolExecution).filter(
            ToolExecution.id == execution_id
        ).first()


# Global tool service instance
tool_service = ToolService()