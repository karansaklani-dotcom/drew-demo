"""
Test AI Agent System end-to-end
"""
import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def create_test_user():
    """Create a test user for agent testing"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'drew_events')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if test user exists
    test_user = await db.users.find_one({"email": "agent_test@example.com"})
    
    if test_user:
        print(f"✅ Test user exists: {test_user['_id']}")
        return str(test_user['_id'])
    
    # Create test user
    from datetime import datetime
    user_data = {
        "email": "agent_test@example.com",
        "username": "agent_tester",
        "password": "hashed_password_placeholder",
        "firstName": "Agent",
        "lastName": "Tester",
        "hasCompletedOnboarding": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_data)
    user_id = str(result.inserted_id)
    print(f"✅ Created test user: {user_id}")
    
    client.close()
    return user_id

async def create_test_project(user_id: str):
    """Create a test project"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'drew_events')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    from datetime import datetime
    project_data = {
        "userId": user_id,
        "name": "Test Project for AI Agent",
        "description": "Testing AI agent recommendation system",
        "recommendationIds": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.projects.insert_one(project_data)
    project_id = str(result.inserted_id)
    print(f"✅ Created test project: {project_id}")
    
    client.close()
    return project_id

async def test_agent_via_api():
    """Test the agent via direct API call"""
    import requests
    
    # Get backend URL
    backend_url = os.environ.get('REACT_APP_DREW_AI_BACKEND_URL', 'http://localhost:8001')
    
    print(f"\n🧪 Testing AI Agent API")
    print(f"   Backend URL: {backend_url}")
    
    # Step 1: Register/Login to get JWT token
    print(f"\n🔐 Step 1: Getting authentication token...")
    
    # Try to login first
    login_response = requests.post(
        f"{backend_url}/api/user/verify",
        json={
            "email": "agent_test@example.com",
            "password": "test123"
        }
    )
    
    if login_response.status_code == 200:
        auth_data = login_response.json()
        token = auth_data.get('token')
        user_id = auth_data.get('user', {}).get('_id')
        print(f"   ✅ Logged in successfully")
    else:
        # Register new user
        print(f"   Creating new user...")
        register_response = requests.post(
            f"{backend_url}/api/user/register",
            json={
                "email": "agent_test@example.com",
                "username": "agent_tester",
                "password": "test123",
                "firstName": "Agent",
                "lastName": "Tester"
            }
        )
        
        if register_response.status_code != 201:
            print(f"   ❌ Registration failed: {register_response.text}")
            return
        
        auth_data = register_response.json()
        token = auth_data.get('token')
        user_id = auth_data.get('user', {}).get('_id')
        print(f"   ✅ Registered successfully")
    
    print(f"   User ID: {user_id}")
    print(f"   Token: {token[:20]}...")
    
    # Step 2: Create a project
    print(f"\n📁 Step 2: Creating project...")
    project_id = await create_test_project(user_id)
    
    # Test query
    test_prompt = "I need team building activities in San Francisco for 15 people"
    
    print(f"\n📝 Step 3: Sending prompt: '{test_prompt}'")
    
    # Make API request with auth token
    url = f"{backend_url}/api/project/{project_id}/chat"
    payload = {
        "prompt": test_prompt,
        "userId": user_id,
        "threadId": None
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔄 Calling {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"\n📋 Response Summary:")
            print(f"   Message: {data.get('message', 'N/A')[:100]}...")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            print(f"   Agents Used: {data.get('agentsUsed', [])}")
            print(f"   Thread ID: {data.get('threadId', 'N/A')}")
            
            if data.get('recommendations'):
                print(f"\n🎯 Recommendations:")
                for i, rec in enumerate(data['recommendations'][:3], 1):
                    print(f"   {i}. {rec.get('title')}")
                    print(f"      Reason: {rec.get('reasonToRecommend', 'N/A')[:80]}...")
                    print(f"      Score: {rec.get('score', 0):.2f}")
            
            # Save full response to file
            with open('/app/backend/agent_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to agent_test_response.json")
            
        else:
            print(f"\n❌ FAILED!")
            print(f"   Error: {response.text[:500]}")
    
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_via_api())
