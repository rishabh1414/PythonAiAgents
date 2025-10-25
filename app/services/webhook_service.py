"""
Webhook Service for Make.com Integration
"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings
from app.utils.logger import logger


class WebhookService:
    """Service for handling webhook interactions"""
    
    def __init__(self):
        self.webhook_url = None  # Will be set per user/tool
        self.timeout = 30
    
    async def send_webhook(
        self,
        url: str,
        data: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send data to webhook URL
        
        Args:
            url: Webhook URL
            data: Data to send
            timeout: Request timeout in seconds
            
        Returns:
            Response data
        """
        timeout = timeout or self.timeout
        
        try:
            logger.info(f"Sending webhook to {url}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Webhook successful: {url}")
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": response.json() if response.text else {}
                    }
                else:
                    logger.error(f"Webhook failed: {response.status_code}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text
                    }
                    
        except asyncio.TimeoutError:
            logger.error(f"Webhook timeout: {url}")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_task_with_webhook(
        self,
        task_data: Dict[str, Any],
        webhook_url: str
    ) -> Dict[str, Any]:
        """
        Process a task by sending it to webhook
        
        Args:
            task_data: Task information
            webhook_url: URL to send task to
            
        Returns:
            Processing result
        """
        logger.info(f"Processing task via webhook: {task_data.get('task_id')}")
        
        # Prepare webhook payload
        payload = {
            "task_id": task_data.get("task_id"),
            "task_type": task_data.get("task_type"),
            "content": task_data.get("content"),
            "user_id": task_data.get("user_id"),
            "timestamp": task_data.get("timestamp")
        }
        
        # Send to webhook
        result = await self.send_webhook(webhook_url, payload)
        
        return result
    
    async def wait_for_webhook_response(
        self,
        task_id: str,
        timeout: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for webhook response
        
        Args:
            task_id: Task ID to wait for
            timeout: Timeout in seconds
            
        Returns:
            Response data if received, None if timeout
        """
        # This would be implemented with a queue or database polling
        # For now, it's a placeholder
        logger.info(f"Waiting for webhook response: {task_id}")
        
        await asyncio.sleep(1)  # Simulate waiting
        
        return None


# Global webhook service instance
webhook_service = WebhookService()