"""
Email Agent
Specialist agent for email-related tasks
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class EmailAgent(BaseAgent):
    """Specialist agent for email tasks"""
    
    def __init__(self):
        super().__init__(
            agent_id="email_agent",
            name="Email Specialist",
            description="Handles email composition and management"
        )
        self.capabilities = [
            "email_writing",
            "email_analysis",
            "response_drafting",
            "tone_adjustment",
            "scheduling"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return email agent capabilities"""
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email-related task
        
        Args:
            task: Email task to process
            
        Returns:
            Email draft or analysis
        """
        task_description = task.get("description", "")
        task_data = task.get("data", {})
        
        logger.info(f"Email agent processing: {task_description}")
        
        # Determine email task type
        if "reply" in task_description.lower():
            result = await self._draft_reply(task_data)
        elif "compose" in task_description.lower() or "write" in task_description.lower():
            result = await self._compose_email(task_data)
        elif "analyze" in task_description.lower():
            result = await self._analyze_email(task_data)
        else:
            result = await self._compose_email(task_data)
        
        return result
    
    async def _compose_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a new email"""
        prompt = f"""
        Compose a professional email with the following details:
        Topic: {data.get('topic', 'General inquiry')}
        Recipient: {data.get('recipient', 'Recipient')}
        Tone: {data.get('tone', 'professional')}
        Key points: {data.get('key_points', [])}
        
        Write a clear, concise, and professional email.
        """
        
        email_content = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert email writer."
        )
        
        return {
            "type": "email_draft",
            "subject": data.get('topic', 'Email'),
            "body": email_content,
            "tone": data.get('tone', 'professional')
        }
    
    async def _draft_reply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Draft a reply to an email"""
        original_email = data.get('original_email', '')
        
        prompt = f"""
        Draft a professional reply to this email:
        
        {original_email}
        
        Tone: {data.get('tone', 'professional')}
        Key points to address: {data.get('points_to_address', [])}
        """
        
        reply_content = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert at crafting email replies."
        )
        
        return {
            "type": "email_reply",
            "reply": reply_content
        }
    
    async def _analyze_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an email"""
        email_content = data.get('email_content', '')
        
        prompt = f"""
        Analyze this email and provide:
        1. Main intent
        2. Tone
        3. Key action items
        4. Urgency level
        
        Email:
        {email_content}
        """
        
        analysis = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert at email analysis."
        )
        
        return {
            "type": "email_analysis",
            "analysis": analysis
        }