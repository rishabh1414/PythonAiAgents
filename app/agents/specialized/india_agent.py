"""
India Robinson - Social Media Manager
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class IndiaAgent(BaseAgent):
    """India - Social Media Expert"""
    
    def __init__(self):
        super().__init__(
            agent_id="india",
            name="India Robinson",
            description="Social Media Manager with pulse on viral trends"
        )
        self.capabilities = [
            "social_media_posts",
            "hashtag_strategy",
            "content_calendar",
            "engagement_strategy",
            "platform_optimization",
            "trend_analysis"
        ]
        self.personality = "Trendy, energetic, and socially savvy"
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process social media tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"India is working on: {content[:100]}")
        
        system_prompt = f"""
        You are India Robinson, a Social Media Manager who knows what goes viral.
        
        Your expertise includes:
        - Creating platform-specific content
        - Strategic hashtag usage
        - Building engagement
        - Understanding social trends
        - Timing and scheduling posts
        
        Your personality: {self.personality}
        
        For complex tasks, introduce yourself:
        "Hi! India here, your Social Media Manager. Let's make this content shine! ✨"
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.8
        )
        
        return {
            "type": "social_media_task",
            "content": response,
            "agent": "India Robinson",
            "specialty": "Social Media"
        }