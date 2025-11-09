"""
Generate embeddings for all activities in the database
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from semantic_search import SemanticSearchService
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def main():
    print("🔄 Starting embedding generation...")
    
    # Get configuration
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'drew_events')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return
    
    print(f"📊 Database: {db_name}")
    print(f"🔗 MongoDB URL: {mongo_url}")
    
    # Initialize MongoDB client
    client = AsyncIOMotorClient(mongo_url)
    
    # Initialize semantic search service
    semantic_search = SemanticSearchService(
        openai_api_key=openai_api_key,
        mongo_client=client,
        db_name=db_name
    )
    
    # Ensure indexes
    print("\n📑 Ensuring search indexes...")
    await semantic_search.ensure_indexes()
    
    # Generate embeddings for all activities
    print("\n🧠 Generating embeddings for activities...")
    count = await semantic_search.batch_generate_embeddings(collection_name="activities")
    
    print(f"\n✅ Successfully generated {count} embeddings")
    
    # Verify
    db = client[db_name]
    total = await db.activities.count_documents({})
    with_embeddings = await db.activities.count_documents({"embedding": {"$exists": True}})
    
    print(f"\n📊 Verification:")
    print(f"   Total activities: {total}")
    print(f"   Activities with embeddings: {with_embeddings}")
    print(f"   Coverage: {(with_embeddings/total*100 if total > 0 else 0):.1f}%")
    
    # Show sample
    sample = await db.activities.find_one({"embedding": {"$exists": True}})
    if sample:
        print(f"\n✨ Sample activity:")
        print(f"   Title: {sample.get('title')}")
        print(f"   Embedding dimensions: {len(sample.get('embedding', []))}")
        print(f"   Embedding text: {sample.get('embeddingText', 'N/A')[:100]}...")
    
    client.close()
    print("\n🎉 Embedding generation complete!")

if __name__ == "__main__":
    asyncio.run(main())
