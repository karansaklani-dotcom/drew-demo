# Drew Event Management Platform - API Contracts & Integration Plan

## Overview
This document outlines the API contracts, data models, and integration strategy for connecting the Drew frontend with the backend services.

## Current Frontend State
- **Mock Data Location**: `/app/frontend/src/mock/mockData.js`
- **Authentication**: Currently using localStorage-based mock authentication
- **Protected Routes**: Login, Onboarding, Event Discovery, Event Detail pages

## API Contracts

### 1. Authentication Endpoints

#### POST `/api/auth/magic-link`
Send magic link for passwordless authentication
```json
Request:
{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "message": "Magic link sent to your email"
}
```

#### POST `/api/auth/google`
Initiate Google OAuth flow
```json
Request:
{
  "code": "google_oauth_code"
}

Response:
{
  "success": true,
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "hasCompletedOnboarding": false
  },
  "token": "jwt_token"
}
```

#### GET `/api/auth/me`
Get current authenticated user
```json
Headers:
Authorization: Bearer <token>

Response:
{
  "id": "user_id",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "role": "volunteer",
  "organizationId": "org_id",
  "hasCompletedOnboarding": true
}
```

#### POST `/api/auth/logout`
Logout user
```json
Response:
{
  "success": true
}
```

### 2. User & Onboarding Endpoints

#### POST `/api/users/onboarding`
Complete user onboarding
```json
Request:
{
  "firstName": "John",
  "lastName": "Doe",
  "role": "engineering",
  "organization": {
    "name": "Tech Company",
    "industry": "technology",
    "companySize": "51-200",
    "website": "https://example.com"
  }
}

Response:
{
  "success": true,
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "hasCompletedOnboarding": true
  }
}
```

### 3. Event Endpoints

#### GET `/api/events`
Get all events with optional filters
```json
Query Parameters:
- location: string (optional)
- date: string (optional)
- category: string (optional)
- search: string (optional)

Response:
{
  "events": [
    {
      "id": "event_id",
      "title": "Lakehouse Jazz",
      "description": "Experience live jazz...",
      "longDescription": "Immerse yourself...",
      "price": 35,
      "location": "Hidden Boathouse",
      "city": "San Francisco",
      "state": "California",
      "date": "2025-08-15",
      "rating": 4.83,
      "reviewCount": 1789,
      "category": "Performances",
      "images": ["url1", "url2"],
      "freeCancellation": true,
      "host": {
        "name": "David",
        "title": "Music producer",
        "avatar": "url"
      }
    }
  ]
}
```

#### GET `/api/events/:id`
Get single event details
```json
Response:
{
  "id": "event_id",
  "title": "Lakehouse Jazz",
  "description": "...",
  "longDescription": "...",
  "price": 35,
  "location": "Hidden Boathouse",
  "city": "San Francisco",
  "state": "California",
  "date": "2025-08-15",
  "rating": 4.83,
  "reviewCount": 1789,
  "category": "Performances",
  "images": ["url1", "url2", "url3", "url4"],
  "freeCancellation": true,
  "host": {...},
  "included": [
    {"icon": "MapPin", "title": "Access to venue"}
  ],
  "required": [
    {"icon": "ShieldCheck", "title": "Must be 21+"}
  ],
  "itinerary": [
    {
      "image": "url",
      "title": "Arrive at boathouse",
      "description": "Get accurate directions..."
    }
  ]
}
```

#### POST `/api/events`
Create new event (for future AI generation feature)
```json
Request:
{
  "prompt": "Jazz event near lake...",
  "preferences": {
    "date": "2025-08-15",
    "location": "San Francisco",
    "interests": ["music", "jazz"]
  }
}

Response:
{
  "event": {...}
}
```

## MongoDB Data Models

### User Model
```javascript
{
  _id: ObjectId,
  email: String (unique, required),
  firstName: String,
  lastName: String,
  role: String (enum: ['volunteer', 'champion', 'admin']),
  organizationId: ObjectId (ref: 'Organization'),
  hasCompletedOnboarding: Boolean (default: false),
  googleId: String (optional),
  createdAt: Date,
  updatedAt: Date
}
```

### Organization Model
```javascript
{
  _id: ObjectId,
  name: String (required),
  industry: String (enum: ['technology', 'healthcare', 'finance', 'education', 'other']),
  companySize: String (enum: ['1-50', '51-200', '201-1000', '1000+']),
  website: String (optional),
  createdAt: Date,
  updatedAt: Date
}
```

