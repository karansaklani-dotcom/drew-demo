"""
Comprehensive seed script for Drew backend
Seeds all entities with diverse activities across categories
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ============================================================================
# ACTIVITY TYPES
# ============================================================================
activity_types = [
    {
        "name": "Volunteering",
        "description": "Community service and volunteer activities that make a positive social impact",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Team Bonding",
        "description": "Activities designed to strengthen team relationships and collaboration",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Employee Engagement",
        "description": "Events focused on boosting employee morale and company culture",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Learning & Development",
        "description": "Educational workshops and skill-building sessions",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Wellness",
        "description": "Health and wellness activities for physical and mental well-being",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Social Events",
        "description": "Casual social gatherings and entertainment activities",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Creative Workshops",
        "description": "Arts, crafts, and creative expression activities",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

# ============================================================================
# ACTIVITY FORMATS
# ============================================================================
activity_formats = [
    {
        "name": "In-Person",
        "description": "Physical, face-to-face activities at a specific location",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Virtual",
        "description": "Online activities accessible from anywhere",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Hybrid",
        "description": "Combination of in-person and virtual participation options",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

# ============================================================================
# OCCASIONS
# ============================================================================
occasions = [
    {
        "name": "Team Building",
        "description": "Events for strengthening team dynamics",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Company Milestone",
        "description": "Celebrating company achievements and anniversaries",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "New Employee Onboarding",
        "description": "Welcoming and integrating new team members",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Holiday Celebration",
        "description": "Seasonal and holiday gatherings",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Professional Development",
        "description": "Career growth and skill enhancement",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Community Service Day",
        "description": "Giving back to the community",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

# ============================================================================
# PRE-REQUISITES
# ============================================================================
prerequisites = [
    {
        "name": "Age Requirement",
        "description": "Participants must be 18+ years old",
        "additionalInfo": "Valid ID required for verification",
        "checksum": "prereq_age_18",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Physical Fitness",
        "description": "Moderate physical activity required",
        "additionalInfo": "Comfortable walking shoes recommended",
        "checksum": "prereq_physical",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Laptop Required",
        "description": "Bring your own laptop",
        "additionalInfo": "Charger and mouse recommended",
        "checksum": "prereq_laptop",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "No Experience Needed",
        "description": "Suitable for all skill levels",
        "additionalInfo": "Beginners welcome",
        "checksum": "prereq_beginner",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

# ============================================================================
# OFFERINGS
# ============================================================================
offerings = [
    {
        "shortDescription": "Refreshments Provided",
        "longDescription": "Light snacks, beverages, and refreshments throughout the event",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "shortDescription": "All Materials Included",
        "longDescription": "All necessary materials, supplies, and equipment provided",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "shortDescription": "Professional Instructor",
        "longDescription": "Led by experienced professional with industry expertise",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "shortDescription": "Certificate of Completion",
        "longDescription": "Receive a certificate upon successful completion",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "shortDescription": "Transportation Provided",
        "longDescription": "Round-trip transportation from designated pickup points",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "shortDescription": "Digital Resources",
        "longDescription": "Access to online resources and follow-up materials",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

# ============================================================================
# COMPREHENSIVE ACTIVITIES
# ============================================================================
activities = [
    # VOLUNTEERING ACTIVITIES
    {
        "title": "Community Garden Revitalization",
        "shortDescription": "Help transform a local community garden into a thriving green space",
        "longDescription": "Join us in revitalizing the Mission District Community Garden. We'll be planting vegetables, building raised beds, and creating a sustainable urban farming space that will benefit the local community for years to come.",
        "activityTypeId": "volunteering",  # Will be replaced with actual ID
        "formatId": "in-person",
        "minParticipants": 10,
        "maxParticipants": 30,
        "minDuration": 180,
        "maxDuration": 300,
        "preferredDuration": 240,
        "location": "Mission District Community Garden",
        "city": "San Francisco",
        "state": "California",
        "price": 0,
        "category": "Volunteering",
        "images": [
            "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800",
            "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=800",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400",
        "host": {
            "name": "Sarah Chen",
            "title": "Community Coordinator",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"
        },
        "freeCancellation": True,
        "rating": 4.9,
        "reviewCount": 127,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Beach Cleanup & Marine Conservation",
        "shortDescription": "Protect our oceans by cleaning Ocean Beach and learning about marine ecosystems",
        "longDescription": "Spend a morning making a tangible environmental impact while enjoying the beautiful California coast. We'll provide all cleanup materials and you'll learn about marine conservation from expert guides.",
        "activityTypeId": "volunteering",
        "formatId": "in-person",
        "minParticipants": 5,
        "maxParticipants": 50,
        "minDuration": 120,
        "maxDuration": 180,
        "preferredDuration": 150,
        "location": "Ocean Beach",
        "city": "San Francisco",
        "state": "California",
        "price": 0,
        "category": "Volunteering",
        "images": [
            "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?w=800",
            "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?w=400",
        "host": {
            "name": "Michael Torres",
            "title": "Environmental Scientist",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Michael"
        },
        "freeCancellation": True,
        "rating": 4.8,
        "reviewCount": 203,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    
    # TEAM BONDING ACTIVITIES
    {
        "title": "Escape Room Challenge: Corporate Heist",
        "shortDescription": "Work together to solve puzzles and escape before time runs out",
        "longDescription": "Test your team's problem-solving skills in this immersive escape room experience. The Corporate Heist scenario requires collaboration, communication, and creative thinking to succeed.",
        "activityTypeId": "team-bonding",
        "formatId": "in-person",
        "minParticipants": 6,
        "maxParticipants": 12,
        "minDuration": 60,
        "maxDuration": 90,
        "preferredDuration": 75,
        "location": "Downtown Escape Rooms",
        "city": "San Francisco",
        "state": "California",
        "price": 45,
        "category": "Team Building",
        "images": [
            "https://images.unsplash.com/photo-1583521214690-73421a1829a9?w=800",
            "https://images.unsplash.com/photo-1511306404404-ad607bd7c601?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1583521214690-73421a1829a9?w=400",
        "host": {
            "name": "Alex Rodriguez",
            "title": "Game Master & Team Coach",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex"
        },
        "freeCancellation": True,
        "rating": 4.7,
        "reviewCount": 342,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Culinary Team Building: Cooking Competition",
        "shortDescription": "Bond over food as teams compete in a friendly cooking challenge",
        "longDescription": "Divide into teams and create delicious dishes in this interactive cooking competition. Learn new culinary skills while strengthening team dynamics and having fun together.",
        "activityTypeId": "team-bonding",
        "formatId": "in-person",
        "minParticipants": 8,
        "maxParticipants": 24,
        "minDuration": 150,
        "maxDuration": 210,
        "preferredDuration": 180,
        "location": "Bay Area Culinary Studio",
        "city": "Oakland",
        "state": "California",
        "price": 85,
        "category": "Team Building",
        "images": [
            "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=800",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400",
        "host": {
            "name": "Chef Maria Gonzalez",
            "title": "Executive Chef",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Maria"
        },
        "freeCancellation": True,
        "rating": 4.9,
        "reviewCount": 156,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    
    # EMPLOYEE ENGAGEMENT ACTIVITIES
    {
        "title": "Innovation Workshop: Design Thinking Sprint",
        "shortDescription": "Learn design thinking methodologies to drive innovation in your organization",
        "longDescription": "This hands-on workshop teaches the fundamentals of design thinking through real-world challenges. Perfect for teams looking to foster innovation and creative problem-solving.",
        "activityTypeId": "employee-engagement",
        "formatId": "hybrid",
        "minParticipants": 8,
        "maxParticipants": 20,
        "minDuration": 240,
        "maxDuration": 360,
        "preferredDuration": 300,
        "location": "Innovation Hub SF",
        "city": "San Francisco",
        "state": "California",
        "price": 150,
        "category": "Professional Development",
        "images": [
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800",
            "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=400",
        "host": {
            "name": "Dr. James Park",
            "title": "Innovation Consultant",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=James"
        },
        "freeCancellation": False,
        "rating": 4.8,
        "reviewCount": 89,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Employee Appreciation Jazz Night",
        "shortDescription": "Celebrate your team with live jazz, networking, and great food",
        "longDescription": "An elegant evening of live jazz music, gourmet appetizers, and team celebration. Perfect for recognizing employee achievements and fostering company culture.",
        "activityTypeId": "employee-engagement",
        "formatId": "in-person",
        "minParticipants": 20,
        "maxParticipants": 100,
        "minDuration": 180,
        "maxDuration": 240,
        "preferredDuration": 210,
        "location": "SF Jazz Center",
        "city": "San Francisco",
        "state": "California",
        "price": 75,
        "category": "Social Events",
        "images": [
            "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800",
            "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400",
        "host": {
            "name": "David Williams",
            "title": "Event Producer",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David"
        },
        "freeCancellation": True,
        "rating": 4.9,
        "reviewCount": 234,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    
    # LEARNING & DEVELOPMENT ACTIVITIES
    {
        "title": "Public Speaking Mastery Workshop",
        "shortDescription": "Build confidence and master the art of public speaking",
        "longDescription": "Transform your public speaking skills through practical exercises, feedback, and proven techniques. Suitable for all levels from beginners to experienced presenters.",
        "activityTypeId": "learning",
        "formatId": "virtual",
        "minParticipants": 5,
        "maxParticipants": 15,
        "minDuration": 180,
        "maxDuration": 240,
        "preferredDuration": 210,
        "location": "Virtual",
        "city": "Online",
        "state": "California",
        "price": 120,
        "category": "Professional Development",
        "images": [
            "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800",
            "https://images.unsplash.com/photo-1560439513-74b037a25d84?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=400",
        "host": {
            "name": "Jennifer Lee",
            "title": "Communication Coach",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jennifer"
        },
        "freeCancellation": True,
        "rating": 4.9,
        "reviewCount": 167,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Data Analytics Bootcamp",
        "shortDescription": "Learn data analysis fundamentals with hands-on Python and SQL training",
        "longDescription": "Intensive 2-day bootcamp covering data analysis basics, Python programming, SQL queries, and data visualization. Perfect for professionals looking to add data skills to their toolkit.",
        "activityTypeId": "learning",
        "formatId": "in-person",
        "minParticipants": 8,
        "maxParticipants": 20,
        "minDuration": 480,
        "maxDuration": 600,
        "preferredDuration": 540,
        "location": "Tech Training Center",
        "city": "San Jose",
        "state": "California",
        "price": 450,
        "category": "Professional Development",
        "images": [
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
            "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400",
        "host": {
            "name": "Dr. Priya Sharma",
            "title": "Data Science Lead",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Priya"
        },
        "freeCancellation": False,
        "rating": 4.8,
        "reviewCount": 92,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    
    # WELLNESS ACTIVITIES
    {
        "title": "Mindfulness & Meditation for Professionals",
        "shortDescription": "Reduce stress and improve focus through guided mindfulness practices",
        "longDescription": "Learn practical mindfulness techniques designed for busy professionals. This session includes guided meditation, breathing exercises, and strategies for incorporating mindfulness into your daily routine.",
        "activityTypeId": "wellness",
        "formatId": "hybrid",
        "minParticipants": 5,
        "maxParticipants": 30,
        "minDuration": 60,
        "maxDuration": 90,
        "preferredDuration": 75,
        "location": "Zen Wellness Center",
        "city": "Palo Alto",
        "state": "California",
        "price": 40,
        "category": "Wellness",
        "images": [
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800",
            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400",
        "host": {
            "name": "Emma Thompson",
            "title": "Certified Mindfulness Instructor",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Emma"
        },
        "freeCancellation": True,
        "rating": 4.9,
        "reviewCount": 278,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Corporate Yoga & Wellness Session",
        "shortDescription": "Energize your team with a refreshing yoga and wellness experience",
        "longDescription": "This all-levels yoga session is designed specifically for workplace wellness. Includes stretching, breathing exercises, and relaxation techniques that can be practiced at the office.",
        "activityTypeId": "wellness",
        "formatId": "in-person",
        "minParticipants": 8,
        "maxParticipants": 25,
        "minDuration": 60,
        "maxDuration": 90,
        "preferredDuration": 75,
        "location": "Your Office or Local Studio",
        "city": "San Francisco",
        "state": "California",
        "price": 35,
        "category": "Wellness",
        "images": [
            "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=800",
            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400",
        "host": {
            "name": "Lisa Chen",
            "title": "Certified Yoga Instructor",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lisa"
        },
        "freeCancellation": True,
        "rating": 4.7,
        "reviewCount": 184,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    
    # CREATIVE WORKSHOPS
    {
        "title": "Pottery & Ceramics Team Workshop",
        "shortDescription": "Create unique pottery pieces while bonding with your team",
        "longDescription": "Explore your creative side in this hands-on pottery workshop. Learn wheel throwing or hand-building techniques and take home your own ceramic creations. No experience necessary!",
        "activityTypeId": "creative",
        "formatId": "in-person",
        "minParticipants": 6,
        "maxParticipants": 16,
        "minDuration": 120,
        "maxDuration": 180,
        "preferredDuration": 150,
        "location": "Artisan Pottery Studio",
        "city": "Berkeley",
        "state": "California",
        "price": 70,
        "category": "Arts & Culture",
        "images": [
            "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=800",
            "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400",
        "host": {
            "name": "Robert Kim",
            "title": "Master Potter",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert"
        },
        "freeCancellation": True,
        "rating": 4.8,
        "reviewCount": 145,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Corporate Improv Comedy Workshop",
        "shortDescription": "Boost creativity and communication through improv comedy exercises",
        "longDescription": "Learn improv techniques that improve quick thinking, active listening, and team collaboration. This fun, engaging workshop helps teams think outside the box and build confidence.",
        "activityTypeId": "creative",
        "formatId": "in-person",
        "minParticipants": 10,
        "maxParticipants": 30,
        "minDuration": 120,
        "maxDuration": 180,
        "preferredDuration": 150,
        "location": "Comedy Theater",
        "city": "San Francisco",
        "state": "California",
        "price": 55,
        "category": "Team Building",
        "images": [
            "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800",
            "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800"
        ],
        "thumbnailUrl": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=400",
        "host": {
            "name": "Rachel Davis",
            "title": "Improv Instructor & Comedian",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rachel"
        },
        "freeCancellation": True,
        "rating": 4.9,
        "reviewCount": 211,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

async def seed_all():
    """Seed all entities"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'drew_events')]
    
    print("🌱 Starting comprehensive seeding...")
    
    # Clear existing data
    print("\n📦 Clearing existing data...")
    await db.activity_types.delete_many({})
    await db.activity_formats.delete_many({})
    await db.occasions.delete_many({})
    await db.prerequisites.delete_many({})
    await db.offerings.delete_many({})
    await db.activities.delete_many({})
    
    # Seed activity types
    print("\n✅ Seeding Activity Types...")
    result = await db.activity_types.insert_many(activity_types)
    activity_type_ids = {
        "volunteering": str(result.inserted_ids[0]),
        "team-bonding": str(result.inserted_ids[1]),
        "employee-engagement": str(result.inserted_ids[2]),
        "learning": str(result.inserted_ids[3]),
        "wellness": str(result.inserted_ids[4]),
        "social": str(result.inserted_ids[5]),
        "creative": str(result.inserted_ids[6])
    }
    print(f"   Inserted {len(result.inserted_ids)} activity types")
    
    # Seed activity formats
    print("\n✅ Seeding Activity Formats...")
    result = await db.activity_formats.insert_many(activity_formats)
    format_ids = {
        "in-person": str(result.inserted_ids[0]),
        "virtual": str(result.inserted_ids[1]),
        "hybrid": str(result.inserted_ids[2])
    }
    print(f"   Inserted {len(result.inserted_ids)} activity formats")
    
    # Seed occasions
    print("\n✅ Seeding Occasions...")
    result = await db.occasions.insert_many(occasions)
    print(f"   Inserted {len(result.inserted_ids)} occasions")
    
    # Seed prerequisites
    print("\n✅ Seeding Pre-requisites...")
    result = await db.prerequisites.insert_many(prerequisites)
    prereq_ids = [str(id) for id in result.inserted_ids]
    print(f"   Inserted {len(result.inserted_ids)} pre-requisites")
    
    # Seed offerings
    print("\n✅ Seeding Offerings...")
    result = await db.offerings.insert_many(offerings)
    offering_ids = [str(id) for id in result.inserted_ids]
    print(f"   Inserted {len(result.inserted_ids)} offerings")
    
    # Update activities with real IDs and add itineraries
    print("\n✅ Seeding Activities with detailed data...")
    for i, activity in enumerate(activities):
        # Map type and format IDs
        activity['activityTypeId'] = activity_type_ids[activity['activityTypeId']]
        activity['formatId'] = format_ids[activity['formatId']]
        
        # Add some offerings and prerequisites
        activity['offerings'] = offering_ids[:3]  # First 3 offerings
        activity['preRequisites'] = [
            {
                "title": prerequisites[0]["name"],
                "icon": "ShieldCheck"
            },
            {
                "title": prerequisites[3]["name"],
                "icon": "Users"
            }
        ]
        
        # Add detailed itineraries based on activity type
        if "volunteering" in activity['activityTypeId']:
            activity['itineraries'] = [
                {
                    "image": activity['images'][0] if activity.get('images') else "",
                    "title": "Meet & Greet",
                    "description": "Meet the team and get briefed on the day's activities"
                },
                {
                    "image": activity['images'][1] if len(activity.get('images', [])) > 1 else "",
                    "title": "Main Activity",
                    "description": "Get hands-on with the volunteer work"
                },
                {
                    "image": activity['images'][2] if len(activity.get('images', [])) > 2 else "",
                    "title": "Wrap-up & Reflection",
                    "description": "Share experiences and celebrate the impact made"
                }
            ]
        else:
            activity['itineraries'] = [
                {
                    "image": activity['images'][0] if activity.get('images') else "",
                    "title": "Introduction",
                    "description": "Welcome and overview of the session"
                },
                {
                    "image": activity['images'][1] if len(activity.get('images', [])) > 1 else "",
                    "title": "Main Session",
                    "description": "Core activity and hands-on participation"
                },
                {
                    "image": activity['images'][2] if len(activity.get('images', [])) > 2 else "",
                    "title": "Q&A and Closing",
                    "description": "Questions, feedback, and next steps"
                }
            ]
        
        # Add included items
        activity['included'] = [
            {"icon": "MapPin", "title": "Venue access"},
            {"icon": "Coffee", "title": "Refreshments"},
            {"icon": "BookOpen", "title": "Materials provided"}
        ]
        
        # Add required items
        activity['required'] = [
            {"icon": "Clock", "title": "Arrive 10 minutes early"},
            {"icon": "Shirt", "title": "Comfortable attire"}
        ]
    
    result = await db.activities.insert_many(activities)
    print(f"   Inserted {len(result.inserted_ids)} activities")
    
    print("\n✨ Seeding complete!")
    print(f"\n📊 Summary:")
    print(f"   - Activity Types: {len(activity_types)}")
    print(f"   - Activity Formats: {len(activity_formats)}")
    print(f"   - Occasions: {len(occasions)}")
    print(f"   - Pre-requisites: {len(prerequisites)}")
    print(f"   - Offerings: {len(offerings)}")
    print(f"   - Activities: {len(activities)}")
    
    client.close()
    return len(activities)

if __name__ == "__main__":
    asyncio.run(seed_all())
