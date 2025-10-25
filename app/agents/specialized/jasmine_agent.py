"""
Jasmine Thompson - Email Communication Specialist with Tool Support
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class JasmineAgent(BaseAgent):
    """Jasmine - Email Communication Expert with Gmail tool integration"""
    
    def __init__(self):
        super().__init__(
            agent_id="jasmine",
            name="Jasmine Thompson",
            description="Email Communication Specialist"
        )
        self.capabilities = [
            "professional_email_writing",
            "email_replies",
            "cold_outreach",
            "follow_up_emails",
            "email_analysis",
            "gmail_sending"  # New capability
        ]
    
    def get_capabilities(self) -> List[str]:
        return self.capabilities
    
    async def should_use_tool(self, task_content: str) -> Optional[Dict[str, Any]]:
        """
        Check if Jasmine should use Gmail tool
        Looks for patterns like "send email to", "email abc@example.com"
        """
        task_lower = task_content.lower()
        
        # Check if user wants to actually SEND an email
        send_indicators = [
            "send email to",
            "send to",
            "email to",
            "send mail to",
            "mail to"
        ]
        
        if any(indicator in task_lower for indicator in send_indicators):
            # Extract email address
            import re
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, task_content)
            
            if emails:
                return {
                    "tool_name": "gmail",
                    "recipient": emails[0],
                    "action": "send"
                }
        
        return None
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process email-related tasks with tool integration"""
        
        content = task.get("content", "")
        
        # Extract conversation context
        conversation_context = self.extract_conversation_context(task)
        
        logger.info(f"Jasmine is working on: {content[:100]}")
        
        # Check if we should use a tool
        tool_info = await self.should_use_tool(content)
        
        if tool_info and tool_info.get("action") == "send":
            # User wants to SEND email - use tool
            return await self._handle_tool_request(content, tool_info, conversation_context)
        else:
            # User wants email DRAFTED - just write it
            return await self._draft_email(content, conversation_context)
    
    async def _draft_email(self, content: str, conversation_context: str) -> Dict[str, Any]:
        """Draft an email without sending"""
        
        system_prompt = f"""
        You are Jasmine Thompson, an Email Communication Specialist.
        
        CRITICAL INSTRUCTIONS:
        1. DO NOT introduce yourself - just create the content
        2. Write the complete email immediately
        3. Include: Subject line, greeting, body, closing
        4. Make it professional and ready to send
        5. If there's previous context, reference it naturally
        
        Format:
        Subject: [Subject Line]
        
        Dear [Name],
        
        [Email body]
        
        Best regards,
        [Sender name]
        
        {conversation_context if conversation_context else "This is a new conversation."}
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return {
            "type": "email_draft",
            "content": response,
            "agent": "Jasmine Thompson",
            "specialty": "Email Communication"
        }
    
    async def _handle_tool_request(
        self, 
        content: str, 
        tool_info: Dict[str, Any],
        conversation_context: str
    ) -> Dict[str, Any]:
        """Handle tool execution request"""
        
        # Generate email content first
        system_prompt = f"""
        You are Jasmine Thompson, an Email Communication Specialist.
        
        The user wants to SEND an email to {tool_info['recipient']}.
        
        Generate the email subject and body based on their request.
        
        Respond in this EXACT JSON format:
        {{
            "subject": "Email subject here",
            "body": "Email body here (can be HTML)"
        }}
        
        {conversation_context if conversation_context else ""}
        
        IMPORTANT: Only return the JSON, nothing else.
        """
        
        messages = [{"role": "user", "content": content}]
        
        response = await llm_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        try:
            import json
            email_data = json.loads(response)
            
            # Return tool execution request
            # Format: [TOOL:tool_id:params_json]
            tool_request = {
                "to": tool_info["recipient"],
                "subject": email_data.get("subject", "No Subject"),
                "body": email_data.get("body", "")
            }
            
            # This will be parsed by the chat endpoint
            return {
                "type": "tool_request",
                "content": f"I'll send that email to {tool_info['recipient']} right away!\n\n[TOOL:gmail:{json.dumps(tool_request)}]",
                "agent": "Jasmine Thompson",
                "specialty": "Email Communication",
                "tool_params": tool_request
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "type": "email_draft",
                "content": f"I can help you email {tool_info['recipient']}! However, you need to configure your Gmail tool first. Go to Settings → Tools and add your webhook URL.",
                "agent": "Jasmine Thompson",
                "specialty": "Email Communication"
            }