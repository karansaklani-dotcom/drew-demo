"""
Test the purely semantic search approach
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from semantic_search import SemanticSearchService
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_semantic_queries():
    """Test semantic search with comprehensive queries"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'drew_events')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ ERROR: OPENAI_API_KEY not found")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    
    semantic_search = SemanticSearchService(
        openai_api_key=openai_api_key,
        mongo_client=client,
        db_name=db_name
    )
    
    print("🧪 Testing Pure Semantic Search")
    print("=" * 70)
    
    # Test comprehensive queries with all requirements included
    test_queries = [
        {
            "query": "team building activities for 15 people in San Francisco",
            "description": "Basic team building with location and group size"
        },
        {
            "query": "volunteer opportunities for small groups in Oakland or Berkeley",
            "description": "Volunteering with location options"
        },
        {
            "query": "creative workshops for corporate teams in the Bay Area under $100 per person",
            "description": "Workshop with budget constraint"
        },
        {
            "query": "wellness and yoga activities for remote teams that can accommodate 20-30 people",
            "description": "Wellness with specific group size range"
        },
        {
            "query": "fun cooking class for team bonding in San Francisco for groups of 10-15",
            "description": "Cooking class with specific requirements"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['description']}")
        print(f"Query: '{query}'")
        print(f"{'='*70}\n")
        
        results = await semantic_search.semantic_search_activities(
            query=query,
            limit=3
        )
        
        if results:
            print(f"✅ Found {len(results)} activities:\n")
            for j, activity in enumerate(results, 1):
                print(f"  {j}. {activity.get('title')}")
                print(f"     Location: {activity.get('city')}, {activity.get('state')}")
                print(f"     Category: {activity.get('category')}")
                print(f"     Group Size: {activity.get('minParticipants')}-{activity.get('maxParticipants')} people")
                print(f"     Price: ${activity.get('price')}")
                print(f"     Similarity: {activity.get('similarity', 0):.4f}")
                print()
        else:
            print(f"❌ No results found\n")
    
    client.close()
    
    print("\n" + "=" * 70)
    print("✅ Semantic search testing complete!")
    print("\nKey Insight:")
    print("The semantic search understands the MEANING of the query,")
    print("not just keyword matching. Group size, location, and preferences")
    print("are encoded in the embedding and matched semantically.")

if __name__ == "__main__":
    asyncio.run(test_semantic_queries())
