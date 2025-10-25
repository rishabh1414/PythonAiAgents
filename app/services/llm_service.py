"""
LLM Service
Handles interactions with OpenAI and other LLM providers
"""
from typing import List, Dict, Any, Optional
import openai
from app.core.config import settings
from app.utils.logger import logger

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY


class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.model = "gpt-4-turbo-preview"
        self.temperature = 0.7
        self.max_tokens = 2000
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
        
        Returns:
            Generated response text
        """
        try:
            # Prepare messages
            formatted_messages = []
            
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            formatted_messages.extend(messages)
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            # Extract response
            result = response.choices[0].message.content
            
            logger.info(f"LLM generated response: {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise Exception(f"Failed to generate LLM response: {str(e)}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def classify_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Classify user intent and determine which agent should handle it
        
        Args:
            user_message: User's message
        
        Returns:
            Dictionary with intent and recommended agent
        """
        system_prompt = """
        You are an intent classifier. Analyze the user's message and determine:
        1. The main intent (email, social_media, content_creation, research, general_chat)
        2. The best agent to handle this request
        3. Confidence level (0-1)
        
        Respond in JSON format:
        {
            "intent": "intent_name",
            "agent": "agent_id",
            "confidence": 0.95,
            "reasoning": "brief explanation"
        }
        """
        
        try:
            messages = [{"role": "user", "content": user_message}]
            response = await self.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            # Return default if classification fails
            return {
                "intent": "general_chat",
                "agent": "manager",
                "confidence": 0.5,
                "reasoning": "Classification failed, defaulting to manager"
            }


# Create global instance
llm_service = LLMService()