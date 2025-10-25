"""
Agent Collaboration System
Enables agents to work together on complex tasks with conversation memory
"""
from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent
from app.services.llm_service import llm_service
from app.utils.logger import logger


class AgentCollaboration:
    """Manages collaboration between multiple agents with conversation context"""
    
    def __init__(self, agents: Dict[str, BaseAgent]):
        self.agents = agents
        self.conversation_history = []
        
    async def coordinate_agents(
        self,
        task: str,
        primary_agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents to complete a complex task with conversation memory
        
        Args:
            task: The task to complete
            primary_agent_id: Initial agent to handle the task
            context: Additional context including conversation history
            
        Returns:
            Combined result from all agents
        """
        logger.info(f"Starting agent collaboration for task with {primary_agent_id}")
        
        # Build conversation context
        conversation_history = context.get("conversation_history", []) if context else []
        context_summary = self._build_context_summary(conversation_history)
        
        # Enhanced task with context
        enhanced_task = f"{context_summary}\n\nCurrent request: {task}"
        
        # Start with primary agent
        primary_agent = self.agents.get(primary_agent_id)
        if not primary_agent:
            return {"error": f"Agent {primary_agent_id} not found"}
        
        # Analyze if task needs multiple agents
        needs_collaboration = await self._analyze_collaboration_need(task)
        
        if not needs_collaboration["needs_help"]:
            # Single agent can handle it - route to specialist if needed
            specialist = self._route_to_specialist(task)
            if specialist and specialist != primary_agent_id:
                logger.info(f"Routing to specialist: {specialist}")
                specialist_agent = self.agents.get(specialist)
                if specialist_agent:
                    result = await specialist_agent.execute({
                        "task_id": "specialist-task",
                        "content": enhanced_task,  # Pass context
                        "task_type": "direct",
                        "data": context or {}
                    })
                    return result
            
            # Use primary agent
            result = await primary_agent.execute({
                "task_id": "single-task",
                "content": enhanced_task,  # Pass context
                "task_type": "general",
                "data": context or {}
            })
            return result
        
        # Multi-agent collaboration needed
        return await self._execute_collaboration(
            task=enhanced_task,  # Pass enhanced task with context
            primary_agent=primary_agent,
            required_agents=needs_collaboration["required_agents"],
            context=context
        )
    
    def _build_context_summary(self, conversation_history: List[Dict]) -> str:
        """
        Build a summary of conversation history for agents
        
        Args:
            conversation_history: List of previous messages
            
        Returns:
            Formatted context summary
        """
        if not conversation_history or len(conversation_history) < 2:
            return "[Context: This is the start of a new conversation]"
        
        # Format the conversation history
        history_text = "\n=== Previous Conversation Context ===\n"
        
        # Get last 5 messages for context (or all if less than 5)
        recent_messages = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            
            # Truncate very long messages
            if len(content) > 150:
                content = content[:150] + "..."
            
            history_text += f"{role}: {content}\n"
        
        history_text += "=== End of Context ===\n"
        
        return history_text
    
    def _route_to_specialist(self, task: str) -> Optional[str]:
        """
        Route task to appropriate specialist based on keywords
        
        Args:
            task: Task description
            
        Returns:
            Agent ID of specialist or None
        """
        task_lower = task.lower()
        
        # Direct routing based on keywords (priority order)
        if any(word in task_lower for word in ['email', 'mail', 'message', 'letter', 'correspondence', 'send to']):
            return 'jasmine'
        elif any(word in task_lower for word in ['article', 'blog', 'content', 'write', 'post', 'story', 'essay']):
            # Check if it's not an email
            if 'email' not in task_lower and 'mail' not in task_lower:
                return 'terrell'
        elif any(word in task_lower for word in ['social media', 'twitter', 'facebook', 'instagram', 'linkedin', 'tweet', 'post on', 'social post']):
            return 'india'
        elif any(word in task_lower for word in ['research', 'analyze', 'investigate', 'study', 'data', 'market', 'find out', 'look into']):
            return 'deandre'
        elif any(word in task_lower for word in ['support', 'customer service', 'help desk', 'customer', 'complaint', 'issue']):
            return 'amara'
        elif any(word in task_lower for word in ['marketing', 'campaign', 'strategy', 'promote', 'advertising', 'market', 'seo']):
            return 'malik'
        elif any(word in task_lower for word in ['business', 'financial', 'metrics', 'kpi', 'analysis', 'revenue', 'profit']):
            return 'zara'
        elif any(word in task_lower for word in ['technical', 'documentation', 'guide', 'manual', 'api', 'tutorial', 'how-to']):
            return 'isaiah'
        elif any(word in task_lower for word in ['project', 'plan', 'schedule', 'timeline', 'milestone', 'task', 'organize']):
            return 'keisha'
        
        return None
    
    async def _analyze_collaboration_need(self, task: str) -> Dict[str, Any]:
        """
        Analyze if task requires multiple agents using keyword detection
        
        Args:
            task: Task description
            
        Returns:
            Analysis result with required agents
        """
        task_lower = task.lower()
        
        needs_multiple = False
        required_agents = []
        
        # Check for multiple task types
        if any(word in task_lower for word in ['email', 'mail', 'message', 'letter']):
            required_agents.append('email')
        
        if any(word in task_lower for word in ['article', 'blog', 'content', 'write', 'post']):
            # Avoid duplication with email
            if 'email' not in required_agents:
                required_agents.append('content')
        
        if any(word in task_lower for word in ['social media', 'twitter', 'facebook', 'instagram', 'linkedin', 'social post']):
            required_agents.append('social_media')
        
        if any(word in task_lower for word in ['research', 'analyze', 'investigate', 'study', 'data']):
            required_agents.append('research')
        
        if any(word in task_lower for word in ['marketing', 'campaign', 'strategy', 'promote', 'advertising']):
            required_agents.append('marketing')
        
        if any(word in task_lower for word in ['support', 'help customer', 'customer service', 'complaint']):
            required_agents.append('customer_support')
        
        if any(word in task_lower for word in ['business', 'analysis', 'financial', 'metrics', 'kpi']):
            required_agents.append('business')
        
        if any(word in task_lower for word in ['technical', 'documentation', 'guide', 'manual', 'api']):
            required_agents.append('technical')
        
        if any(word in task_lower for word in ['project', 'plan', 'schedule', 'timeline', 'organize']):
            required_agents.append('management')
        
        # Check for explicit multi-task requests
        multi_indicators = [
            'and', 'also', 'plus', 'along with', 'as well as', 
            'both', 'together with', 'combined with', 'including'
        ]
        has_multi_indicator = any(indicator in task_lower for indicator in multi_indicators)
        
        # Need collaboration if:
        # 1. More than one specialty detected AND
        # 2. Multi-indicator present OR very complex request
        needs_multiple = len(required_agents) > 1 and (
            has_multi_indicator or 
            len(required_agents) > 2
        )
        
        logger.info(f"Collaboration analysis: needs_multiple={needs_multiple}, agents={required_agents}")
        
        return {
            "needs_help": needs_multiple,
            "complexity": "complex" if needs_multiple else "simple",
            "required_agents": required_agents,
            "reasoning": f"Detected {len(required_agents)} specialties with multi-task indicators"
        }
    
    async def _execute_collaboration(
        self,
        task: str,
        primary_agent: BaseAgent,
        required_agents: List[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute multi-agent collaboration
        
        Args:
            task: Task to complete (with context)
            primary_agent: Primary agent
            required_agents: List of required agent specialties
            context: Additional context including conversation history
            
        Returns:
            Combined result from all agents
        """
        collaboration_results = []
        
        # Map specialties to agent IDs
        from app.agents.agent_names import AGENT_SPECIALIZATIONS
        
        logger.info(f"Executing collaboration with specialties: {required_agents}")
        
        # Get all required specialist agents
        agents_to_use = []
        for specialty in required_agents:
            agent_ids = AGENT_SPECIALIZATIONS.get(specialty, [])
            if agent_ids:
                agent_id = agent_ids[0]  # Get first available agent for specialty
                agent = self.agents.get(agent_id)
                if agent and agent not in agents_to_use:
                    agents_to_use.append(agent)
        
        # If no specialists found, use primary
        if not agents_to_use:
            logger.warning("No specialists found, using primary agent")
            agents_to_use = [primary_agent]
        
        # Execute tasks with each specialist
        for agent in agents_to_use:
            logger.info(f"🤝 {agent.name} is contributing their expertise")
            
            # Customize task for each specialist
            specialized_task = self._customize_task_for_agent(task, agent.agent_id)
            
            try:
                result = await agent.execute({
                    "task_id": f"collab-{agent.agent_id}",
                    "content": specialized_task,
                    "task_type": agent.agent_id,
                    "data": context or {}
                })
                
                if result.get("success"):
                    contribution = result.get("result", {}).get("content", "")
                    
                    collaboration_results.append({
                        "agent": agent.name,
                        "agent_id": agent.agent_id,
                        "contribution": contribution
                    })
                    
                    logger.info(f"✓ {agent.name} completed their part")
                else:
                    logger.error(f"✗ {agent.name} failed: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error with {agent.name}: {str(e)}")
                continue
        
        # Check if we got any results
        if not collaboration_results:
            logger.error("No collaboration results obtained")
            return {
                "success": False,
                "error": "All agents failed to complete their tasks"
            }
        
        # Synthesize all contributions
        final_result = await self._synthesize_results(task, collaboration_results)
        
        return {
            "success": True,
            "collaboration": True,
            "agents_involved": [r["agent"] for r in collaboration_results],
            "individual_contributions": collaboration_results,
            "final_result": final_result
        }
    
    def _customize_task_for_agent(self, task: str, agent_id: str) -> str:
        """
        Customize task description for specific agent to focus on their specialty
        
        Args:
            task: Original task (including context)
            agent_id: Agent identifier
            
        Returns:
            Customized task description
        """
        # Extract just the current request (after context)
        if "Current request:" in task:
            parts = task.split("Current request:")
            context_part = parts[0]
            request_part = parts[1].strip() if len(parts) > 1 else task
        else:
            context_part = ""
            request_part = task
        
        task_lower = request_part.lower()
        
        # Customize based on agent specialty
        if agent_id == 'jasmine':
            # Extract email-specific requirements
            customized = f"{context_part}\n\nYour task: Focus on the email writing aspect.\n{request_part}"
            return customized
        
        elif agent_id == 'terrell':
            # Extract content creation requirements
            customized = f"{context_part}\n\nYour task: Focus on creating engaging written content.\n{request_part}"
            return customized
        
        elif agent_id == 'india':
            # Extract social media requirements
            customized = f"{context_part}\n\nYour task: Focus on social media content and strategy.\n{request_part}"
            return customized
        
        elif agent_id == 'deandre':
            # Extract research requirements
            customized = f"{context_part}\n\nYour task: Focus on research and data analysis.\n{request_part}"
            return customized
        
        elif agent_id == 'malik':
            # Extract marketing requirements
            customized = f"{context_part}\n\nYour task: Focus on marketing strategy and campaigns.\n{request_part}"
            return customized
        
        elif agent_id == 'amara':
            # Extract customer support requirements
            customized = f"{context_part}\n\nYour task: Focus on customer support and service.\n{request_part}"
            return customized
        
        elif agent_id == 'zara':
            # Extract business analysis requirements
            customized = f"{context_part}\n\nYour task: Focus on business analysis and metrics.\n{request_part}"
            return customized
        
        elif agent_id == 'isaiah':
            # Extract technical documentation requirements
            customized = f"{context_part}\n\nYour task: Focus on technical documentation.\n{request_part}"
            return customized
        
        elif agent_id == 'keisha':
            # Extract project management requirements
            customized = f"{context_part}\n\nYour task: Focus on project planning and organization.\n{request_part}"
            return customized
        
        # Default: return task as-is
        return task
    
    async def _synthesize_results(
        self,
        original_task: str,
        contributions: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesize all agent contributions into a cohesive final result
        
        Args:
            original_task: Original task request
            contributions: All agent contributions
            
        Returns:
            Synthesized final result
        """
        if len(contributions) == 1:
            # Single agent - return directly
            logger.info("Single agent result, no synthesis needed")
            return contributions[0]["contribution"]
        
        logger.info(f"Synthesizing results from {len(contributions)} agents")
        
        # Multiple agents - combine their work intelligently
        synthesis_prompt = f"""
        Multiple AI specialists have worked together on this request.
        
        Original request: {original_task.split('Current request:')[-1] if 'Current request:' in original_task else original_task}
        
        Here are their contributions:
        
        {chr(10).join([
            f"--- {c['agent']} ---\n{c['contribution']}\n"
            for c in contributions
        ])}
        
        Your task:
        1. Combine these contributions into ONE cohesive, well-organized response
        2. Present each specialist's work clearly under their name
        3. Make it natural and easy to read
        4. Keep all the important information
        5. Format nicely with clear sections
        
        Structure:
        - Brief intro (1 line)
        - Each agent's contribution in a clear section
        - Brief conclusion if appropriate
        """
        
        try:
            final_response = await llm_service.generate_response(
                messages=[{"role": "user", "content": synthesis_prompt}],
                system_prompt="You are an expert at organizing multiple inputs into clear, structured responses. Keep it concise and well-formatted.",
                temperature=0.7
            )
            
            logger.info("Synthesis completed successfully")
            return final_response
            
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            
            # Fallback: Format contributions manually
            result = "**Team Collaboration Result**\n\n"
            result += "Our specialist agents have worked together on your request:\n\n"
            
            for c in contributions:
                result += f"### {c['agent']}\n\n"
                result += f"{c['contribution']}\n\n"
                result += "---\n\n"
            
            return result