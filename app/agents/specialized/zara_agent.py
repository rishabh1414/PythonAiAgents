"""
Zara Jackson - Business Analyst
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class ZaraAgent(BaseAgent):
    """Zara - Business Analyst"""
    
    def __init__(self):
        super().__init__(
            agent_id="zara",
            name="Zara Jackson",
            description="Business Analyst with sharp strategic insights"
        )
        self.capabilities = [
            "business_analysis",
            "financial_modeling",
            "process_optimization",
            "strategic_planning",
            "kpi_tracking",
            "market_analysis"
        ]
        self.personality = "Sharp, strategic, and business-savvy"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process business analysis tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Zara is working on: {content[:100]}")
        
        system_prompt = f"""
        You are Zara Jackson, a Business Analyst with exceptional strategic acumen.
        
        Your expertise includes:
        - Analyzing business performance and metrics
        - Creating financial models and projections
        - Optimizing business processes
        - Strategic planning and recommendations
        - Competitive analysis
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "Hello! I'm Zara, your Business Analyst. Let's dive into the numbers and strategy."
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.6
        )
        
        return {
            "type": "business_task",
            "content": response,
            "agent": "Zara Jackson",
            "specialty": "Business Analysis"
        }