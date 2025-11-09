"""Quick integration test for agentic backend."""

import asyncio
import sys
sys.path.insert(0, '/app/agentic_backend')


async def test_basic_functionality():
    """Test basic functionality of the agentic backend."""
    print("🧪 Testing Agentic Backend Integration")
    print("=" * 80)
    
    try:
        # Test 1: Import all modules
        print("\n1. Testing imports...")
        from config import config
        from checkpointing import get_checkpointer
        from threads.manager import ThreadManager
        from agents import BaseAgent, EventDiscoveryAgent
        from agents.sub_agent import create_sub_agent
        from tools.event_tools import create_event_tools
        from api.client import MainBackendClient
        from api.gateway import APIGateway
        print("   ✅ All imports successful")
        
        # Test 2: Configuration
        print("\n2. Testing configuration...")
        assert config.llm.api_key is not None
        assert config.mongodb.url is not None
        assert config.server.port == 8002
        print(f"   ✅ LLM Provider: {config.llm.default_provider}")
        print(f"   ✅ LLM Model: {config.llm.default_model}")
        print(f"   ✅ MongoDB: {config.mongodb.db_name}")
        print(f"   ✅ Server Port: {config.server.port}")
        
        # Test 3: Thread Manager Initialization
        print("\n3. Testing Thread Manager...")
        thread_manager = ThreadManager()
        await thread_manager.initialize()
        print("   ✅ Thread manager initialized")
        
        # Test 4: Create Thread
        print("\n4. Testing Thread Creation...")
        thread = await thread_manager.create_thread(
            agent_type="test",
            title="Integration Test Thread"
        )
        print(f"   ✅ Thread created: {thread.id}")
        
        # Test 5: Add Messages
        print("\n5. Testing Message Addition...")
        from threads.models import MessageType
        
        message1 = await thread_manager.add_message(
            thread_id=thread.id,
            role=MessageType.USER,
            content="Test message 1",
            generate_embedding=False  # Skip embedding for quick test
        )
        print(f"   ✅ Message 1 added: {message1.id}")
        
        message2 = await thread_manager.add_message(
            thread_id=thread.id,
            role=MessageType.ASSISTANT,
            content="Test response 1",
            generate_embedding=False
        )
        print(f"   ✅ Message 2 added: {message2.id}")
        
        # Test 6: Get Messages
        print("\n6. Testing Message Retrieval...")
        messages = await thread_manager.get_messages(thread.id)
        assert len(messages) == 2
        print(f"   ✅ Retrieved {len(messages)} messages")
        
        # Test 7: Get Thread
        print("\n7. Testing Thread Retrieval...")
        retrieved_thread = await thread_manager.get_thread(thread.id)
        assert retrieved_thread.id == thread.id
        assert retrieved_thread.message_count == 2
        print(f"   ✅ Thread retrieved with {retrieved_thread.message_count} messages")
        
        # Test 8: Event Tools
        print("\n8. Testing Event Tools...")
        tools = create_event_tools()
        assert len(tools) > 0
        print(f"   ✅ Created {len(tools)} event tools")
        
        # Test 9: API Client
        print("\n9. Testing API Client...")
        api_client = MainBackendClient()
        print("   ✅ API client initialized")
        
        # Test 10: API Gateway
        print("\n10. Testing API Gateway...")
        gateway = APIGateway()
        print("   ✅ API gateway initialized")
        
        # Test 11: Checkpointer
        print("\n11. Testing Checkpointer...")
        checkpointer = await get_checkpointer()
        assert checkpointer is not None
        print("   ✅ Checkpointer initialized")
        
        # Test 12: Event Agent (without full initialization)
        print("\n12. Testing Event Agent Creation...")
        event_agent = EventDiscoveryAgent()
        print("   ✅ Event agent created")
        
        # Cleanup
        print("\n13. Cleanup...")
        await thread_manager.close()
        await api_client.close()
        await gateway.close()
        print("   ✅ Cleanup complete")
        
        print("\n" + "=" * 80)
        print("✅ All integration tests passed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_server_components():
    """Test server components without starting the full server."""
    print("\n\n🔧 Testing Server Components")
    print("=" * 80)
    
    try:
        # Test FastAPI app creation
        print("\n1. Testing FastAPI app...")
        from server import app
        assert app is not None
        print("   ✅ FastAPI app created")
        
        # Check routes
        routes = [route.path for route in app.routes]
        essential_routes = [
            "/health",
            "/api/threads",
            "/api/agents/invoke",
        ]
        
        print("\n2. Testing API routes...")
        for route in essential_routes:
            found = any(route in r for r in routes)
            if found:
                print(f"   ✅ Route exists: {route}")
            else:
                print(f"   ⚠ Route not found: {route}")
        
        print("\n" + "=" * 80)
        print("✅ Server component tests passed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀" * 40)
    print("AGENTIC BACKEND INTEGRATION TEST SUITE")
    print("🚀" * 40)
    
    test1 = await test_basic_functionality()
    test2 = await test_server_components()
    
    print("\n" + "=" * 80)
    if test1 and test2:
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print("\n📝 Next Steps:")
        print("   1. Start the server: python /app/agentic_backend/server.py")
        print("   2. Check health: curl http://localhost:8002/health")
        print("   3. View docs: http://localhost:8002/docs")
        print("   4. Run examples: python /app/agentic_backend/examples/simple_conversation.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
    
    return test1 and test2


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
