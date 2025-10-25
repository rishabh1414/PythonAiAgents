"""
Main API Router
"""
from fastapi import APIRouter

from app.api.endpoints import auth, chat, tasks, agents, webhooks
from app.api.endpoints import tools, agent_config, agent_chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(tasks.router)
api_router.include_router(agents.router)
api_router.include_router(webhooks.router)

# New routers
api_router.include_router(tools.router)
api_router.include_router(agent_config.router)
api_router.include_router(agent_chat.router)