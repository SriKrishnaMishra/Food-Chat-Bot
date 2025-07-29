"""
Test script to verify the FastAPI application works correctly
"""

import requests
import json
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = f"http://localhost:{os.getenv('SERVER_PORT', 8000)}"
    
    print("🧪 Testing Pandeyji Eatery API")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running.")
        print("   Run: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Detailed health check
    print("\n2. Testing detailed health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Detailed health check passed")
            print(f"   Database status: {health_data.get('database', 'unknown')}")
            print(f"   Active sessions: {health_data.get('active_sessions', 0)}")
        else:
            print(f"❌ Detailed health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Webhook endpoint with sample data
    print("\n3. Testing webhook endpoint...")
    try:
        # Sample Dialogflow webhook payload
        sample_payload = {
            "queryResult": {
                "intent": {
                    "displayName": "order.add - context: ongoing-order"
                },
                "parameters": {
                    "food-item": ["Pizza", "Biryani"],
                    "number": [2, 1]
                },
                "outputContexts": [
                    {
                        "name": "projects/test-project/agent/sessions/test-session-123/contexts/ongoing-order"
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{base_url}/",
            json=sample_payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook test passed")
            print(f"   Response: {result.get('fulfillmentText', 'No response text')}")
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
    
    print("\n🎉 API testing completed!")
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        import db_helper
        
        # Test getting next order ID
        next_id = db_helper.get_next_order_id()
        if next_id > 0:
            print(f"✅ Database connection successful (Next order ID: {next_id})")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 Pandeyji Eatery - System Test")
    print("=" * 50)
    
    # Test database first
    if not test_database_connection():
        print("\n💡 Tips to fix database issues:")
        print("1. Run: python interactive_setup.py")
        print("2. Make sure MySQL is running")
        print("3. Check your .env file credentials")
        return
    
    # Ask user if server is running
    print("\n❓ Is the server running? (python run.py)")
    response = input("Enter 'y' if server is running, or 'n' to skip API tests [n]: ").strip().lower()
    
    if response in ['y', 'yes']:
        test_api_endpoints()
    else:
        print("\n💡 To test the API:")
        print("1. Run: python run.py")
        print("2. In another terminal, run: python test_application.py")

if __name__ == "__main__":
    main()
