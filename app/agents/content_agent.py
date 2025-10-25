"""
Content Agent
Specialist agent for content creation
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class ContentAgent(BaseAgent):
    """Specialist agent for content creation"""
    
    def __init__(self):
        super().__init__(
            agent_id="content_agent",
            name="Content Creator",
            description="Generates various types of content"
        )
        self.capabilities = [
            "article_writing",
            "copywriting",
            "blog_posts",
            "editing",
            "summarization"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return content agent capabilities"""
        return self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content creation task
        
        Args:
            task: Content task to process
            
        Returns:
            Generated content
        """
        task_description = task.get("description", "")
        task_data = task.get("data", {})
        
        logger.info(f"Content agent processing: {task_description}")
        
        # Determine content type
        if "article" in task_description.lower():
            result = await self._write_article(task_data)
        elif "blog" in task_description.lower():
            result = await self._write_blog_post(task_data)
        elif "copy" in task_description.lower():
            result = await self._write_copy(task_data)
        else:
            result = await self._general_content(task_data)
        
        return result
    
    async def _write_article(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Write an article"""
        prompt = f"""
        Write a comprehensive article about: {data.get('topic', 'General topic')}
        
        Target audience: {data.get('audience', 'General readers')}
        Tone: {data.get('tone', 'informative')}
        Length: {data.get('length', '500-700')} words
        Key points to cover: {data.get('key_points', [])}
        
        Include an engaging introduction, well-structured body, and conclusion.
        """
        
        article = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert article writer.",
            max_tokens=2000
        )
        
        return {
            "type": "article",
            "title": data.get('topic', 'Article'),
            "content": article,
            "word_count": len(article.split())
        }
    
    async def _write_blog_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Write a blog post"""
        prompt = f"""
        Write an engaging blog post about: {data.get('topic', 'Blog topic')}
        
        Style: {data.get('style', 'conversational')}
        Include: {data.get('include', 'personal insights and examples')}
        """
        
        blog_content = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert blog writer with a conversational style.",
            max_tokens=1500
        )
        
        return {
            "type": "blog_post",
            "title": data.get('topic', 'Blog Post'),
            "content": blog_content
        }
    
    async def _write_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Write marketing copy"""
        prompt = f"""
        Write compelling marketing copy for: {data.get('product', 'Product/Service')}
        
        Target audience: {data.get('audience', 'General consumers')}
        Goal: {data.get('goal', 'Generate interest')}
        Tone: {data.get('tone', 'persuasive')}
        Length: {data.get('length', 'short')}
        """
        
        copy = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert copywriter.",
            max_tokens=500
        )
        
        return {
            "type": "marketing_copy",
            "copy": copy
        }
    
    async def _general_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general content"""
        prompt = data.get('prompt', 'Write helpful content')
        
        content = await llm_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a versatile content creator."
        )
        
        return {
            "type": "general_content",
            "content": content
        }