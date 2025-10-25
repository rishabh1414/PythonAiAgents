"""
Migration Script - Add new tables for tools and agent configs
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
from app.models.tool import Tool, UserTool, ToolExecution
from app.models.agent_config import AgentConfig
from app.models.user_agent_chat import UserAgentChat, AgentChatMessage
from app.utils.logger import logger


def migrate():
    """Run migration"""
    logger.info("Starting migration...")
    
    try:
        # Create new tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Migration complete - New tables created")
        
        logger.info("\nNew tables added:")
        logger.info("  - tools")
        logger.info("  - user_tools")
        logger.info("  - tool_executions")
        logger.info("  - agent_configs")
        logger.info("  - user_agent_chats")
        logger.info("  - agent_chat_messages")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate()
    