### Event Model
```javascript
{
  _id: ObjectId,
  title: String (required),
  description: String (required),
  longDescription: String,
  price: Number (required),
  location: String (required),
  city: String (required),
  state: String (required),
  date: Date (required),
  rating: Number (default: 0),
  reviewCount: Number (default: 0),
  category: String (enum: ['Performances', 'Wellness', 'Food & Drink', 'Arts & Culture']),
  images: [String] (array of URLs),
  freeCancellation: Boolean (default: false),
  host: {
    name: String,
    title: String,
    avatar: String
  },
  included: [{
    icon: String,
    title: String
  }],
  required: [{
    icon: String,
    title: String
  }],
  itinerary: [{
    image: String,
    title: String,
    description: String
  }],
  createdAt: Date,
  updatedAt: Date
}
```

## Frontend Integration Plan

### Files to Update

1. **Remove Mock Data**:
   - Delete `/app/frontend/src/mock/mockData.js` after backend integration

2. **Create API Service Layer**:
   - `/app/frontend/src/services/api.js` - Axios instance with interceptors
   - `/app/frontend/src/services/authService.js` - Auth API calls
   - `/app/frontend/src/services/eventService.js` - Event API calls
   - `/app/frontend/src/services/userService.js` - User API calls

3. **Update AuthContext** (`/app/frontend/src/context/AuthContext.js`):
   - Replace mock functions with real API calls
   - Implement JWT token management
   - Add token refresh logic
   - Update session persistence to use tokens instead of full user object

4. **Update Pages**:
   - `/app/frontend/src/pages/Login.js`:
     - Connect to `/api/auth/magic-link` and `/api/auth/google`
     - Handle OAuth redirect flow
   
   - `/app/frontend/src/pages/Onboarding.js`:
     - Connect to `/api/users/onboarding`
     - Handle organization creation
   
   - `/app/frontend/src/pages/EventDiscovery.js`:
     - Fetch events from `/api/events`
     - Add loading states and error handling
   
   - `/app/frontend/src/pages/EventDetail.js`:
     - Fetch event by ID from `/api/events/:id`
     - Add 404 handling

## Backend Implementation Tasks

1. **Setup**:
   - Configure JWT authentication
   - Setup Google OAuth credentials (CLIENT_ID, CLIENT_SECRET)
   - Create MongoDB models (User, Organization, Event)
   - Seed database with mock events

2. **Authentication**:
   - Implement magic link email sending (using SendGrid or similar)
   - Google OAuth flow
   - JWT middleware for protected routes

3. **CRUD Operations**:
   - User profile management
   - Organization management
   - Event listing and details

4. **Security**:
   - Password hashing (if needed)
   - Rate limiting
   - Input validation with Pydantic
   - CORS configuration

## Environment Variables Required

### Backend `.env`
```
MONGO_URL=<existing>
DB_NAME=drew_events
JWT_SECRET=<generate_strong_secret>
JWT_EXPIRATION=7d

# Google OAuth
GOOGLE_CLIENT_ID=<to_be_provided>
GOOGLE_CLIENT_SECRET=<to_be_provided>
GOOGLE_REDIRECT_URI=<backend_url>/api/auth/google/callback

# Email (for magic links)
SENDGRID_API_KEY=<optional_for_now>
FROM_EMAIL=noreply@drew.app

# Frontend URL (for redirects)
FRONTEND_URL=<from_existing_env>
```

### Frontend `.env`
```
REACT_APP_BACKEND_URL=<existing>
REACT_APP_GOOGLE_CLIENT_ID=<same_as_backend>
```

## Testing Strategy

1. **Backend Testing**:
   - Test all endpoints with curl
   - Verify JWT token generation and validation
   - Test Google OAuth flow
   - Verify database operations

2. **Frontend Testing**:
   - Test login flow (both magic link and Google)
   - Test onboarding completion
   - Test event listing and filtering
   - Test event detail view
   - Test authentication persistence (page refresh)

## Notes

- OAuth credentials need to be configured in Google Console before implementation
- Magic link email feature can be implemented later; focus on Google OAuth first
- Event creation (AI feature) is mocked for now and can be implemented in phase 2
- Image uploads for events can use external URLs initially; file upload can be added later
