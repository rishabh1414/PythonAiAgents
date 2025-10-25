"""
API Testing Script
Quick tests for API endpoints
"""
import sys
import os
import httpx
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.utils.logger import logger


BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "test123",
    "full_name": "Test User"
}


async def test_health_check():
    """Test health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            logger.info(f"✓ Health check: {response.json()}")
            return True
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False


async def test_register():
    """Test user registration"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json=TEST_USER
            )
            
            if response.status_code == 201:
                logger.info(f"✓ Registration successful")
                return response.json()
            elif response.status_code == 400:
                logger.info("User already exists, skipping registration")
                return None
            else:
                logger.error(f"✗ Registration failed: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"✗ Registration error: {e}")
        return None


async def test_login():
    """Test user login"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                logger.info(f"✓ Login successful")
                logger.info(f"  Token: {token[:20]}...")
                return token
            else:
                logger.error(f"✗ Login failed: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"✗ Login error: {e}")
        return None


async def test_get_agents(token: str):
    """Test getting agents list"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/agents",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                agents = response.json()
                logger.info(f"✓ Retrieved {len(agents)} agents")
                for agent in agents:
                    logger.info(f"  - {agent['name']} ({agent['agent_id']})")
                return agents
            else:
                logger.error(f"✗ Get agents failed: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"✗ Get agents error: {e}")
        return None


async def test_send_message(token: str):
    """Test sending a chat message"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/chat/send",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "message": "Hello! Can you help me write an email?"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Message sent successfully")
                logger.info(f"  Agent: {data['agent_name']}")
                logger.info(f"  Response: {data['message']['content'][:100]}...")
                return data
            else:
                logger.error(f"✗ Send message failed: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"✗ Send message error: {e}")
        return None


async def test_create_task(token: str):
    """Test creating a task"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/tasks/create",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": "Write marketing email",
                    "description": "Create a promotional email for our new product",
                    "task_type": "email",
                    "priority": 2
                }
            )
            
            if response.status_code == 201:
                task = response.json()
                logger.info(f"✓ Task created successfully")
                logger.info(f"  Task ID: {task['id']}")
                logger.info(f"  Status: {task['status']}")
                return task
            else:
                logger.error(f"✗ Create task failed: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"✗ Create task error: {e}")
        return None


async def run_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("API Testing Started")
    logger.info("=" * 60)
    
    # Test health check
    if not await test_health_check():
        logger.error("Server is not running. Start it with:")
        logger.error("  python3 -m uvicorn app.main:app --reload")
        return
    
    logger.info("")
    
    # Test registration
    await test_register()
    await asyncio.sleep(1)
    
    # Test login
    token = await test_login()
    if not token:
        logger.error("Cannot proceed without authentication token")
        return
    
    await asyncio.sleep(1)
    logger.info("")
    
    # Test agents
    await test_get_agents(token)
    await asyncio.sleep(1)
    logger.info("")
    
    # Test chat
    await test_send_message(token)
    await asyncio.sleep(1)
    logger.info("")
    
    # Test tasks
    await test_create_task(token)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ API Testing Complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())