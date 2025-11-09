"""Sub-agent demonstration."""

import asyncio
import sys
sys.path.insert(0, '/app/agentic_backend')

from agents import EventDiscoveryAgent
from agents.sub_agent import create_sub_agent
from threads.manager import ThreadManager
from threads.models import MessageType


async def main():
    """Demonstrate sub-agent functionality."""
    print("Sub-Agent Demonstration\n")
    print("=" * 80)
    
    # Initialize components
    thread_manager = ThreadManager()
    await thread_manager.initialize()
    
    main_agent = EventDiscoveryAgent()
    await main_agent.initialize()
    
    # Create parent thread
    parent_thread = await thread_manager.create_thread(
        agent_type="event_discovery",
        title="Main Event Planning Thread"
    )
    
    print(f"Parent Thread: {parent_thread.id}\n")
    
    # Main agent handles initial request
    print("Main Agent: Planning a weekend music festival...")
    result = await main_agent.invoke(
        message="Help me plan a weekend music festival trip",
        thread_id=parent_thread.id
    )
    print(f"Response: {result.get('response', '')}\n")
    
    # Create sub-agent for venue finding
    print("Creating sub-agent for venue search...")
    venue_agent = await create_sub_agent(
        agent_type="venue_finder",
        parent_thread_id=parent_thread.id,
        system_message="You are a venue finding specialist. Help find suitable venues for events."
    )
    
    print(f"Sub-Agent Thread: {venue_agent.subthread_id}\n")
    
    # Execute subtask
    print("Sub-Agent: Finding venues with capacity > 500...")
    venue_result = await venue_agent.execute_subtask(
        task_description="Find music venues in the area with capacity greater than 500 people"
    )
    print(f"Response: {venue_result.get('response', '')}\n")
    
    # Merge context back to parent
    print("Merging sub-agent results to parent thread...")
    await venue_agent.merge_context_to_parent(
        summary="Found several suitable venues with capacity > 500"
    )
    
    # Get parent thread messages to see merged content
    parent_messages = await thread_manager.get_messages(parent_thread.id)
    print(f"\nParent thread now has {len(parent_messages)} messages")
    
    # Show merged messages
    print("\nMessages with sub-agent content:")
    for msg in parent_messages:
        if msg.metadata.get('is_subagent_response') or msg.metadata.get('is_subagent_summary'):
            print(f"  - {msg.role}: {msg.content[:100]}...")
    
    # Cleanup
    await thread_manager.close()
    print("\nSub-agent demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
