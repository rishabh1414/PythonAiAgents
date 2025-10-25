"""
Manager Agent
Orchestrates and delegates tasks to specialist agents
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class ManagerAgent(BaseAgent):
    """Manager agent that routes tasks to specialists"""
    
    def __init__(self):
        super().__init__(
            agent_id="manager",
            name="Manager Agent",
            description="Orchestrates and delegates tasks to specialist agents"
        )
        self.capabilities = [
            "task_routing",
            "coordination",
            "decision_making",
            "delegation"
        ]
        
        # Map task types to specialist agents
        self.agent_routing = {
            "email": "email_agent",
            "social": "social_agent",
            "content": "content_agent",
            "research": "research_agent"
        }
    
    def get_capabilities(self) -> List[str]:
        """Return manager capabilities"""
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task by routing to appropriate specialist
        
        Args:
            task: Task to process
            
        Returns:
            Routing decision
        """
        task_type = task.get("task_type", "general")
        task_content = task.get("content", "")
        
        logger.info(f"Manager analyzing task type: {task_type}")
        
        # Determine best agent for the task
        if task_type in self.agent_routing:
            assigned_agent = self.agent_routing[task_type]
        else:
            # Use LLM to classify
            intent = await llm_service.classify_intent(task_content)
            assigned_agent = intent.get("agent", "content_agent")
        
        return {
            "action": "delegate",
            "assigned_agent": assigned_agent,
            "task_type": task_type,
            "reasoning": f"Task best suited for {assigned_agent}"
        }
    
    def route_task(self, task: Dict[str, Any]) -> str:
        """
        Determine which agent should handle a task
        
        Args:
            task: Task to route
            
        Returns:
            Agent ID
        """
        task_type = task.get("task_type")
        return self.agent_routing.get(task_type, "content_agent")