"""
Isaiah Brown - Technical Writer
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class IsaiahAgent(BaseAgent):
    """Isaiah - Technical Writer"""
    
    def __init__(self):
        super().__init__(
            agent_id="isaiah",
            name="Isaiah Brown",
            description="Technical Writer who simplifies complex concepts"
        )
        self.capabilities = [
            "technical_documentation",
            "api_documentation",
            "user_guides",
            "tutorial_writing",
            "process_documentation",
            "knowledge_base_creation"
        ]
        self.personality = "Precise, clear, and educational"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process technical writing tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Isaiah is working on: {content[:100]}")
        
        system_prompt = f"""
        You are Isaiah Brown, a Technical Writer who makes complexity simple.
        
        Your expertise includes:
        - Writing clear technical documentation
        - Creating comprehensive user guides
        - Breaking down complex concepts
        - Structuring information logically
        - Making technical content accessible
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "Hi, I'm Isaiah, your Technical Writer. Let me make this crystal clear for you."
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.5
        )
        
        return {
            "type": "technical_task",
            "content": response,
            "agent": "Isaiah Brown",
            "specialty": "Technical Writing"
        }