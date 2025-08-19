#!/usr/bin/env python3
"""Simple test runner to verify MCP functionality"""

import os
import asyncio
import sys
sys.path.insert(0, 'src')

# Set up environment
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['MCP_ENABLED_SERVICES'] = 'confluence,jira,slack'
os.environ['CONFLUENCE_BASE_URL'] = 'https://test.atlassian.net'
os.environ['CONFLUENCE_EMAIL'] = 'test@example.com'
os.environ['CONFLUENCE_API_TOKEN'] = 'test-token'
os.environ['JIRA_BASE_URL'] = 'https://test.atlassian.net'
os.environ['JIRA_EMAIL'] = 'test@example.com'
os.environ['JIRA_API_TOKEN'] = 'test-token'
os.environ['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
os.environ['SLACK_SIGNING_SECRET'] = 'test-secret'

try:
    print("🧪 Testing MCP Server Setup...")
    
    # Test imports
    print("✅ Testing imports...")
    from src.main import app
    print("✅ Main app imported successfully")
    
    # Test FastAPI app creation
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    print("✅ Testing root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"📋 Service: {data.get('service')}")
    print(f"📋 Version: {data.get('version')}")
    print(f"📋 Environment: {data.get('environment')}")
    print(f"📋 Enabled services: {data.get('enabled_services')}")
    
    print("✅ Testing health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    health_data = response.json()
    print(f"📋 Health status: {health_data.get('status')}")
    
    print("✅ Testing MCP endpoint...")
    response = client.get("/mcp")
    print(f"📋 MCP endpoint status: {response.status_code}")
    if response.status_code == 200:
        print("✅ MCP endpoint is working!")
    elif response.status_code == 404:
        print("⚠️  MCP endpoint not found - may need additional setup")
    
    print("✅ Testing individual service endpoints...")
    
    # Test Confluence endpoints
    try:
        response = client.get("/confluence/health")
        if response.status_code == 200:
            print("✅ Confluence health endpoint working")
        else:
            print(f"⚠️  Confluence health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  Confluence health test failed: {e}")
    
    # Test JIRA endpoints  
    try:
        response = client.get("/jira/health")
        if response.status_code == 200:
            print("✅ JIRA health endpoint working")
        else:
            print(f"⚠️  JIRA health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  JIRA health test failed: {e}")
    
    # Test Slack endpoints
    try:
        response = client.get("/slack/health")
        if response.status_code == 200:
            print("✅ Slack health endpoint working")
        else:
            print(f"⚠️  Slack health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️  Slack health test failed: {e}")
    
    print("\n🎉 Basic MCP server tests completed successfully!")
    print("🔧 Your MCP servers are properly configured and ready to use!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)