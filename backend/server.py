from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from models import (
    UserCreate, UserLogin, User, OnboardingData, 
    Organization, Event
)
from auth import (
    hash_password, verify_password, create_access_token, 
    get_current_user
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'drew_events')]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
        if 'organizationId' in doc and doc['organizationId']:
            doc['organizationId'] = str(doc['organizationId'])
    return doc

# Authentication Routes
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": hashed_pw,
        "firstName": None,
        "lastName": None,
        "role": None,
        "organizationId": None,
        "hasCompletedOnboarding": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.users.insert_one(new_user)
    user_id = str(result.inserted_id)
    
    # Generate token
    token = create_access_token(user_id, user_data.email)
    
    # Return user without password
    new_user.pop('password')
    new_user['_id'] = user_id
    
    return {
        "token": token,
        "user": serialize_doc(new_user)
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate token
    user_id = str(user['_id'])
    token = create_access_token(user_id, user['email'])
    
    # Return user without password
    user.pop('password')
    
    return {
        "token": token,
        "user": serialize_doc(user)
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"_id": ObjectId(current_user['user_id'])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.pop('password', None)
    return serialize_doc(user)

@api_router.post("/auth/magic-link")
async def send_magic_link(data: dict):
    # Mock implementation for now
    # In production, send actual email with magic link
    return {"success": True, "message": "Magic link sent"}

# User Routes
@api_router.post("/users/onboarding")
async def complete_onboarding(
    onboarding_data: OnboardingData,
    current_user: dict = Depends(get_current_user)
):
    user_id = ObjectId(current_user['user_id'])
    
    # Create organization if provided
    org_id = None
    if onboarding_data.organization:
        org_doc = {
            **onboarding_data.organization.dict(),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = await db.organizations.insert_one(org_doc)
        org_id = result.inserted_id
    
    # Update user with onboarding data
    update_data = {
        "firstName": onboarding_data.firstName,
        "lastName": onboarding_data.lastName,
        "role": onboarding_data.role,
        "hasCompletedOnboarding": True,
        "updatedAt": datetime.utcnow()
    }
    
    if org_id:
        update_data["organizationId"] = org_id
    
    await db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    # Fetch updated user
    updated_user = await db.users.find_one({"_id": user_id})
    updated_user.pop('password', None)
    
    return {
        "success": True,
        "user": serialize_doc(updated_user)
    }

# Event Routes
@api_router.get("/events")
async def get_events(
    location: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    query = {}
    
    if location:
        query["$or"] = [
            {"city": {"$regex": location, "$options": "i"}},
            {"state": {"$regex": location, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    events = await db.events.find(query).to_list(100)
    
    return {
        "events": [serialize_doc(event) for event in events]
    }

@api_router.get("/events/{event_id}")
async def get_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return serialize_doc(event)

# Health check
@api_router.get("/")
async def root():
    return {"message": "Drew API is running", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()