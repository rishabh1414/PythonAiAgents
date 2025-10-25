"""
Base Agent Class - Updated with Tool Support
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from app.utils.logger import logger


class BaseAgent(ABC):
    """Base class for all agents with tool support"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = "idle"
        self.current_task = None
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.memory = []
        self.allowed_tools = []  # List of tool IDs this agent can use
        
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - must be implemented by subclasses"""
        pass
    
    def set_allowed_tools(self, tool_ids: List[UUID]):
        """Set which tools this agent can use"""
        self.allowed_tools = tool_ids
    
    def can_use_tool(self, tool_id: UUID) -> bool:
        """Check if agent can use a specific tool"""
        return tool_id in self.allowed_tools
    
    def add_to_memory(self, interaction: Dict[str, Any]):
        """Add interaction to agent's memory"""
        self.memory.append({
            "timestamp": datetime.utcnow(),
            "data": interaction
        })
        # Keep only last 20 interactions
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]
    
    def get_recent_memory(self, count: int = 5) -> List[Dict]:
        """Get recent memory items"""
        return self.memory[-count:] if self.memory else []
    
    def extract_conversation_context(self, task_data: Dict[str, Any]) -> str:
        """Extract and format conversation context from task data"""
        context = task_data.get("data", {})
        history = context.get("conversation_history", [])
        
        if not history or len(history) < 2:
            return ""
        
        # Format recent conversation
        context_text = "\n[Previous conversation context]:\n"
        for msg in history[-5:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:150] + "..." if len(msg["content"]) > 150 else msg["content"]
            context_text += f"{role}: {content}\n"
        context_text += "[End of context]\n\n"
        
        return context_text
    
    async def should_use_tool(self, task_content: str) -> Optional[Dict[str, Any]]:
        """
        Determine if agent should use a tool for this task
        Returns tool info if tool should be used, None otherwise
        """
        # This will be overridden by specific agents that use tools
        return None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with error handling and status management"""
        
        task_id = task.get("task_id", "unknown")
        self.status = "busy"
        self.current_task = task_id
        
        logger.info(f"Agent {self.name} starting task {task_id}")
        
        try:
            # Add conversation context to memory
            self.add_to_memory({
                "type": "task_start",
                "task_id": task_id,
                "content": task.get("content", "")[:100]
            })
            
            # Process the task
            result = await self.process_task(task)
            
            # Update status
            self.tasks_completed += 1
            self.status = "idle"
            self.current_task = None
            
            # Remember the result
            self.add_to_memory({
                "type": "task_complete",
                "task_id": task_id,
                "result": str(result)[:200]
            })
            
            logger.info(f"Agent {self.name} completed task successfully")
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "result": result
            }
            
        except Exception as e:
            self.tasks_failed += 1
            self.status = "idle"
            self.current_task = None
            
            logger.error(f"Agent {self.name} failed task: {str(e)}")
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "current_task": self.current_task,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "memory_items": len(self.memory),
            "allowed_tools": len(self.allowed_tools)
        }
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        pass