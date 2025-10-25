"""
Memory Service
Manages agent memory and context retrieval
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.agent_memory import AgentMemory
from app.services.llm_service import llm_service
from app.db.redis_client import cache_get, cache_set
from app.utils.logger import logger
import json


class MemoryService:
    """Service for agent memory management"""
    
    def __init__(self):
        self.short_term_expiry = 3600  # 1 hour
        self.long_term_threshold = 0.7  # Importance score threshold
    
    async def store_memory(
        self,
        db: Session,
        agent_id: str,
        content: str,
        memory_type: str = "short_term",
        context: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.5
    ) -> AgentMemory:
        """Store a new memory for an agent"""
        try:
            # Generate embedding for semantic search (optional)
            try:
                embedding = await llm_service.generate_embedding(content)
            except:
                embedding = []  # Fallback if embedding fails
            
            # Create memory
            memory = AgentMemory(
                agent_id=agent_id,
                content=content,
                memory_type=memory_type,
                context=context or {},
                embedding=embedding,
                importance_score=importance_score
            )
            
            # Set expiry for short-term memories
            if memory_type == "short_term":
                memory.expires_at = datetime.utcnow() + timedelta(seconds=self.short_term_expiry)
            
            db.add(memory)
            db.commit()
            db.refresh(memory)
            
            # Cache in Redis for quick access
            cache_key = f"memory:{agent_id}:{memory.id}"
            cache_set(cache_key, json.dumps({
                "content": content,
                "type": memory_type,
                "score": importance_score
            }), expire=self.short_term_expiry)
            
            logger.info(f"Stored {memory_type} memory for agent {agent_id}")
            return memory
            
        except Exception as e:
            logger.error(f"Memory storage error: {e}")
            db.rollback()
            raise
    
    async def retrieve_memories(
        self,
        db: Session,
        agent_id: str,
        query: str,
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[AgentMemory]:
        """Retrieve relevant memories for a query"""
        try:
            # Build query
            query_obj = db.query(AgentMemory).filter(
                AgentMemory.agent_id == agent_id
            )
            
            # Filter by type if specified
            if memory_type:
                query_obj = query_obj.filter(AgentMemory.memory_type == memory_type)
            
            # Filter out expired memories
            query_obj = query_obj.filter(
                (AgentMemory.expires_at.is_(None)) |
                (AgentMemory.expires_at > datetime.utcnow())
            )
            
            # Order by importance and recency
            memories = query_obj.order_by(
                AgentMemory.importance_score.desc(),
                AgentMemory.last_accessed.desc()
            ).limit(limit).all()
            
            # Update access count
            for memory in memories:
                memory.accessed_count += 1
                memory.last_accessed = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Retrieved {len(memories)} memories for agent {agent_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Memory retrieval error: {e}")
            return []
    
    async def cleanup_expired_memories(self, db: Session):
        """Clean up expired short-term memories"""
        try:
            deleted = db.query(AgentMemory).filter(
                AgentMemory.expires_at < datetime.utcnow()
            ).delete()
            
            db.commit()
            logger.info(f"Cleaned up {deleted} expired memories")
            
        except Exception as e:
            logger.error(f"Memory cleanup error: {e}")
            db.rollback()


# Create global instance
memory_service = MemoryService()