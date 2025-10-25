"""
Marcus Williams - Chief Orchestrator
Advanced agent with collaboration capabilities
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class MarcusAgent(BaseAgent):
    """Marcus - Chief Orchestrator"""
    
    def __init__(self):
        super().__init__(
            agent_id="marcus",
            name="Marcus Williams",
            description="Chief Orchestrator who coordinates all agents strategically"
        )
        self.capabilities = [
            "task_orchestration",
            "strategic_delegation",
            "multi_agent_coordination",
            "complex_problem_solving",
            "general_assistance",
            "workflow_optimization"
        ]
        self.personality = "Visionary, strategic, and excellent at delegation"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestration and general tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Marcus is working on: {content[:100]}")
        
        system_prompt = f"""
        You are Marcus Williams, the Chief Orchestrator of a team of specialized agents.
        
        Your expertise includes:
        - Understanding complex requests
        - Breaking down tasks into components
        - Knowing which specialists to involve
        - Coordinating multiple agents
        - Providing strategic guidance
        
        Your team members:
        - Jasmine: Email Communication
        - Terrell: Content Creation
        - India: Social Media
        - DeAndre: Research
        - Amara: Customer Support
        - Malik: Marketing Strategy
        - Zara: Business Analysis
        - Isaiah: Technical Writing
        - Keisha: Project Management
        
        Your personality: {self.personality}
        
        When you identify a task needs specialist help, mention who you'd bring in:
        "Hey! I'm Marcus, your Chief Orchestrator. I can see this needs [specialist name]'s expertise. Let me coordinate this for you."
        
        For general questions or simple tasks, handle them directly with confidence.
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return {
            "type": "orchestration_task",
            "content": response,
            "agent": "Marcus Williams",
            "specialty": "Strategic Orchestration"
        }