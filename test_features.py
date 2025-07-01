#!/usr/bin/env python3
"""
Test Bot Features
================
Test script to verify all bot features are working correctly.
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_API_ID', 
        'TELEGRAM_API_HASH',
        'TELEGRAM_PHONE'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing Module Imports...")
    
    try:
        from telegram_bot_optimized import OptimizedTelegramBot
        print("✅ telegram_bot_optimized imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import telegram_bot_optimized: {e}")
        return False
    
    try:
        from core.data_manager import DataManager
        print("✅ DataManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import DataManager: {e}")
        return False
    
    try:
        from core.ai_analyzer import AIAnalyzer
        print("✅ AIAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AIAnalyzer: {e}")
        return False
    
    return True

async def test_data_manager():
    """Test DataManager functionality"""
    print("\n🔍 Testing DataManager...")
    
    try:
        from core.data_manager import DataManager
        
        # Initialize data manager
        dm = DataManager()
        print("✅ DataManager initialized")
        
        # Test adding a message
        test_message = {
            'message_id': 12345,
            'chat_id': 67890,
            'chat_title': 'Test Chat',
            'user_id': 11111,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'message_text': 'This is a test message',
            'message_type': 'text',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        success, message = await dm.add_message(test_message)
        if success:
            print("✅ Message added successfully")
        else:
            print(f"❌ Failed to add message: {message}")
            return False
        
        # Test getting messages
        messages = await dm.get_messages(limit=5)
        print(f"✅ Retrieved {len(messages)} messages")
        
        # Test getting contacts
        contacts = await dm.get_contacts(limit=5)
        print(f"✅ Retrieved {len(contacts)} contacts")
        
        # Test adding a note
        success, message = await dm.add_note("Test note for outreach", category="outreach")
        if success:
            print("✅ Note added successfully")
        else:
            print(f"❌ Failed to add note: {message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ DataManager test failed: {e}")
        return False

async def test_ai_analyzer():
    """Test AIAnalyzer functionality"""
    print("\n🔍 Testing AIAnalyzer...")
    
    try:
        from core.data_manager import DataManager
        from core.ai_analyzer import AIAnalyzer
        
        dm = DataManager()
        analyzer = AIAnalyzer(dm)
        print("✅ AIAnalyzer initialized")
        
        # Test sentiment analysis
        test_text = "This is a positive message with great potential for collaboration."
        sentiment = await analyzer._analyze_sentiment(test_text)
        print(f"✅ Sentiment analysis: {sentiment}")
        
        # Test topic extraction
        topics = await analyzer._extract_topics(test_text)
        print(f"✅ Topic extraction: {topics}")
        
        return True
        
    except Exception as e:
        print(f"❌ AIAnalyzer test failed: {e}")
        return False

async def test_outreach_features():
    """Test outreach functionality"""
    print("\n🔍 Testing Outreach Features...")
    
    try:
        from telegram_bot_optimized import OptimizedTelegramBot
        
        # Initialize bot (without starting it)
        bot = OptimizedTelegramBot()
        print("✅ Bot initialized for testing")
        
        # Test outreach blurb generation
        test_contact = {
            'name': 'John Doe',
            'username': 'johndoe',
            'lead_score': 0.8,
            'category': 'High-Value Lead',
            'company': 'Tech Corp',
            'user_id': 12345
        }
        
        blurb = await bot._generate_outreach_blurb(test_contact)
        print(f"✅ Generated outreach blurb: {blurb['type']}")
        print(f"   Message: {blurb['message'][:50]}...")
        
        # Test follow-up action
        action = bot._get_followup_action(test_contact)
        print(f"✅ Follow-up action: {action}")
        
        return True
        
    except Exception as e:
        print(f"❌ Outreach features test failed: {e}")
        return False

def test_ollama():
    """Test Ollama backend"""
    print("\n🔍 Testing Ollama Backend...")
    
    try:
        import requests
        
        # Check if Ollama server is running
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
        else:
            print("❌ Ollama server error")
            return False
        
        # Check for required model
        models = response.json().get('models', [])
        required_model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        model_found = any(m.get('name') == required_model for m in models)
        if model_found:
            print(f"✅ Model {required_model} available")
        else:
            print(f"⚠️  Model {required_model} not found")
            print(f"   Pull with: ollama pull {required_model}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        print("   Make sure Ollama is installed and running: ollama serve")
        return False

def test_google_sheets():
    """Test Google Sheets integration"""
    print("\n🔍 Testing Google Sheets Integration...")
    
    try:
        from check_google_sheets import check_google_sheets
        
        # Check if Google Sheets credentials exist
        if os.path.exists('google_service_account.json'):
            print("✅ Google service account file found")
            
            # Try to check sheets (this will fail if not properly configured, but that's okay)
            try:
                check_google_sheets()
                print("✅ Google Sheets integration working")
            except Exception as e:
                print(f"⚠️  Google Sheets not fully configured: {e}")
                print("   This is normal if you haven't set up Google Sheets yet")
        else:
            print("⚠️  Google service account file not found")
            print("   This is normal if you're not using Google Sheets integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Bot Feature Tests...")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Module Imports", test_imports),
        ("Ollama Backend", test_ollama),
        ("DataManager", test_data_manager),
        ("AIAnalyzer", test_ai_analyzer),
        ("Outreach Features", test_outreach_features),
        ("Google Sheets", test_google_sheets)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to use.")
        print("\n🚀 Next Steps:")
        print("1. Run: python start_optimized_bot.py")
        print("2. In Telegram, send: /help")
        print("3. Use /read_chats to sync your chats")
        print("4. Use /outreach to generate outreach blurbs")
        print("5. Use /contacts and /leads to view your data")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("1. Make sure all environment variables are set in .env file")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Check that all required files exist")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 