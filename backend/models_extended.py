"""
Extended models for Drew backend with semantic search support
Includes Activity, Offering, Occasion, PreRequisite with detailed fields
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
import hashlib
import json

def create_checksum(data: Dict[str, Any]) -> str:
    """Create MD5 checksum from data dictionary"""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()

# ============================================================================
# BASE MODELS
# ============================================================================

class BaseEntityModel(BaseModel):
    """Base model with common fields"""
    id: Optional[str] = Field(alias="_id", default=None)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    deletedAt: Optional[datetime] = None
    
    # Semantic search fields
    embedding: Optional[List[float]] = None  # Vector for semantic search
    embeddingText: Optional[str] = None  # Text used to generate embedding
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ============================================================================
# ACTIVITY TYPE MODELS
# ============================================================================

class ActivityTypeCreate(BaseModel):
    name: str
    description: str

class ActivityType(BaseEntityModel):
    """Activity Type - e.g., Workshop, Tour, Class, Performance"""
    name: str
    description: str

class ActivityTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ============================================================================
# ACTIVITY FORMAT MODELS
# ============================================================================

class ActivityFormatCreate(BaseModel):
    name: str
    description: str

class ActivityFormat(BaseEntityModel):
    """Activity Format - e.g., In-person, Virtual, Hybrid"""
    name: str
    description: str

class ActivityFormatUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ============================================================================
# PRE-REQUISITE MODELS
# ============================================================================

class PreRequisiteCreate(BaseModel):
    name: str
    description: str
    additionalInfo: str

class PreRequisite(BaseEntityModel):
    """Pre-requisite for activities"""
    name: str
    description: str
    additionalInfo: str
    checksum: str
    
    @validator('checksum', pre=True, always=True)
    def generate_checksum(cls, v, values):
        if not v:
            return create_checksum({
                'name': values.get('name', ''),
                'description': values.get('description', ''),
                'additionalInfo': values.get('additionalInfo', '')
            })
        return v

class PreRequisiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    additionalInfo: Optional[str] = None

# ============================================================================
# OFFERING MODELS  
# ============================================================================

class OfferingCreate(BaseModel):
    shortDescription: str
    longDescription: str

class Offering(BaseEntityModel):
    """Offering - things included in activities"""
    shortDescription: str
    longDescription: str

class OfferingUpdate(BaseModel):
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None

# ============================================================================
# OCCASION MODELS
# ============================================================================

class OccasionCreate(BaseModel):
    name: str
    description: str

class Occasion(BaseEntityModel):
    """Occasion - e.g., Birthday, Anniversary, Team Building"""
    name: str
    description: str

class OccasionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ============================================================================
# ACTIVITY SUB-MODELS
# ============================================================================

class ItineraryItemDetailed(BaseModel):
    """Detailed itinerary item with duration"""
    duration: int  # Duration in minutes
    title: str
    description: str
    image: Optional[str] = None

class ActivityItineraryCreate(BaseModel):
    """Full itinerary for an activity"""
    duration: int  # Total duration in minutes
    title: str
    description: str
    items: List[ItineraryItemDetailed] = []
    
    @validator('items')
    def validate_items_duration(cls, v, values):
        """Validate that sum of item durations equals total duration"""
        if v and 'duration' in values:
            total = sum(item.duration for item in v)
            if total != values['duration']:
                raise ValueError(f"Item durations ({total}) must equal total duration ({values['duration']})")
        return v

class ActivityItinerary(BaseEntityModel):
    """Activity Itinerary stored in DB"""
    activityId: str
    duration: int
    title: str
    description: str
    items: List[ItineraryItemDetailed] = []

class ActivityPreRequisiteLink(BaseModel):
    """Link between Activity and PreRequisite"""
    preRequisiteId: str
    name: str
    description: str
    additionalInfo: str
    checksum: str

class ActivityOfferingLink(BaseModel):
    """Link between Activity and Offering"""
    offeringId: str
    isRequired: bool = False
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None

class HostInfo(BaseModel):
    """Host information"""
    name: str
    title: str
    avatar: str

# ============================================================================
# ACTIVITY MODELS
# ============================================================================

class ActivityCreate(BaseModel):
    """Create activity request"""
    title: str
    shortDescription: str
    longDescription: str
    activityTypeId: str
    
    # Participants
    minParticipants: int
    maxParticipants: int
    
    # Duration (in minutes)
    minDuration: int
    maxDuration: int
    preferredDuration: int
    
    # Format
    formatId: str
    
    # Location
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    # Pricing
    price: float = 0.0
    
    # Media
    thumbnailUrl: Optional[str] = None
    images: List[str] = []
    
    # Host
    host: Optional[HostInfo] = None
    
    # Relations (IDs)
    preRequisiteIds: List[str] = []
    offeringIds: List[str] = []
    
    # Additional
    freeCancellation: bool = False
    category: Optional[str] = None
    rating: float = 0.0
    reviewCount: int = 0

class Activity(BaseEntityModel):
    """Full activity model"""
    title: str
    shortDescription: str
    longDescription: str
    
    # Type and Format
    activityTypeId: str
    activityType: Optional[ActivityType] = None  # Populated on query
    formatId: str
    format: Optional[ActivityFormat] = None  # Populated on query
    
    # Participants
    minParticipants: int
    maxParticipants: int
    
    # Duration
    minDuration: int
    maxDuration: int
    preferredDuration: int
    
    # Location
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    # Pricing
    price: float = 0.0
    
    # Media
    thumbnailUrl: Optional[str] = None
    images: List[str] = []
    
    # Host
    host: Optional[HostInfo] = None
    
    # Itineraries (embedded or referenced)
    itineraries: List[ActivityItinerary] = []
    
    # Pre-requisites (embedded with details)
    preRequisites: List[ActivityPreRequisiteLink] = []
    
    # Offerings (embedded with details)
    offerings: List[ActivityOfferingLink] = []
    
    # Additional
    freeCancellation: bool = False
    category: Optional[str] = None
    rating: float = 0.0
    reviewCount: int = 0
    
    # Metadata for agent
    metadata: Optional[Dict[str, Any]] = {}

class ActivityUpdate(BaseModel):
    """Update activity request"""
    title: Optional[str] = None
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None
    activityTypeId: Optional[str] = None
    formatId: Optional[str] = None
    minParticipants: Optional[int] = None
    maxParticipants: Optional[int] = None
    minDuration: Optional[int] = None
    maxDuration: Optional[int] = None
    preferredDuration: Optional[int] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    price: Optional[float] = None
    thumbnailUrl: Optional[str] = None
    images: Optional[List[str]] = None
    host: Optional[HostInfo] = None
    preRequisiteIds: Optional[List[str]] = None
    offeringIds: Optional[List[str]] = None
    freeCancellation: Optional[bool] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    reviewCount: Optional[int] = None

# ============================================================================
# PROJECT MODELS
# ============================================================================

class ProjectCreate(BaseModel):
    """Create project request"""
    name: str
    description: str
    occasionIds: List[str] = []  # List of occasion IDs

class Project(BaseEntityModel):
    """Project - tracks user's event planning projects"""
    name: str
    description: str
    userId: str
    threadId: str  # LangGraph thread ID for agent conversations
    occasionIds: List[str] = []
    occasions: List[Occasion] = []  # Populated on query
    recommendationIds: List[str] = []

