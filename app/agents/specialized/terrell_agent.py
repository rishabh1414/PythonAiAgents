"""
Terrell Johnson - Content Creation Expert
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class TerrellAgent(BaseAgent):
    """Terrell - Content Creation Expert"""
    
    def __init__(self):
        super().__init__(
            agent_id="terrell",
            name="Terrell Johnson",
            description="Content Creation Expert"
        )
        self.capabilities = ["article_writing", "blog_posts", "creative_writing"]
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process content creation tasks"""
        
        content = task.get("content", "")
        
        logger.info(f"Terrell is working on: {content[:100]}")
        
        system_prompt = """
        You are Terrell Johnson, a Content Creation Expert.
        
        CRITICAL INSTRUCTIONS:
        1. DO NOT introduce yourself - just create the content
        2. Write in a clean, professional format
        3. Use proper structure with headers when appropriate
        4. Be direct and deliver the content immediately
        5. No meta-commentary about what you're doing
        
        For blog posts/articles:
        - Start with an engaging title
        - Use clear sections with headers (use ## for headers)
        - Write naturally and engagingly
        - End with a strong conclusion
        
        Just write the content - nothing else.
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.8
        )
        
        return {
            "type": "content_task",
            "content": response,
            "agent": "Terrell Johnson",
            "specialty": "Content Creation"
        }