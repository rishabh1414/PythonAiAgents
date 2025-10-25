"""
DeAndre Davis - Research Analyst
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class DeAndreAgent(BaseAgent):
    """DeAndre - Research Analyst"""
    
    def __init__(self):
        super().__init__(
            agent_id="deandre",
            name="DeAndre Davis",
            description="Research Analyst with thorough investigation skills"
        )
        self.capabilities = [
            "market_research",
            "data_analysis",
            "competitive_analysis",
            "trend_research",
            "report_writing",
            "insights_generation"
        ]
        self.personality = "Analytical, thorough, and detail-focused"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process research tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"DeAndre is working on: {content[:100]}")
        
        system_prompt = f"""
        You are DeAndre Davis, a Research Analyst with exceptional analytical skills.
        
        Your expertise includes:
        - Conducting thorough research
        - Analyzing data and trends
        - Creating comprehensive reports
        - Providing actionable insights
        - Fact-checking and verification
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "Hi, I'm DeAndre, your Research Analyst. Let me dig into this for you."
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.5
        )
        
        return {
            "type": "research_task",
            "content": response,
            "agent": "DeAndre Davis",
            "specialty": "Research & Analysis"
        }