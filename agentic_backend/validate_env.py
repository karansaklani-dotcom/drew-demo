#!/usr/bin/env python3
"""Environment validation script for agentic backend."""

import sys
import os
import asyncio
from pathlib import Path

# Add to path
sys.path.insert(0, '/app/agentic_backend')

from dotenv import load_dotenv

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

print("🔍 Validating Agentic Backend Environment")
print("=" * 80)

# Track validation results
all_valid = True

def validate(name, value, expected_type=str, optional=False):
    """Validate a configuration value."""
    global all_valid
    
    if value is None or value == "":
        if optional:
            print(f"⚠️  {name}: Not set (optional)")
            return True
        else:
            print(f"❌ {name}: Missing (required)")
            all_valid = False
            return False
    
    if expected_type == int:
        try:
            int(value)
            print(f"✅ {name}: {value}")
            return True
        except:
            print(f"❌ {name}: Invalid integer value: {value}")
            all_valid = False
            return False
    else:
        print(f"✅ {name}: {value}")
        return True


print("\n1️⃣  LLM Configuration")
print("-" * 80)

api_key = os.getenv('EMERGENT_LLM_KEY')
if api_key:
    print(f"✅ EMERGENT_LLM_KEY: {api_key[:20]}... (length: {len(api_key)})")
else:
    print("❌ EMERGENT_LLM_KEY: Missing (required)")
    all_valid = False

validate("DEFAULT_MODEL", os.getenv('DEFAULT_MODEL'))
validate("DEFAULT_PROVIDER", os.getenv('DEFAULT_PROVIDER'))
validate("EMBEDDING_MODEL", os.getenv('EMBEDDING_MODEL'))
validate("EMBEDDING_DIMENSIONS", os.getenv('EMBEDDING_DIMENSIONS'), int)


print("\n2️⃣  MongoDB Configuration")
print("-" * 80)

mongo_url = os.getenv('MONGO_URL')
validate("MONGO_URL", mongo_url)
validate("DB_NAME", os.getenv('DB_NAME'))

# Test MongoDB connection
if mongo_url:
    print("\n   Testing MongoDB connection...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        async def test_mongo():
            client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=3000)
            try:
                result = await client.admin.command('ping')
                print(f"   ✅ MongoDB connection successful: {result}")
                return True
            except Exception as e:
                print(f"   ❌ MongoDB connection failed: {e}")
                return False
            finally:
                client.close()
        
        if asyncio.run(test_mongo()):
            pass
        else:
            all_valid = False
    except Exception as e:
        print(f"   ❌ Error testing MongoDB: {e}")
        all_valid = False


print("\n3️⃣  Main Backend Configuration")
print("-" * 80)

validate("MAIN_BACKEND_URL", os.getenv('MAIN_BACKEND_URL'))
validate("MAIN_BACKEND_API_PREFIX", os.getenv('MAIN_BACKEND_API_PREFIX'))

# Test main backend connection
backend_url = os.getenv('MAIN_BACKEND_URL')
if backend_url:
    print(f"\n   Testing main backend connection...")
    try:
        import httpx
        
        async def test_backend():
            async with httpx.AsyncClient(timeout=3.0) as client:
                try:
                    api_prefix = os.getenv('MAIN_BACKEND_API_PREFIX', '/api')
                    url = f"{backend_url}{api_prefix}/"
                    response = await client.get(url)
                    if response.status_code < 500:
                        print(f"   ✅ Main backend reachable: {url} (status: {response.status_code})")
                        return True
                    else:
                        print(f"   ⚠️  Main backend returned error: {response.status_code}")
                        return True  # Still reachable
                except Exception as e:
                    print(f"   ⚠️  Main backend not reachable (may be offline): {e}")
                    return True  # Don't fail validation, might not be running
        
        asyncio.run(test_backend())
    except Exception as e:
        print(f"   ⚠️  Error testing backend: {e}")


print("\n4️⃣  Server Configuration")
print("-" * 80)

validate("AGENTIC_SERVER_HOST", os.getenv('AGENTIC_SERVER_HOST'))
validate("AGENTIC_SERVER_PORT", os.getenv('AGENTIC_SERVER_PORT'), int)


print("\n5️⃣  Thread Management Configuration")
print("-" * 80)

validate("MAX_TOKENS_PER_THREAD", os.getenv('MAX_TOKENS_PER_THREAD'), int)
validate("SUMMARIZATION_THRESHOLD", os.getenv('SUMMARIZATION_THRESHOLD'), int)
validate("MAX_MESSAGES_PER_THREAD", os.getenv('MAX_MESSAGES_PER_THREAD'), int)


print("\n6️⃣  Optional Configuration")
print("-" * 80)

validate("CORS_ORIGINS", os.getenv('CORS_ORIGINS'), optional=True)


print("\n7️⃣  Configuration Loading Test")
print("-" * 80)

try:
    from config import config
    print("✅ Config module loaded successfully")
    print(f"   - LLM Provider: {config.llm.default_provider}")
    print(f"   - LLM Model: {config.llm.default_model}")
    print(f"   - MongoDB DB: {config.mongodb.db_name}")
    print(f"   - Server Port: {config.server.port}")
    print(f"   - Summarization Threshold: {config.thread.summarization_threshold}")
except Exception as e:
    print(f"❌ Config module failed to load: {e}")
    all_valid = False


print("\n8️⃣  Dependencies Check")
print("-" * 80)

dependencies = [
    ('langgraph', 'LangGraph'),
    ('langgraph.checkpoint.mongodb.aio', 'LangGraph MongoDB'),
    ('motor', 'Motor (MongoDB async)'),
    ('fastapi', 'FastAPI'),
    ('httpx', 'HTTPX'),
    ('openai', 'OpenAI'),
    ('emergentintegrations', 'Emergent Integrations'),
    ('tiktoken', 'Tiktoken'),
]

missing_deps = []
for module, name in dependencies:
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError:
        print(f"❌ {name} - Not installed")
        missing_deps.append(name)
        all_valid = False

if missing_deps:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
    print("   Install with: pip install -r /app/agentic_backend/requirements.txt")


print("\n" + "=" * 80)

if all_valid:
    print("✅ ALL VALIDATION CHECKS PASSED")
    print("=" * 80)
    print("\n🚀 Your environment is properly configured!")
    print("\nNext steps:")
    print("   1. Start the server: cd /app/agentic_backend && python server.py")
    print("   2. Check health: curl http://localhost:8002/health")
    print("   3. View API docs: http://localhost:8002/docs")
    sys.exit(0)
else:
    print("❌ VALIDATION FAILED")
    print("=" * 80)
    print("\n⚠️  Please fix the issues above before starting the server.")
    print("\nFor help, see: /app/agentic_backend/ENV_SETUP_GUIDE.md")
    sys.exit(1)
