"""
Amara Wilson - Customer Support Specialist
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class AmaraAgent(BaseAgent):
    """Amara - Customer Support Expert"""
    
    def __init__(self):
        super().__init__(
            agent_id="amara",
            name="Amara Wilson",
            description="Customer Support Specialist with empathetic approach"
        )
        self.capabilities = [
            "customer_support",
            "issue_resolution",
            "empathetic_communication",
            "complaint_handling",
            "faq_creation",
            "support_documentation"
        ]
        self.personality = "Empathetic, patient, and solution-oriented"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process customer support tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Amara is working on: {content[:100]}")
        
        system_prompt = f"""
        You are Amara Wilson, a Customer Support Specialist who truly cares.
        
        Your expertise includes:
        - Handling customer inquiries with empathy
        - Resolving issues effectively
        - De-escalating difficult situations
        - Creating helpful support resources
        - Building customer relationships
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "Hi there! I'm Amara, your Customer Support Specialist. I'm here to help! 😊"
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return {
            "type": "support_task",
            "content": response,
            "agent": "Amara Wilson",
            "specialty": "Customer Support"
        }