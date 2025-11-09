"""Semantic search demonstration."""

import asyncio
import sys
sys.path.insert(0, '/app/agentic_backend')

from threads.manager import ThreadManager
from threads.models import MessageType, ThreadSearchQuery


async def main():
    """Demonstrate semantic search on messages."""
    print("Semantic Search Demonstration\n")
    print("=" * 80)
    
    # Initialize
    thread_manager = ThreadManager()
    await thread_manager.initialize()
    
    # Create thread
    thread = await thread_manager.create_thread(
        agent_type="event_discovery",
        title="Music Event Search"
    )
    
    print(f"Thread: {thread.id}\n")
    
    # Add sample messages
    sample_messages = [
        "I love jazz music and want to find concerts",
        "Looking for rock concerts in San Francisco",
        "Are there any classical music performances?",
        "I prefer outdoor music festivals",
        "What about indie bands playing at small venues?",
        "Electronic dance music events would be great",
        "I enjoy acoustic performances at coffee shops"
    ]
    
    print("Adding messages to thread...")
    for msg in sample_messages:
        await thread_manager.add_message(
            thread_id=thread.id,
            role=MessageType.USER,
            content=msg,
            generate_embedding=True
        )
        print(f"  ✓ {msg[:50]}...")
    
    print("\n" + "=" * 80)
    
    # Perform semantic searches
    search_queries = [
        "jazz performances",
        "outdoor festivals",
        "small venue shows"
    ]
    
    for query_text in search_queries:
        print(f"\nSearching for: '{query_text}'")
        print("-" * 80)
        
        results = await thread_manager.semantic_search(
            ThreadSearchQuery(
                query=query_text,
                thread_id=thread.id,
                limit=3,
                similarity_threshold=0.6
            )
        )
        
        if results:
            print(f"Found {len(results)} relevant messages:\n")
            for i, result in enumerate(results, 1):
                score = result['similarity_score']
                content = result['content']
                print(f"{i}. [Score: {score:.3f}] {content}")
        else:
            print("No relevant messages found")
    
    # Cleanup
    await thread_manager.close()
    print("\n" + "=" * 80)
    print("Semantic search demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
