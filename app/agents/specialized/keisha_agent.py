"""
Keisha Taylor - Project Manager
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class KeishaAgent(BaseAgent):
    """Keisha - Project Manager"""
    
    def __init__(self):
        super().__init__(
            agent_id="keisha",
            name="Keisha Taylor",
            description="Project Manager who keeps everything organized and on track"
        )
        self.capabilities = [
            "project_planning",
            "timeline_management",
            "resource_allocation",
            "risk_management",
            "stakeholder_communication",
            "milestone_tracking"
        ]
        self.personality = "Organized, efficient, and proactive"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process project management tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Keisha is working on: {content[:100]}")
        
        system_prompt = f"""
        You are Keisha Taylor, a Project Manager who excels at organization.
        
        Your expertise includes:
        - Creating detailed project plans
        - Managing timelines and deadlines
        - Coordinating team members
        - Tracking progress and milestones
        - Risk identification and mitigation
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "Hi! I'm Keisha, your Project Manager. Let's get this organized and moving forward! 📋"
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.6
        )
        
        return {
            "type": "project_task",
            "content": response,
            "agent": "Keisha Taylor",
            "specialty": "Project Management"
        }