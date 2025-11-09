from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# User Models
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(alias="_id")
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[str] = None
    organizationId: Optional[str] = None
    hasCompletedOnboarding: bool = False
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Organization Models
class OrganizationCreate(BaseModel):
    name: str
    industry: str
    companySize: str
    website: Optional[str] = None

class Organization(BaseModel):
    id: str = Field(alias="_id")
    name: str
    industry: str
    companySize: str
    website: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# User Update Model
class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[str] = None
    organizationId: Optional[str] = None

# Organization Update Model
class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    website: Optional[str] = None

# Onboarding Model
class OnboardingData(BaseModel):
    firstName: str
    lastName: str
    role: str
    organization: Optional[OrganizationCreate] = None

# Activity/Event Models (renamed from Event to Activity for API consistency)
class Offering(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Occasion(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class PreRequisite(BaseModel):
    title: str
    icon: str

# Event Models
class HostInfo(BaseModel):
    name: str
    title: str
    avatar: str

class EventItem(BaseModel):
    icon: str
    title: str

class ItineraryItem(BaseModel):
    image: str
    title: str
    description: str

class ActivityCreate(BaseModel):
    title: str
    description: str
    longDescription: Optional[str] = None
    shortDescription: Optional[str] = None
    price: float
    location: str
    city: str
    state: str
    date: Optional[str] = None
    category: str
    images: List[str] = []
    thumbnailUrl: Optional[str] = None
    host: Optional[HostInfo] = None
    included: List[EventItem] = []
    required: List[EventItem] = []
    itinerary: List[ItineraryItem] = []
    freeCancellation: bool = False
    offerings: List[str] = []  # List of offering IDs
    preRequisites: List[PreRequisite] = []

class Activity(ActivityCreate):
    id: str = Field(alias="_id")
    rating: float = 0.0
    reviewCount: int = 0
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    longDescription: Optional[str] = None
    shortDescription: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    images: Optional[List[str]] = None
    thumbnailUrl: Optional[str] = None
    host: Optional[HostInfo] = None
    included: Optional[List[EventItem]] = None
    required: Optional[List[EventItem]] = None
    itinerary: Optional[List[ItineraryItem]] = None
    freeCancellation: Optional[bool] = None
    offerings: Optional[List[str]] = None
    preRequisites: Optional[List[PreRequisite]] = None

# Keep Event models for backward compatibility
EventCreate = ActivityCreate
Event = Activity
