from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from models import (
    UserCreate, UserLogin, User, UserUpdate,
    Organization, OrganizationCreate, OrganizationUpdate,
    ActivityCreate, Activity, ActivityUpdate,
    OnboardingData, Offering, Occasion
)
from models_extended import (
    AgentPromptRequest, AgentResponse,
    ProjectCreate, Project, ProjectUpdate,
    RecommendationCreate, Recommendation, RecommendationUpdate
)
from auth import (
    hash_password, verify_password, create_access_token, 
    get_current_user
)
from semantic_search import SemanticSearchService
from recommendation_agent import RecommendationAgent
from agent_tools import AgentTools
from multi_agent_system import SupervisorAgent

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'drew_events')]

# Create the main app without a prefix
app = FastAPI(title="Drew API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AI services
openai_api_key = os.environ.get('OPENAI_API_KEY')
semantic_search_service = None
recommendation_agent = None
agent_tools = None
supervisor_agent = None

if openai_api_key:
    try:
        semantic_search_service = SemanticSearchService(
            openai_api_key=openai_api_key,
            mongo_client=client,
            db_name=os.environ.get('DB_NAME', 'drew_events')
        )
        recommendation_agent = RecommendationAgent(
            openai_api_key=openai_api_key,
            semantic_search_service=semantic_search_service
        )
        agent_tools = AgentTools(
            semantic_search_service=semantic_search_service,
            db=db
        )
        supervisor_agent = SupervisorAgent(
            openai_api_key=openai_api_key,
            tools=agent_tools
        )
        logger.info("AI services initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize AI services: {e}")
else:
    logger.warning("OPENAI_API_KEY not set, AI features will be disabled")

# Helper function to convert ObjectId to string
def serialize_doc(doc: Dict) -> Dict:
    """Convert MongoDB ObjectId fields to strings"""
    if doc and '_id' in doc:
        doc['id'] = str(doc['_id'])
        doc['_id'] = str(doc['_id'])
    if doc and 'organizationId' in doc and doc['organizationId']:
        if isinstance(doc['organizationId'], ObjectId):
            doc['organizationId'] = str(doc['organizationId'])
    return doc

def serialize_list(docs: List[Dict]) -> List[Dict]:
    """Serialize a list of documents"""
    return [serialize_doc(doc) for doc in docs]

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@api_router.post("/user/register", status_code=201)
async def register(user_data: UserCreate):
    """Register a new user account"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already taken")
    
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

@api_router.post("/user/verify")
async def verify_login(credentials: UserLogin):
    """Verify user credentials and create session"""
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

@api_router.get("/user/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get currently authenticated user information"""
    user = await db.users.find_one({"_id": ObjectId(current_user['user_id'])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.pop('password', None)
    return serialize_doc(user)

@api_router.put("/user/{user_id}")
async def update_user(
    user_id: str, 
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user information"""
    # Verify user is updating their own profile or is admin
    if current_user['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Build update document
    update_doc = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_doc:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    update_doc['updatedAt'] = datetime.utcnow()
    
    # Update user
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch updated user
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user.pop('password', None)
    
    return serialize_doc(updated_user)

@api_router.post("/auth/magic-link")
async def send_magic_link(data: Dict[str, str]):
    """Send magic link email for passwordless login"""
    # Mock implementation for now
    # In production, send actual email with magic link
    email = data.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    return {"success": True, "message": "Magic link sent"}

@api_router.get("/auth/google/redirect")
async def google_oauth_redirect():
    """Initiate Google OAuth flow"""
    # Mock implementation
    # In production, redirect to Google OAuth consent screen
    return {"message": "Google OAuth not implemented yet", "status": "mock"}

@api_router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current user (JWT is stateless, so this is mainly for frontend)"""
    return {"success": True, "message": "Logged out successfully"}

# =============================================================================
# ORGANIZATION ROUTES
# =============================================================================

@api_router.post("/organization", status_code=201)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new organization"""
    org_doc = {
        **org_data.dict(),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.organizations.insert_one(org_doc)
    org_doc['_id'] = result.inserted_id
    
    return serialize_doc(org_doc)

@api_router.get("/organization/{org_id}")
async def get_organization(
    org_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get organization by ID"""
    if not ObjectId.is_valid(org_id):
        raise HTTPException(status_code=400, detail="Invalid organization ID")
    
    org = await db.organizations.find_one({"_id": ObjectId(org_id)})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return serialize_doc(org)

@api_router.put("/organization/{org_id}")
async def update_organization(
    org_id: str,
    update_data: OrganizationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update organization information"""
    if not ObjectId.is_valid(org_id):
        raise HTTPException(status_code=400, detail="Invalid organization ID")
    
    # Build update document
    update_doc = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_doc:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    update_doc['updatedAt'] = datetime.utcnow()
    
    # Update organization
    result = await db.organizations.update_one(
        {"_id": ObjectId(org_id)},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Fetch updated organization
    updated_org = await db.organizations.find_one({"_id": ObjectId(org_id)})
    
    return serialize_doc(updated_org)

@api_router.get("/organization")
async def list_organizations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List organizations with optional filtering"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"industry": {"$regex": search, "$options": "i"}}
        ]
    
    # Get total count
    total = await db.organizations.count_documents(query)
    
    # Get paginated results
    cursor = db.organizations.find(query).skip(offset).limit(limit)
    organizations = await cursor.to_list(length=limit)
    
    return {
        "rows": serialize_list(organizations),
        "count": len(organizations),
        "total": total,
        "limit": limit,
        "offset": offset
    }

# =============================================================================
# ACTIVITY/EVENT ROUTES
# =============================================================================

@api_router.get("/activity")
async def list_activities(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None
):
    """List activities/events with optional filtering"""
    query = {}
    
    if location:
        query["$or"] = [
            {"city": {"$regex": location, "$options": "i"}},
            {"state": {"$regex": location, "$options": "i"}},
            {"location": {"$regex": location, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    if search:
        search_query = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
        if "$or" in query:
            query["$and"] = [{"$or": query["$or"]}, {"$or": search_query}]
            del query["$or"]
        else:
            query["$or"] = search_query
    
    # Get total count
    total = await db.activities.count_documents(query)
    
    # Get paginated results
    cursor = db.activities.find(query).skip(offset).limit(limit)
    activities = await cursor.to_list(length=limit)
    
    return {
        "rows": serialize_list(activities),
        "count": len(activities),
        "total": total,
        "limit": limit,
        "offset": offset
    }

@api_router.get("/activity/{activity_id}")
async def get_activity(
    activity_id: str,
    expand: Optional[str] = Query(None, description="Comma-separated relations to expand")
):
    """Get activity/event details by ID"""
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")
    
    activity = await db.activities.find_one({"_id": ObjectId(activity_id)})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = serialize_doc(activity)
    
    # Handle expand parameter
    if expand:
        expand_fields = [field.strip() for field in expand.split(',')]
        
        # Expand offerings if requested
        if 'offerings' in expand_fields and activity.get('offerings'):
            offering_ids = [ObjectId(oid) for oid in activity['offerings'] if ObjectId.is_valid(oid)]
            if offering_ids:
                offerings = await db.offerings.find({"_id": {"$in": offering_ids}}).to_list(100)
                activity['offerings'] = serialize_list(offerings)
    
    return activity

@api_router.post("/activity", status_code=201)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new activity/event"""
    activity_doc = {
        **activity_data.dict(),
        "rating": 0.0,
        "reviewCount": 0,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.activities.insert_one(activity_doc)
    activity_doc['_id'] = result.inserted_id
    
    return serialize_doc(activity_doc)

@api_router.put("/activity/{activity_id}")
async def update_activity(
    activity_id: str,
    update_data: ActivityUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update activity/event information"""
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")
    
    # Build update document
    update_doc = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_doc:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    update_doc['updatedAt'] = datetime.utcnow()
    
    # Update activity
    result = await db.activities.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Fetch updated activity
    updated_activity = await db.activities.find_one({"_id": ObjectId(activity_id)})
    
    return serialize_doc(updated_activity)

# =============================================================================
# OCCASION ROUTES
# =============================================================================

@api_router.get("/occasion")
async def list_occasions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List occasions with optional filtering"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Get total count
    total = await db.occasions.count_documents(query)
    
    # Get paginated results
    cursor = db.occasions.find(query).skip(offset).limit(limit)
    occasions = await cursor.to_list(length=limit)
    
    return {
        "rows": serialize_list(occasions),
        "count": len(occasions),
        "total": total,
        "limit": limit,
        "offset": offset
    }

@api_router.get("/occasion/{occasion_id}")
async def get_occasion(
    occasion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get occasion by ID"""
    if not ObjectId.is_valid(occasion_id):
        raise HTTPException(status_code=400, detail="Invalid occasion ID")
    
    occasion = await db.occasions.find_one({"_id": ObjectId(occasion_id)})
    if not occasion:
        raise HTTPException(status_code=404, detail="Occasion not found")
    
    return serialize_doc(occasion)

# =============================================================================
# OFFERING ROUTES
# =============================================================================

@api_router.get("/offering")
async def list_offerings(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List offerings with optional filtering"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Get total count
    total = await db.offerings.count_documents(query)
    
    # Get paginated results
    cursor = db.offerings.find(query).skip(offset).limit(limit)
    offerings = await cursor.to_list(length=limit)
    
    return {
        "rows": serialize_list(offerings),
        "count": len(offerings),
        "total": total,
        "limit": limit,
        "offset": offset
    }

@api_router.get("/offering/{offering_id}")
async def get_offering(
    offering_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get offering by ID"""
    if not ObjectId.is_valid(offering_id):
        raise HTTPException(status_code=400, detail="Invalid offering ID")
    
    offering = await db.offerings.find_one({"_id": ObjectId(offering_id)})
    if not offering:
        raise HTTPException(status_code=404, detail="Offering not found")
    
    return serialize_doc(offering)

# =============================================================================
# ONBOARDING ROUTES
# =============================================================================

@api_router.post("/onboarding")
async def complete_onboarding(
    onboarding_data: OnboardingData,
    current_user: dict = Depends(get_current_user)
):
    """Complete user onboarding process"""
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

# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@api_router.post("/project", status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project"""
    import uuid
    
    project_doc = {
        **project_data.dict(),
        "userId": current_user['user_id'],
        "threadId": str(uuid.uuid4()),  # Generate new thread ID for agent
        "recommendationIds": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.projects.insert_one(project_doc)
    project_doc['_id'] = result.inserted_id
    
    return serialize_doc(project_doc)

@api_router.get("/project")
async def list_projects(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List user's projects"""
    user_id = current_user['user_id']
    
    query = {"userId": user_id}
    
    # Get total count
    total = await db.projects.count_documents(query)
    
    # Get paginated results
    cursor = db.projects.find(query).skip(offset).limit(limit).sort("createdAt", -1)
    projects = await cursor.to_list(length=limit)
    
    return {
        "rows": serialize_list(projects),
        "count": len(projects),
        "total": total,
        "limit": limit,
        "offset": offset
    }

@api_router.get("/project/{project_id}")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get project by ID"""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    project = await db.projects.find_one({
        "_id": ObjectId(project_id),
        "userId": current_user['user_id']
    })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Populate occasions if they exist
    if project.get('occasionIds'):
        occasion_object_ids = [ObjectId(oid) for oid in project['occasionIds'] if ObjectId.is_valid(oid)]
        if occasion_object_ids:
            occasions = await db.occasions.find({"_id": {"$in": occasion_object_ids}}).to_list(100)
            project['occasions'] = serialize_list(occasions)
    
    return serialize_doc(project)

@api_router.put("/project/{project_id}")
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update project"""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    # Build update document
    update_doc = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_doc:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    update_doc['updatedAt'] = datetime.utcnow()
    
    # Update project
    result = await db.projects.update_one(
        {"_id": ObjectId(project_id), "userId": current_user['user_id']},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Fetch updated project
    updated_project = await db.projects.find_one({"_id": ObjectId(project_id)})
    
    return serialize_doc(updated_project)

@api_router.delete("/project/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete project"""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    result = await db.projects.delete_one({
        "_id": ObjectId(project_id),
        "userId": current_user['user_id']
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Also delete associated recommendations
    await db.recommendations.delete_many({"projectId": project_id})
    
    return {"success": True, "message": "Project deleted"}

# =============================================================================
# RECOMMENDATION ENDPOINTS
# =============================================================================

@api_router.post("/recommendation", status_code=201)
async def create_recommendation(
    rec_data: RecommendationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new recommendation"""
    # Verify project belongs to user
    project = await db.projects.find_one({
        "_id": ObjectId(rec_data.projectId) if ObjectId.is_valid(rec_data.projectId) else None,
        "userId": current_user['user_id']
    })
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    rec_doc = {
        **rec_data.dict(),
        "userId": current_user['user_id'],
        "score": 0.0,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db.recommendations.insert_one(rec_doc)
    rec_id = str(result.inserted_id)
    rec_doc['_id'] = result.inserted_id
    
    # Add recommendation ID to project
    await db.projects.update_one(
        {"_id": ObjectId(rec_data.projectId)},
        {"$push": {"recommendationIds": rec_id}}
    )
    
    return serialize_doc(rec_doc)

@api_router.get("/recommendation")
async def list_recommendations(
    project_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List recommendations for a project or user"""
    query = {"userId": current_user['user_id']}
    
    if project_id:
        query["projectId"] = project_id
    
    # Get total count
    total = await db.recommendations.count_documents(query)
    
    # Get paginated results
    cursor = db.recommendations.find(query).skip(offset).limit(limit).sort("createdAt", -1)
    recommendations = await cursor.to_list(length=limit)
    
    return {
        "rows": serialize_list(recommendations),
        "count": len(recommendations),
        "total": total,
        "limit": limit,
        "offset": offset
    }

@api_router.get("/recommendation/{rec_id}")
async def get_recommendation(
    rec_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get recommendation by ID with populated activity data"""
    if not ObjectId.is_valid(rec_id):
        raise HTTPException(status_code=400, detail="Invalid recommendation ID")
    
    rec = await db.recommendations.find_one({
        "_id": ObjectId(rec_id),
        "userId": current_user['user_id']
    })
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Populate activity if exists
    if rec.get('activityId') and ObjectId.is_valid(rec['activityId']):
        activity = await db.activities.find_one({"_id": ObjectId(rec['activityId'])})
        if activity:
            rec['activityDetails'] = serialize_doc(activity)
    
    # Populate offerings
    if rec.get('offeringIds'):
        offering_ids = [ObjectId(oid) for oid in rec['offeringIds'] if ObjectId.is_valid(oid)]
        if offering_ids:
            offerings = await db.offerings.find({"_id": {"$in": offering_ids}}).to_list(100)
            rec['offerings'] = serialize_list(offerings)
    
    # Populate prerequisites
    if rec.get('preRequisiteIds'):
        prereq_ids = [ObjectId(oid) for oid in rec['preRequisiteIds'] if ObjectId.is_valid(oid)]
        if prereq_ids:
            prereqs = await db.prerequisites.find({"_id": {"$in": prereq_ids}}).to_list(100)
            rec['preRequisites'] = serialize_list(prereqs)
    
    return serialize_doc(rec)

@api_router.put("/recommendation/{rec_id}")
async def update_recommendation(
    rec_id: str,
    update_data: RecommendationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update recommendation"""
    if not ObjectId.is_valid(rec_id):
        raise HTTPException(status_code=400, detail="Invalid recommendation ID")
    
    # Build update document
    update_doc = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_doc:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    update_doc['updatedAt'] = datetime.utcnow()
    
    # Update recommendation
    result = await db.recommendations.update_one(
        {"_id": ObjectId(rec_id), "userId": current_user['user_id']},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Fetch updated recommendation
    updated_rec = await db.recommendations.find_one({"_id": ObjectId(rec_id)})
    
    return serialize_doc(updated_rec)

@api_router.delete("/recommendation/{rec_id}")
async def delete_recommendation(
    rec_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete recommendation"""
    if not ObjectId.is_valid(rec_id):
        raise HTTPException(status_code=400, detail="Invalid recommendation ID")
    
    # Get recommendation to find project
    rec = await db.recommendations.find_one({
        "_id": ObjectId(rec_id),
        "userId": current_user['user_id']
    })
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Delete recommendation
    await db.recommendations.delete_one({"_id": ObjectId(rec_id)})
    
    # Remove from project's recommendation list
    if rec.get('projectId'):
        await db.projects.update_one(
            {"_id": ObjectId(rec['projectId'])},
            {"$pull": {"recommendationIds": rec_id}}
        )
    
    return {"success": True, "message": "Recommendation deleted"}

# =============================================================================
# AI AGENT ENDPOINTS
# =============================================================================

@api_router.post("/project/{project_id}/chat/stream")
async def project_chat_stream(
    project_id: str,
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Stream chat with AI agent for a specific project
    Returns Server-Sent Events with real-time agent progress
    """
    if not supervisor_agent:
        raise HTTPException(
            status_code=503,
            detail="AI service is not available"
        )
    
    async def event_generator():
        try:
            # Verify project
            project = await db.projects.find_one({
                "_id": ObjectId(project_id) if ObjectId.is_valid(project_id) else None,
                "userId": current_user['user_id']
            })
            
            if not project:
                yield f"data: {json.dumps({'error': 'Project not found'})}\n\n"
                return
            
            prompt = request.get('prompt', request.get('message', ''))
            if not prompt:
                yield f"data: {json.dumps({'error': 'Prompt required'})}\n\n"
                return
            
            # Send initial state
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting AI agents...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Run agent with streaming state updates
            # We'll modify supervisor to yield states
            response = await supervisor_agent.run(
                prompt=prompt,
                user_id=current_user['user_id'],
                project_id=project_id,
                thread_id=project.get('threadId')
            )
            
            # Stream agent states
            for state in response.get('agentStates', []):
                yield f"data: {json.dumps({'type': 'agent_state', 'state': state})}\n\n"
                await asyncio.sleep(0.1)
            
            # Stream project updates
            project_name = response.get('projectName')
            project_desc = response.get('projectDescription')
            
            if project_name and project_desc:
                await db.projects.update_one(
                    {"_id": ObjectId(project_id)},
                    {"$set": {
                        "name": project_name,
                        "description": project_desc
                    }}
                )
                project_update_data = {'type': 'project_update', 'name': project_name, 'description': project_desc}
                yield f"data: {json.dumps(project_update_data)}\n\n"
            
            # Stream response message character by character
            message = response.get('message', '')
            logger.info(f"Streaming message: {len(message)} characters")
            
            if message:
                for i in range(0, len(message), 10):  # 10 chars at a time
                    chunk = message[i:i+10]
                    yield f"data: {json.dumps({'type': 'message_chunk', 'chunk': chunk})}\n\n"
                    await asyncio.sleep(0.03)
            else:
                logger.warning("No message to stream - response.get('message') is empty")
            
            # Send completion
            completion_data = {'type': 'complete', 'recommendationCount': len(response.get('recommendations', []))}
            yield f"data: {json.dumps(completion_data)}\n\n"
            logger.info("Streaming complete")
            
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@api_router.post("/project/{project_id}/chat")
async def project_chat(
    project_id: str,
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with AI agent for a specific project (non-streaming fallback)
    Creates recommendations, builds itineraries, manages offerings
    """
    if not supervisor_agent:
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please configure OPENAI_API_KEY."
        )
    
    try:
        # Verify project belongs to user
        project = await db.projects.find_one({
            "_id": ObjectId(project_id) if ObjectId.is_valid(project_id) else None,
            "userId": current_user['user_id']
        })
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        prompt = request.get('prompt', request.get('message', ''))
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Run supervisor agent
        response = await supervisor_agent.run(
            prompt=prompt,
            user_id=current_user['user_id'],
            project_id=project_id,
            thread_id=project.get('threadId')
        )
        
        # Update project with AI-generated name and description
        if response.get('projectName') and response.get('projectDescription'):
            await db.projects.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": {
                    "name": response['projectName'],
                    "description": response['projectDescription']
                }}
            )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in project chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@api_router.post("/agent/recommend")
async def get_recommendations(
    request: AgentPromptRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered activity recommendations based on user prompt
    DEPRECATED: Use /project/{project_id}/chat instead
    """
    if not recommendation_agent:
        raise HTTPException(
            status_code=503,
            detail="AI recommendation service is not available. Please configure OPENAI_API_KEY."
        )
    
    try:
        user_id = current_user['user_id']
        
        # Run the agent
        response = await recommendation_agent.run(
            prompt=request.prompt,
            user_id=user_id,
            session_id=request.sessionId,
            context=request.context
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error in recommendation agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing recommendation request: {str(e)}"
        )

@api_router.post("/agent/embeddings/generate")
async def generate_embeddings(
    current_user: dict = Depends(get_current_user)
):
    """
    Generate embeddings for all activities (admin function)
    Requires authentication
    """
    if not semantic_search_service:
        raise HTTPException(
            status_code=503,
            detail="Semantic search service is not available"
        )
    
    try:
        # Ensure indexes
        await semantic_search_service.ensure_indexes()
        
        # Generate embeddings
        count = await semantic_search_service.batch_generate_embeddings()
        
        return {
            "success": True,
            "message": f"Generated embeddings for {count} activities",
            "count": count
        }
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating embeddings: {str(e)}"
        )

# =============================================================================
# HEALTH CHECK & ROOT
# =============================================================================

@api_router.get("/")
async def api_root():
    """API health check"""
    ai_status = "enabled" if recommendation_agent else "disabled"
    return {
        "message": "Drew API is running",
        "version": "1.0.0",
        "status": "healthy",
        "ai_features": ai_status
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Drew API", "version": "1.0.0", "docs": "/docs"}

# =============================================================================
# BACKWARD COMPATIBILITY - Keep old /events endpoints
# =============================================================================

@api_router.get("/events")
async def get_events_compat(
    location: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Legacy endpoint - Get events (redirects to activities)"""
    result = await list_activities(
        limit=100,
        offset=0,
        search=search,
        category=category,
        location=location
    )
    return {"events": result["rows"]}

@api_router.get("/events/{event_id}")
async def get_event_compat(event_id: str, expand: Optional[str] = Query(None)):
    """Legacy endpoint - Get event by ID (redirects to activity)"""
    return await get_activity(event_id, expand)

# Include the router in the main app
app.include_router(api_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
