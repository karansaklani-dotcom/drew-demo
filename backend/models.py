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

class EventCreate(BaseModel):
    title: str
    description: str
    longDescription: str
    price: float
    location: str
    city: str
    state: str
    date: str
    category: str
    images: List[str]
    host: HostInfo
    included: List[EventItem] = []
    required: List[EventItem] = []
    itinerary: List[ItineraryItem] = []
    freeCancellation: bool = False

class Event(EventCreate):
    id: str = Field(alias="_id")
    rating: float = 0.0
    reviewCount: int = 0
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
