"""
Test script for AI integration in Novrintech Desktop Client
"""
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
import json

def test_ai_service():
    """Test AI service functionality"""
    print("🧪 Testing AI Service Integration...")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    
    # Test 1: Check application context
    print("\n1️⃣ Testing Application Context:")
    context = ai_service.get_application_context()
    print(f"✅ Application Name: {context['application_info']['name']}")
    print(f"✅ Version: {context['application_info']['version']}")
    print(f"✅ Features Count: {len(context['application_info']['features'])}")
    print(f"✅ API Endpoints: {len(context['application_info']['api_endpoints'])}")
    
    # Test 2: Check AI health
    print("\n2️⃣ Testing AI Backend Health:")
    health_result = ai_service.check_ai_health()
    if health_result["success"]:
        print(f"✅ AI Backend is online")
        print(f"✅ Status: {health_result.get('status', 'Unknown')}")
        print(f"✅ Response Time: {health_result.get('response_time', 0):.2f}s")
    else:
        print(f"❌ AI Backend is offline: {health_result['error']}")
    
    # Test 3: Test suggested questions
    print("\n3️⃣ Testing Suggested Questions:")
    questions = ai_service.get_suggested_questions()
    print(f"✅ Generated {len(questions)} suggested questions")
    for i, q in enumerate(questions[:3], 1):
        print(f"   {i}. {q}")
    
    # Test 4: Test quick help
    print("\n4️⃣ Testing Quick Help System:")
    help_topics = ["upload", "download", "shortcuts"]
    for topic in help_topics:
        help_text = ai_service.get_quick_help(topic)
        print(f"✅ Help for '{topic}': {len(help_text)} characters")
    
    # Test 5: Test AI message (if backend is available)
    if health_result["success"]:
        print("\n5️⃣ Testing AI Message Processing:")
        test_message = "What features does this application have?"
        print(f"📤 Sending: {test_message}")
        
        result = ai_service.send_message_to_ai(test_message, include_context=True)
        
        if result["success"]:
            print(f"✅ AI Response received ({len(result['response'])} characters)")
            print(f"📝 Preview: {result['response'][:100]}...")
        else:
            print(f"❌ AI Response failed: {result['error']}")
    else:
        print("\n5️⃣ Skipping AI Message Test (backend offline)")
    
    # Test 6: Test chat history
    print("\n6️⃣ Testing Chat History:")
    ai_service.add_to_ai_history("user", "Test message")
    ai_service.add_to_ai_history("assistant", "Test response")
    history = ai_service.get_ai_chat_history()
    print(f"✅ Chat history has {len(history)} messages")
    
    # Test 7: Test file operations
    print("\n7️⃣ Testing File Operations:")
    save_result = ai_service.save_ai_chat_history("test_ai_history.json")
    if save_result:
        print("✅ AI chat history saved successfully")
        
        load_result = ai_service.load_ai_chat_history("test_ai_history.json")
        if load_result:
            print("✅ AI chat history loaded successfully")
        else:
            print("❌ Failed to load AI chat history")
    else:
        print("❌ Failed to save AI chat history")
    
    print("\n" + "=" * 50)
    print("🎉 AI Service Integration Test Complete!")
    
    # Cleanup
    ai_service.stop_ai_keepalive()
    
    # Clean up test file
    try:
        os.remove("test_ai_history.json")
        print("🧹 Cleaned up test files")
    except:
        pass

def test_config_integration():
    """Test configuration integration"""
    print("\n🔧 Testing Configuration Integration...")
    print("=" * 50)
    
    try:
        from config import APP_CONTEXT, AI_API_URL, AI_ENDPOINTS
        
        print(f"✅ AI API URL: {AI_API_URL}")
        print(f"✅ AI Endpoints: {list(AI_ENDPOINTS.keys())}")
        print(f"✅ App Context Keys: {list(APP_CONTEXT.keys())}")
        print(f"✅ Features Count: {len(APP_CONTEXT['features'])}")
        print(f"✅ Components: {list(APP_CONTEXT['components'].keys())}")
        
        print("✅ Configuration integration successful!")
        
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

if __name__ == "__main__":
    print("🚀 Novrintech AI Integration Test Suite")
    print("Testing AI service integration and configuration...")
    
    try:
        test_config_integration()
        test_ai_service()
        
        print("\n🎯 All tests completed successfully!")
        print("\n💡 You can now run the main application with:")
        print("   python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\n🔧 Please check your configuration and try again.")
        import traceback
        traceback.print_exc()