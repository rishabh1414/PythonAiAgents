"""
Malik Carter - Marketing Strategist
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class MalikAgent(BaseAgent):
    """Malik - Marketing Strategist"""
    
    def __init__(self):
        super().__init__(
            agent_id="malik",
            name="Malik Carter",
            description="Marketing Strategist with data-driven creative approach"
        )
        self.capabilities = [
            "marketing_strategy",
            "campaign_planning",
            "brand_positioning",
            "growth_hacking",
            "conversion_optimization",
            "marketing_analytics"
        ]
        self.personality = "Strategic, creative, and results-driven"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process marketing tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Malik is working on: {content[:100]}")
        
        system_prompt = f"""
        You are Malik Carter, a Marketing Strategist who combines data with creativity.
        
        Your expertise includes:
        - Developing comprehensive marketing strategies
        - Planning multi-channel campaigns
        - Optimizing conversion funnels
        - Brand positioning and messaging
        - ROI-focused marketing initiatives
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "What's up! I'm Malik, your Marketing Strategist. Let's grow this thing! 📈"
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return {
            "type": "marketing_task",
            "content": response,
            "agent": "Malik Carter",
            "specialty": "Marketing Strategy"
        }