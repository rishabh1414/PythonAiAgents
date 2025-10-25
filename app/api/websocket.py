"""
WebSocket Handler
Real-time communication with clients
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
from uuid import UUID
import json
from datetime import datetime

from app.utils.logger import logger
from app.core.security import decode_access_token


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Store active connections: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Connect a new WebSocket client
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Disconnect a WebSocket client
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            # Remove user entry if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send message to specific user
        
        Args:
            message: Message data
            user_id: Target user ID
        """
        if user_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected users
        
        Args:
            message: Message to broadcast
        """
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")
    
    async def send_agent_status(self, agent_id: str, status: str, user_id: str):
        """
        Send agent status update
        
        Args:
            agent_id: Agent identifier
            status: Agent status
            user_id: Target user ID
        """
        message = {
            "type": "agent_status",
            "agent_id": agent_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_task_update(self, task_id: str, status: str, user_id: str, data: dict = None):
        """
        Send task update notification
        
        Args:
            task_id: Task identifier
            status: Task status
            user_id: Target user ID
            data: Optional additional data
        """
        message = {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_message_notification(self, conversation_id: str, message_data: dict, user_id: str):
        """
        Send new message notification
        
        Args:
            conversation_id: Conversation identifier
            message_data: Message data
            user_id: Target user ID
        """
        notification = {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": message_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(notification, user_id)
    
    def get_active_users(self) -> List[str]:
        """Get list of active user IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())


# Create global connection manager
manager = ConnectionManager()


async def get_websocket_user(websocket: WebSocket, token: str = None) -> str:
    """
    Authenticate WebSocket connection and get user ID
    
    Args:
        websocket: WebSocket connection
        token: JWT token
        
    Returns:
        User ID
    """
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        raise Exception("No token provided")
    
    # Decode token
    payload = decode_access_token(token)
    
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        raise Exception("Invalid token")
    
    user_id = payload.get("sub")
    
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token payload")
        raise Exception("No user ID in token")
    
    return user_id


async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint handler
    
    Args:
        websocket: WebSocket connection
        token: Authentication token
    """
    user_id = None
    
    try:
        # Authenticate user
        user_id = await get_websocket_user(websocket, token)
        
        # Connect user
        await manager.connect(websocket, user_id)
        
        # Send connection success
        await websocket.send_json({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type")
            
            if message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "typing":
                # Broadcast typing indicator
                await manager.send_personal_message({
                    "type": "typing",
                    "user_id": user_id,
                    "is_typing": message.get("is_typing", False)
                }, user_id)
            
            else:
                logger.info(f"Received WebSocket message: {message_type}")
    
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
            logger.info(f"WebSocket disconnected: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user_id:
            manager.disconnect(websocket, user_id)