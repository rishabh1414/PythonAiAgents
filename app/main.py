"""
FastAPI Main Application
Entry point for the multi-agent system
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.websocket import websocket_endpoint
from app.core.events import register_events
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent AI System",
    description="Production-ready multi-agent system with real-time chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - IMPORTANT: Must be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]
)

# Include API router
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket, token: str = None):
    """WebSocket connection endpoint"""
    await websocket_endpoint(websocket, token)

# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Multi-Agent System API",
        "version": "1.0.0",
        "docs": "/docs",
        "agents": 10
    }

# Register startup/shutdown events
register_events(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )