"""
Agent Registry - Loads agents dynamically from database
NO PRE-BUILT AGENTS
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.agents.base import BaseAgent
from app.agents.dynamic_agent import DynamicAgent
from app.agents.collaboration import AgentCollaboration
from app.models.agent_config import AgentConfig
from app.utils.logger import logger


class AgentRegistry:
    """Central registry for dynamically loaded agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.collaboration: Optional[AgentCollaboration] = None
    
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Remove an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents"""
        return self.agents
    
    def load_agents_from_db(self, db: Session):
        """
        Load all active agents from database
        This is the ONLY way agents are created
        """
        try:
            # Clear existing agents
            self.agents.clear()
            
            # Load agent configurations from database
            configs = db.query(AgentConfig).filter(
                AgentConfig.is_active == True
            ).order_by(AgentConfig.display_order).all()
            
            logger.info(f"Loading {len(configs)} agents from database...")
            
            for config in configs:
                # Create dynamic agent from config
                agent = DynamicAgent(
                    agent_id=config.agent_id,
                    name=config.display_name or config.name,
                    description=config.description or "",
                    system_prompt=config.system_prompt,
                    personality=config.personality or "Professional",
                    tone=config.tone,
                    temperature=config.temperature,
                    capabilities=config.capabilities or [],
                    allowed_tools=config.allowed_tools or []
                )
                
                self.register_agent(agent)
            
            # Initialize collaboration system
            if self.agents:
                self.collaboration = AgentCollaboration(self.agents)
                logger.info(f"✓ Loaded {len(self.agents)} agents with collaboration")
            else:
                logger.warning("⚠️ No agents loaded from database")
            
        except Exception as e:
            logger.error(f"Error loading agents from database: {e}")
    
    def reload_agent(self, db: Session, agent_id: str):
        """Reload a specific agent from database"""
        try:
            config = db.query(AgentConfig).filter(
                AgentConfig.agent_id == agent_id
            ).first()
            
            if not config:
                # Agent was deleted, remove it
                self.unregister_agent(agent_id)
                return
            
            # Create/update agent
            agent = DynamicAgent(
                agent_id=config.agent_id,
                name=config.display_name or config.name,
                description=config.description or "",
                system_prompt=config.system_prompt,
                personality=config.personality or "Professional",
                tone=config.tone,
                temperature=config.temperature,
                capabilities=config.capabilities or [],
                allowed_tools=config.allowed_tools or []
            )
            
            self.register_agent(agent)
            
            # Update collaboration
            if self.agents:
                self.collaboration = AgentCollaboration(self.agents)
            
            logger.info(f"✓ Reloaded agent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Error reloading agent {agent_id}: {e}")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get status of specific agent"""
        agent = self.get_agent(agent_id)
        return agent.get_status() if agent else None
    
    def get_all_statuses(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    async def route_task(self, user_query: str, context: Dict = None):
        """
        Route task to appropriate agent(s)
        """
        if not self.agents:
            return {
                "error": "No agents available. Please ask the owner to create agents."
            }
        
        # If only one agent, use it
        if len(self.agents) == 1:
            agent = list(self.agents.values())[0]
            return await agent.execute({
                "task_id": "direct-task",
                "content": user_query,
                "task_type": "general",
                "data": context or {}
            })
        
        # Use collaboration system
        if self.collaboration:
            # Get first agent as primary
            primary_agent_id = list(self.agents.keys())[0]
            
            result = await self.collaboration.coordinate_agents(
                task=user_query,
                primary_agent_id=primary_agent_id,
                context=context
            )
            return result
        
        # Fallback
        agent = list(self.agents.values())[0]
        return await agent.execute({
            "task_id": "direct-task",
            "content": user_query,
            "task_type": "general",
            "data": context or {}
        })


# Create global registry instance
agent_registry = AgentRegistry()