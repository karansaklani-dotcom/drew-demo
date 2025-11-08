# Seed script to populate events in MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mock_events = [
    {
        "title": "Lakehouse Jazz",
        "description": "Experience live jazz by the blue heron lake in the heart of the Golden Gate park.",
        "longDescription": "Immerse yourself in an evening of exceptional jazz music at the Hidden Boathouse, a unique and intimate venue nestled beside the serene blue heron lake in Golden Gate Park. This event brings together world-class musicians for an unforgettable night of smooth melodies and soulful performances.",
        "price": 35,
        "location": "Hidden Boathouse",
        "city": "San Francisco",
        "state": "California",
        "date": "2025-08-15",
        "rating": 4.83,
        "reviewCount": 1789,
        "category": "Performances",
        "host": {
            "name": "David",
            "title": "Music producer, composer and curator",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=David"
        },
        "images": [
            "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800&h=600&fit=crop"
        ],
        "included": [
            {"icon": "MapPin", "title": "Access to the Hidden Boathouse venue"},
            {"icon": "Music", "title": "Live jazz performances throughout the evening"},
            {"icon": "Wine", "title": "Complimentary welcome drink"},
            {"icon": "MapPin", "title": "Access to cash bar for additional beverages"},
            {"icon": "BookOpen", "title": "Program guide with artist information"}
        ],
        "required": [
            {"icon": "ShieldCheck", "title": "Must be 21+ years old"},
            {"icon": "CreditCard", "title": "Valid ID required for entry"},
            {"icon": "Footprints", "title": "Comfortable walking shoes recommended (venue requires short walk)"},
            {"icon": "Cloud", "title": "Weather-appropriate clothing (venue is partially outdoors)"}
        ],
        "itinerary": [
            {
                "image": "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=400&h=400&fit=crop",
                "title": "Arrive at boathouse",
                "description": "Get accurate directions and enjoy this hidden venue"
            },
            {
                "image": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=400&h=400&fit=crop",
                "title": "Settle in venue",
                "description": "Find a comfortable spot inside the boathouse."
            },
            {
                "image": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=400&h=400&fit=crop",
                "title": "Enjoy live music",
                "description": "Experience a variety of jazz genres from talented musicians."
            },
            {
                "image": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=400&h=400&fit=crop",
                "title": "Sip drinks",
                "description": "Relax with a glass of beer or wine."
            },
            {
                "image": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=400&h=400&fit=crop",
                "title": "Support local art",
                "description": "Contribute to the local artists scene and community."
            }
        ],
        "freeCancellation": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Underground Comedy Night",
        "description": "Stand-up comedy in an intimate speakeasy setting with craft cocktails.",
        "longDescription": "Join us for a night of laughter at our secret underground comedy venue. Featuring both established and up-and-coming comedians in an intimate setting.",
        "price": 45,
        "location": "The Laughing Vault",
        "city": "San Francisco",
        "state": "California",
        "date": "2025-08-20",
        "rating": 4.92,
        "reviewCount": 2341,
        "category": "Performances",
        "host": {
            "name": "Sarah",
            "title": "Comedy promoter and venue curator",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"
        },
        "images": [
            "https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1527224857830-43a7acc85260?w=800&h=600&fit=crop"
        ],
        "included": [
            {"icon": "MapPin", "title": "Access to secret venue location"},
            {"icon": "Smile", "title": "2-hour comedy show with multiple performers"},
            {"icon": "Wine", "title": "One complimentary craft cocktail"}
        ],
        "required": [
            {"icon": "ShieldCheck", "title": "Must be 18+ years old"},
            {"icon": "CreditCard", "title": "Valid ID required for entry"}
        ],
        "itinerary": [],
        "freeCancellation": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Rooftop Sunset Yoga",
        "description": "Flow through vinyasa sequences as the sun sets over the city skyline.",
        "longDescription": "Experience the magic of sunset yoga on a beautiful rooftop venue. Perfect for all levels, this session combines breathwork, movement, and meditation.",
        "price": 28,
        "location": "Sky Studio",
        "city": "San Francisco",
        "state": "California",
        "date": "2025-08-18",
        "rating": 4.95,
        "reviewCount": 892,
        "category": "Wellness",
        "host": {
            "name": "Maya",
            "title": "Certified yoga instructor",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Maya"
        },
        "images": [
            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&h=600&fit=crop"
        ],
        "included": [
            {"icon": "MapPin", "title": "Rooftop venue access"},
            {"icon": "Heart", "title": "90-minute guided yoga session"},
            {"icon": "Wine", "title": "Herbal tea and light refreshments"}
        ],
        "required": [
            {"icon": "Footprints", "title": "Bring your own yoga mat"},
            {"icon": "Cloud", "title": "Wear comfortable athletic clothing"}
        ],
        "itinerary": [],
        "freeCancellation": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Farm-to-Table Dinner Experience",
        "description": "Multi-course seasonal dinner prepared by award-winning chefs.",
        "longDescription": "Indulge in a carefully curated 5-course meal featuring locally sourced ingredients. Each dish is paired with wines from nearby vineyards.",
        "price": 125,
        "location": "Garden Terrace",
        "city": "Napa",
        "state": "California",
        "date": "2025-08-22",
        "rating": 4.88,
        "reviewCount": 1567,
        "category": "Food & Drink",
        "host": {
            "name": "Chef Marcus",
            "title": "Michelin-starred chef",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Marcus"
        },
        "images": [
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop"
        ],
        "included": [
            {"icon": "MapPin", "title": "Outdoor garden venue"},
            {"icon": "UtensilsCrossed", "title": "5-course seasonal menu"},
            {"icon": "Wine", "title": "Wine pairings with each course"}
        ],
        "required": [
            {"icon": "ShieldCheck", "title": "Must be 21+ years old"},
            {"icon": "Shirt", "title": "Smart casual dress code"}
        ],
        "itinerary": [],
        "freeCancellation": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Midnight Art Walk",
        "description": "Explore street art and galleries in the city's most vibrant neighborhood.",
        "longDescription": "Join us for a unique after-hours art experience. Discover hidden murals, meet local artists, and visit exclusive gallery openings.",
        "price": 35,
        "location": "Mission District",
        "city": "San Francisco",
        "state": "California",
        "date": "2025-08-25",
        "rating": 4.76,
        "reviewCount": 654,
        "category": "Arts & Culture",
        "host": {
            "name": "Alex",
            "title": "Art historian and curator",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex"
        },
        "images": [
            "https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800&h=600&fit=crop"
        ],
        "included": [
            {"icon": "MapPin", "title": "Guided walking tour"},
            {"icon": "Palette", "title": "Access to 4 exclusive galleries"},
            {"icon": "Wine", "title": "Wine and snacks at final stop"}
        ],
        "required": [
            {"icon": "Footprints", "title": "Comfortable walking shoes required"},
            {"icon": "Cloud", "title": "Dress for evening weather"}
        ],
        "itinerary": [],
        "freeCancellation": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "title": "Vinyl Listening Party",
        "description": "Deep dive into classic albums on audiophile-grade equipment.",
        "longDescription": "Experience music the way it was meant to be heard. We'll explore iconic albums on high-end turntables and speakers in an intimate setting.",
        "price": 20,
        "location": "Sound Sanctuary",
        "city": "Oakland",
        "state": "California",
        "date": "2025-08-28",
        "rating": 4.91,
        "reviewCount": 423,
        "category": "Performances",
        "host": {
            "name": "DJ Ray",
            "title": "Audiophile and music collector",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ray"
        },
        "images": [
            "https://images.unsplash.com/photo-1458560871784-56d23406c091?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=800&h=600&fit=crop"
        ],
        "included": [
            {"icon": "MapPin", "title": "Intimate listening room"},
            {"icon": "Music", "title": "3 full album playbacks"},
            {"icon": "Wine", "title": "Coffee and refreshments"}
        ],
        "required": [
            {"icon": "Volume2", "title": "Please respect quiet listening environment"}
        ],
        "itinerary": [],
        "freeCancellation": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

async def seed_events():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'drew_events')]
    
    # Clear existing events
    await db.events.delete_many({})
    
    # Insert mock events
    result = await db.events.insert_many(mock_events)
    print(f"Inserted {len(result.inserted_ids)} events")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_events())
