#!/usr/bin/env python3
"""
Test script for User Management System
Tests user registration, authentication, sessions, and chat functionality
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_user_registration():
    """Test user registration functionality"""
    print("🧪 Testing User Registration...")
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_users = [
        {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "testpass123",
            "subscription_tier": "free"
        },
        {
            "username": "testuser2", 
            "email": "test2@example.com",
            "password": "testpass456",
            "subscription_tier": "basic"
        }
    ]
    
    registered_users = []
    
    for user_data in test_users:
        try:
            response = requests.post(
                f"{base_url}/api/auth/register",
                json=user_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ User registered: {user_data['username']}")
                    registered_users.append({
                        'data': user_data,
                        'response': result
                    })
                else:
                    print(f"❌ Registration failed: {result.get('error')}")
            else:
                print(f"❌ Registration request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during registration: {e}")
    
    return registered_users

def test_user_authentication():
    """Test user authentication functionality"""
    print("\n🔐 Testing User Authentication...")
    
    base_url = "http://localhost:8000"
    
    # Test login with valid credentials
    test_credentials = {
        "username": "testuser1",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=test_credentials
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ User authentication successful")
                print(f"   Session token: {result['session_token'][:20]}...")
                print(f"   Expires at: {result['expires_at']}")
                return result['session_token']
            else:
                print(f"❌ Authentication failed: {result.get('error')}")
        else:
            print(f"❌ Authentication request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
    
    return None

def test_session_validation(session_token):
    """Test session validation"""
    print("\n🔍 Testing Session Validation...")
    
    if not session_token:
        print("❌ No session token available for testing")
        return False
    
    base_url = "http://localhost:8000"
    
    headers = {
        "Authorization": f"Bearer {session_token}"
    }
    
    try:
        # Test protected endpoint
        response = requests.get(
            f"{base_url}/api/auth/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Session validation successful")
            print(f"   Username: {result.get('username')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Subscription: {result.get('subscription_tier')}")
            return True
        else:
            print(f"❌ Session validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during session validation: {e}")
        return False

def test_chat_functionality(session_token):
    """Test chat functionality"""
    print("\n💬 Testing Chat Functionality...")
    
    if not session_token:
        print("❌ No session token available for testing")
        return False
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {session_token}"
    }
    
    try:
        # Start a conversation
        response = requests.post(
            f"{base_url}/api/chat/start",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                conversation_id = result['conversation_id']
                print(f"✅ Conversation started: {conversation_id}")
                
                # Send a message
                message_data = {
                    "content": "Hello, this is a test message!",
                    "conversation_id": conversation_id
                }
                
                response = requests.post(
                    f"{base_url}/api/chat/send",
                    headers=headers,
                    json=message_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print("✅ Message sent successfully")
                        
                        # Get conversation history
                        response = requests.get(
                            f"{base_url}/api/chat/history",
                            headers=headers,
                            params={"conversation_id": conversation_id}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('success'):
                                print(f"✅ Retrieved {result['total_messages']} messages")
                                return True
                            else:
                                print(f"❌ Failed to get history: {result.get('error')}")
                        else:
                            print(f"❌ History request failed: {response.status_code}")
                    else:
                        print(f"❌ Message sending failed: {result.get('error')}")
                else:
                    print(f"❌ Message request failed: {response.status_code}")
            else:
                print(f"❌ Conversation start failed: {result.get('error')}")
        else:
            print(f"❌ Conversation start request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during chat testing: {e}")
    
    return False

def test_user_stats(session_token):
    """Test user statistics and analytics"""
    print("\n📊 Testing User Statistics...")
    
    if not session_token:
        print("❌ No session token available for testing")
        return False
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {session_token}"
    }
    
    try:
        # Get user profile
        response = requests.get(
            f"{base_url}/api/auth/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            profile = response.json()
            print("✅ User profile retrieved")
            print(f"   Total documents: {profile.get('total_documents')}")
            print(f"   Total LLM calls: {profile.get('total_llm_calls')}")
            print(f"   Total tokens: {profile.get('total_tokens_processed')}")
            
            # Get activity summary
            response = requests.get(
                f"{base_url}/api/auth/activity",
                headers=headers
            )
            
            if response.status_code == 200:
                activity = response.json()
                if activity.get('success'):
                    print("✅ Activity summary retrieved")
                    print(f"   Recent documents: {activity.get('recent_documents')}")
                    print(f"   Activity counts: {activity.get('activity_counts')}")
                    return True
                else:
                    print(f"❌ Activity retrieval failed: {activity.get('error')}")
            else:
                print(f"❌ Activity request failed: {response.status_code}")
        else:
            print(f"❌ Profile request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during stats testing: {e}")
    
    return False

def test_logout(session_token):
    """Test user logout"""
    print("\n🚪 Testing User Logout...")
    
    if not session_token:
        print("❌ No session token available for testing")
        return False
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/logout",
            json={"session_token": session_token}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ User logged out successfully")
                return True
            else:
                print(f"❌ Logout failed: {result.get('error')}")
        else:
            print(f"❌ Logout request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during logout: {e}")
    
    return False

def main():
    """Main test function"""
    print("🚀 Testing User Management System...\n")
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/docs")
        print("✅ API is running")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
        print("Please start the API with: uvicorn app:app --reload")
        return False
    
    # Run tests
    print("\n" + "="*50)
    
    # Test registration
    registered_users = test_user_registration()
    
    if not registered_users:
        print("❌ No users registered, cannot continue testing")
        return False
    
    # Test authentication
    session_token = test_user_authentication()
    
    if not session_token:
        print("❌ Authentication failed, cannot continue testing")
        return False
    
    # Test session validation
    if not test_session_validation(session_token):
        print("❌ Session validation failed")
        return False
    
    # Test chat functionality
    if not test_chat_functionality(session_token):
        print("❌ Chat functionality failed")
        return False
    
    # Test user statistics
    if not test_user_stats(session_token):
        print("❌ User statistics failed")
        return False
    
    # Test logout
    if not test_logout(session_token):
        print("❌ Logout failed")
        return False
    
    print("\n" + "="*50)
    print("🎉 All user management tests passed!")
    print("\n📚 Next steps:")
    print("1. The user management system is working correctly")
    print("2. You can now integrate it with your chatbot")
    print("3. Users can register, authenticate, and maintain sessions")
    print("4. Chat history and user analytics are fully functional")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
