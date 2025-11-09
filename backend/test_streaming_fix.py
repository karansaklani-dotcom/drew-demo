"""
Test the streaming endpoint with fixes
"""
import requests
import json

backend_url = "http://localhost:8001"

# Step 1: Register user
print("🔐 Registering user...")
import random
test_email = f"stream_test_{random.randint(10000,99999)}@example.com"
register_response = requests.post(
    f"{backend_url}/api/user/register",
    json={
        "email": test_email,
        "username": f"stream_tester_{random.randint(1000,9999)}",
        "password": "test123",
        "firstName": "Stream",
        "lastName": "Tester"
    }
)

if register_response.status_code != 201:
    print(f"❌ Registration failed: {register_response.text}")
    exit(1)

auth_data = register_response.json()
token = auth_data.get('token')
user_id = auth_data.get('user', {}).get('_id')
print(f"✅ User created: {user_id}")

# Step 2: Create project
print("\n📁 Creating project...")
project_response = requests.post(
    f"{backend_url}/api/project",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "name": "Test Streaming Project",
        "description": "Testing message streaming"
    }
)

if project_response.status_code != 201:
    print(f"❌ Project creation failed: {project_response.text}")
    exit(1)

project_data = project_response.json()
project_id = project_data.get('_id') or project_data.get('id')
print(f"✅ Project created: {project_id}")

# Step 3: Test streaming endpoint
print("\n🔄 Testing streaming endpoint...")
print("=" * 60)

stream_url = f"{backend_url}/api/project/{project_id}/chat/stream"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "prompt": "I need 3 fun team building activities in San Francisco",
    "userId": user_id
}

response = requests.post(stream_url, headers=headers, json=payload, stream=True)

if response.status_code != 200:
    print(f"❌ Streaming failed: {response.text}")
    exit(1)

print("✅ Streaming started...\n")

agent_state_count = 0
message_chunks = []
recommendation_count = 0
agent_runs = {}

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            try:
                data = json.loads(line_str[6:])  # Skip 'data: ' prefix
                event_type = data.get('type')
                
                if event_type == 'start':
                    print(f"🚀 {data.get('message')}")
                
                elif event_type == 'agent_state':
                    state = data.get('state', {})
                    agent = state.get('agent')
                    status = state.get('status')
                    message = state.get('message', '')
                    
                    # Track agent runs
                    if agent not in agent_runs:
                        agent_runs[agent] = []
                    agent_runs[agent].append(status)
                    
                    agent_state_count += 1
                    print(f"   [{agent}] {message}")
                
                elif event_type == 'project_update':
                    print(f"\n📋 Project updated: {data.get('name')}")
                    print(f"   Description: {data.get('description')}")
                
                elif event_type == 'message_chunk':
                    chunk = data.get('chunk', '')
                    message_chunks.append(chunk)
                    print(chunk, end='', flush=True)
                
                elif event_type == 'complete':
                    recommendation_count = data.get('recommendationCount', 0)
                    print(f"\n\n✅ Complete! Recommendations: {recommendation_count}")
                
                elif event_type == 'error':
                    print(f"\n❌ Error: {data.get('error')}")
            
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON decode error: {e}")

print("\n" + "=" * 60)
print(f"📊 Summary:")
print(f"   Agent state updates: {agent_state_count}")
print(f"   Message chunks received: {len(message_chunks)}")
print(f"   Full message length: {len(''.join(message_chunks))} chars")
print(f"   Recommendations: {recommendation_count}")

# Check for duplicate execution
print(f"\n🔍 Agent execution analysis:")
for agent, statuses in agent_runs.items():
    print(f"   {agent}: {len(statuses)} states")
    if statuses.count('completed') > 1:
        print(f"      ⚠️  WARNING: Agent completed {statuses.count('completed')} times (duplicate execution!)")
    else:
        print(f"      ✅ No duplicates")

if len(message_chunks) == 0:
    print(f"\n⚠️  WARNING: No message chunks received!")
else:
    print(f"\n✅ Message streaming working!")
    print(f"\nFull message:\n{' '.join(message_chunks)[:200]}...")
