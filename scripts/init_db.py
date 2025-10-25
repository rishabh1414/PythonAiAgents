"""
Database Initialization Script - NO PRE-BUILT AGENTS
Owner creates all agents
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal, Base
from app.models.user import User, UserRole
from app.models.conversation import Conversation, Message
from app.models.task import Task
from app.models.tool import Tool, UserTool, ToolExecution
from app.models.agent_config import AgentConfig
from app.models.user_agent_chat import UserAgentChat, AgentChatMessage
from app.core.security import get_password_hash
from app.utils.logger import logger


def init_database():
    """Initialize database with tables and default data"""
    
    logger.info("=" * 60)
    logger.info("Database Initialization Started")
    logger.info("=" * 60)
    
    # Create all tables
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Tables created successfully")
    except Exception as e:
        logger.error(f"✗ Error creating tables: {e}")
        return
    
    # Create session
    db: Session = SessionLocal()
    
    try:
        # Create owner user
        owner = db.query(User).filter(User.email == "owner@example.com").first()
        if not owner:
            owner = User(
                email="owner@example.com",
                username="owner",
                hashed_password=get_password_hash("owner123"),
                full_name="System Owner",
                role=UserRole.OWNER,
                is_active=True,
                is_superuser=True
            )
            db.add(owner)
            db.commit()
            logger.info("✓ Owner user created")
            logger.info("  Email: owner@example.com")
            logger.info("  Password: owner123")
            logger.info("  Role: OWNER")
        
        # Create demo user
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo_user:
            demo_user = User(
                email="demo@example.com",
                username="demo",
                hashed_password=get_password_hash("demo123"),
                full_name="Demo User",
                role=UserRole.USER,
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            logger.info("✓ Demo user created")
            logger.info("  Email: demo@example.com")
            logger.info("  Password: demo123")
            logger.info("  Role: USER")
        
        # NO AGENTS CREATED - Owner must create them!
        logger.info("\n⚠️ NO AGENTS CREATED")
        logger.info("   Owner must login and create agents via Admin Dashboard")
        
        # Create sample tool
        logger.info("\nCreating sample tool...")
        
        gmail_tool = db.query(Tool).filter(Tool.name == "Gmail Sender").first()
        if not gmail_tool:
            gmail_tool = Tool(
                name="Gmail Sender",
                description="Send emails via Gmail using Make.com webhook",
                logo_url="📧",
                category="email",
                parameters_schema={
                    "to": {
                        "type": "email",
                        "required": True,
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "required": True,
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "required": True,
                        "format": "html",
                        "description": "Email body (HTML supported)"
                    }
                },
                available_to_agents=[],  # Owner will assign later
                is_active=True,
                created_by=owner.id
            )
            db.add(gmail_tool)
            db.commit()
            logger.info("✓ Gmail tool created (users can configure webhook URL)")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Database initialization complete!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Login as Owner: owner@example.com / owner123")
        logger.info("2. Create agents in Admin Dashboard")
        logger.info("3. Create/configure tools")
        logger.info("4. Users can then chat with agents")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()