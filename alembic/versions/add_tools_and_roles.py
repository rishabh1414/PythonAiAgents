"""
Database Migration Script
Run: python3 scripts/migrate_db.py
"""
from app.db.database import engine, Base
from app.models.user import User
from app.models.tool import Tool, UserTool, ToolExecution
from app.models.agent_config import AgentConfig
from app.models.user_agent_chat import UserAgentChat, AgentChatMessage

# Import other models
from app.models.conversation import Conversation, Message
from app.models.task import Task

def migrate():
    """Create all new tables"""
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Migration complete!")

if __name__ == "__main__":
    migrate()