class ProjectUpdate(BaseModel):
    """Update project request"""
    name: Optional[str] = None
    description: Optional[str] = None
    occasionIds: Optional[List[str]] = None

# ============================================================================
# RECOMMENDATION MODELS
# ============================================================================

class RecommendationCreate(BaseModel):
    """Create recommendation request"""
    activityId: str
    projectId: str
    title: str
    shortDescription: str
    longDescription: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    itinerary: Optional[List[ItineraryItemDetailed]] = None
    preRequisiteIds: List[str] = []
    offeringIds: List[str] = []
    reasonToRecommend: Optional[str] = None
    duration: Optional[int] = None

class Recommendation(BaseEntityModel):
    """Recommendation - AI-generated activity recommendations for projects"""
    activityId: str
    activity: Optional[Activity] = None  # Populated on query
    projectId: str
    project: Optional[Project] = None  # Populated on query
    userId: str
    
    # Denormalized activity data for quick access
    title: str
    shortDescription: str
    longDescription: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    itinerary: Optional[List[ItineraryItemDetailed]] = None
    
    # Relations
    preRequisiteIds: List[str] = []
    preRequisites: List[PreRequisite] = []  # Populated on query
    offeringIds: List[str] = []
    offerings: List[Offering] = []  # Populated on query
    
    # AI metadata
    reasonToRecommend: Optional[str] = None
    duration: Optional[int] = None
    score: float = 0.0

class RecommendationUpdate(BaseModel):
    """Update recommendation request"""
    title: Optional[str] = None
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    reasonToRecommend: Optional[str] = None
    duration: Optional[int] = None

# ============================================================================
# AGENT REQUEST/RESPONSE MODELS
# ============================================================================

class AgentPromptRequest(BaseModel):
    """Request to agent with user prompt"""
    prompt: str
    userId: Optional[str] = None
    sessionId: Optional[str] = None
    projectId: Optional[str] = None  # Optional project context
    context: Optional[Dict[str, Any]] = {}

class AgentRecommendation(BaseModel):
    """Recommendation from agent"""
    activityId: str
    activity: Optional[Activity] = None
    score: float
    reasoning: str
    matchedCriteria: List[str] = []

class AgentResponse(BaseModel):
    """Response from agent"""
    message: str
    recommendations: List[AgentRecommendation] = []
    suggestedQuestions: List[str] = []
    sessionId: str
    metadata: Optional[Dict[str, Any]] = {}
