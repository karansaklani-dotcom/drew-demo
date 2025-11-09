"""Simple conversation example with the event discovery agent."""

import asyncio
import sys
sys.path.insert(0, '/app/agentic_backend')

from agents import EventDiscoveryAgent
from threads.manager import ThreadManager


async def main():
    """Run a simple conversation with the event discovery agent."""
    print("Initializing Event Discovery Agent...\n")
    
    # Initialize components
    thread_manager = ThreadManager()
    await thread_manager.initialize()
    
    agent = EventDiscoveryAgent()
    await agent.initialize()
    
    # Create a thread
    thread = await thread_manager.create_thread(
        agent_type="event_discovery",
        title="Event Discovery Demo"
    )
    
    print(f"Thread created: {thread.id}\n")
    
    # Conversation messages
    messages = [
        "Hi! I'm looking for events in San Francisco",
        "I'm interested in music and art events",
        "What concerts are happening this weekend?",
        "Can you recommend something under $50?"
    ]
    
    # Have conversation
    for i, message in enumerate(messages, 1):
        print(f"User ({i}): {message}")
        
        result = await agent.invoke(
            message=message,
            thread_id=thread.id,
            user_preferences={
                "interests": ["music", "art"],
                "location": "San Francisco",
                "price_range": [0, 50]
            }
        )
        
        print(f"Agent: {result.get('response', 'No response')}")
        print("-" * 80)
        print()
    
    # Get thread statistics
    thread = await thread_manager.get_thread(thread.id)
    print(f"\nThread Statistics:")
    print(f"  Messages: {thread.message_count}")
    print(f"  Total Tokens: {thread.total_token_count}")
    print(f"  Summaries: {thread.summary_count}")
    
    # Get thread context
    context = await thread_manager.get_context_for_agent(thread.id)
    print(f"\nThread Context Preview:")
    print(context[:500] + "..." if len(context) > 500 else context)
    
    # Cleanup
    await thread_manager.close()
    print("\nDemo completed!")


if __name__ == "__main__":
    asyncio.run(main())
