"""
Dynamic Agent - Created by Owner at runtime
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class DynamicAgent(BaseAgent):
    """
    Dynamic agent that can be fully customized by Owner
    All behavior comes from database configuration
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        personality: str = "Professional",
        tone: str = "professional",
        temperature: float = 0.7,
        capabilities: List[str] = None,
        allowed_tools: List[UUID] = None
    ):
        super().__init__(agent_id, name, description)
        
        self.system_prompt = system_prompt
        self.personality = personality
        self.tone = tone
        self.temperature = temperature
        self.capabilities = capabilities or []
        self.allowed_tools = allowed_tools or []
    
    def get_capabilities(self) -> List[str]:
        """Get capabilities from configuration"""
        return self.capabilities
    
    async def should_use_tool(self, task_content: str) -> Optional[Dict[str, Any]]:
        """
        Ask LLM if it should use a tool
        """
        if not self.allowed_tools:
            return None
        
        # Use LLM to decide if tool is needed
        decision_prompt = f"""
        You are {self.name}. You have access to tools.
        
        User request: {task_content}
        
        Should you use a tool to complete this request?
        
        Think about:
        - Does the user want you to ACTUALLY DO something (send email, create event, etc.)?
        - Or do they just want you to DRAFT/WRITE something?
        
        Respond ONLY with JSON:
        {{
            "use_tool": true/false,
            "tool_name": "tool name if needed",
            "reason": "brief explanation"
        }}
        """
        
        try:
            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": decision_prompt}],
                system_prompt="You are a decision-making assistant. Only respond with JSON.",
                temperature=0.3
            )
            
            import json
            decision = json.loads(response)
            
            if decision.get("use_tool"):
                return decision
                
        except Exception as e:
            logger.error(f"Tool decision error: {e}")
        
        return None
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using owner-defined configuration"""
        
        content = task.get("content", "")
        
        # Extract conversation context
        conversation_context = self.extract_conversation_context(task)
        
        logger.info(f"{self.name} is working on: {content[:100]}")
        
        # Check if we should use a tool
        tool_decision = await self.should_use_tool(content)
        
        if tool_decision and tool_decision.get("use_tool"):
            # Agent wants to use a tool
            return await self._handle_tool_usage(content, tool_decision, conversation_context)
        else:
            # Regular processing
            return await self._process_normally(content, conversation_context)
    
    async def _process_normally(self, content: str, conversation_context: str) -> Dict[str, Any]:
        """Process task normally without tools"""
        
        full_system_prompt = f"""
        {self.system_prompt}
        
        Personality: {self.personality}
        Tone: {self.tone}
        
        IMPORTANT:
        - DO NOT introduce yourself in every message
        - Be direct and helpful
        - If there's previous context, use it naturally
        
        {conversation_context if conversation_context else "This is a new conversation."}
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=full_system_prompt,
            temperature=self.temperature
        )
        
        return {
            "type": "response",
            "content": response,
            "agent": self.name,
            "specialty": self.description
        }
    
    async def _handle_tool_usage(
        self,
        content: str,
        tool_decision: Dict[str, Any],
        conversation_context: str
    ) -> Dict[str, Any]:
        """Handle tool usage request"""
        
        # Ask LLM to generate tool parameters
        tool_prompt = f"""
        {self.system_prompt}
        
        The user wants you to use the {tool_decision.get('tool_name')} tool.
        
        User request: {content}
        
        {conversation_context}
        
        Generate the parameters needed for this tool in JSON format.
        Think about what information is needed to complete the user's request.
        
        Respond ONLY with JSON parameters, nothing else.
        """
        
        try:
            import json
            
            params_response = await llm_service.generate_response(
                messages=[{"role": "user", "content": tool_prompt}],
                system_prompt="Generate tool parameters as JSON.",
                temperature=0.5
            )
            
            tool_params = json.loads(params_response)
            
            # Return tool execution request
            return {
                "type": "tool_request",
                "content": f"I'll help you with that using {tool_decision.get('tool_name')}!\n\n[TOOL:{tool_decision.get('tool_name')}:{json.dumps(tool_params)}]",
                "agent": self.name,
                "specialty": self.description,
                "tool_params": tool_params
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Fallback
            return {
                "type": "response",
                "content": f"I'd like to use the {tool_decision.get('tool_name')} tool, but I need you to configure it first in your Settings.",
                "agent": self.name,
                "specialty": self.description
            }