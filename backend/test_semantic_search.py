"""
Test semantic search functionality
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from semantic_search import SemanticSearchService
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_search(query: str, semantic_search: SemanticSearchService):
    """Test a search query"""
    print(f"\n🔍 Testing query: '{query}'")
    
    results = await semantic_search.semantic_search_activities(
        query=query,
        limit=5
    )
    
    print(f"✅ Found {len(results)} activities")
    for i, activity in enumerate(results, 1):
        print(f"\n   {i}. {activity.get('title')}")
        print(f"      Category: {activity.get('category')}")
        print(f"      Location: {activity.get('city')}, {activity.get('state')}")
        if 'similarity' in activity:
            print(f"      Similarity: {activity['similarity']:.4f}")
    
    return results

async def main():
    print("🧪 Testing Semantic Search")
    
    # Get configuration
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'drew_events')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return
    
    # Initialize MongoDB client
    client = AsyncIOMotorClient(mongo_url)
    
    # Initialize semantic search service
    semantic_search = SemanticSearchService(
        openai_api_key=openai_api_key,
        mongo_client=client,
        db_name=db_name
    )
    
    # Test queries
    test_queries = [
        "team building activities in San Francisco",
        "volunteer opportunities",
        "wellness and yoga",
        "cooking class for teams",
        "escape room challenge"
    ]
    
    for query in test_queries:
        await test_search(query, semantic_search)
    
    client.close()
    print("\n✅ All tests complete!")

if __name__ == "__main__":
    asyncio.run(main())
