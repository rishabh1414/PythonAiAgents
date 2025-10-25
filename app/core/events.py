"""
Application Events - Startup and Shutdown
"""
from fastapi import FastAPI
from app.db.database import SessionLocal
from app.agents.registry import agent_registry
from app.utils.logger import logger


def register_events(app: FastAPI):
    """Register startup and shutdown events"""
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup"""
        logger.info("=" * 50)
        logger.info("🚀 Starting Multi-Agent System")
        logger.info("=" * 50)
        
        logger.info("Creating database tables...")
        from app.db.database import engine, Base
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created")
        
        # Load agents from database
        try:
            db = SessionLocal()
            agent_registry.load_agents_from_db(db)
            db.close()
            
            agent_count = len(agent_registry.get_all_agents())
            logger.info(f"✓ {agent_count} agents loaded from database")
            
            if agent_count == 0:
                logger.warning("⚠️ No agents found! Owner needs to create agents.")
            
        except Exception as e:
            logger.error(f"Error loading agents: {e}")
        
        logger.info("=" * 50)
        logger.info("✓ Application startup complete")
        logger.info("=" * 50)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown"""
        logger.info("Application shutting down...")