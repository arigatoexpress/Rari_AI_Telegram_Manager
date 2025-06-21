#!/usr/bin/env python3
"""
Quick Test for Google Sheets and Chat History Features
=====================================================
"""

import os
from pathlib import Path

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup")
    print("=" * 40)
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        # Read key variables
        with open(env_file, 'r') as f:
            content = f.read()
            
        checks = [
            ("TELEGRAM_BOT_TOKEN", "Bot token configured"),
            ("GOOGLE_CLOUD_API_KEY", "Google API key configured"),
            ("GOOGLE_SERVICE_ACCOUNT_FILE", "Service account file configured"),
            ("ENCRYPTION_KEY", "Encryption key configured"),
            ("TELEGRAM_API_ID", "Telegram API ID configured"),
            ("TELEGRAM_API_HASH", "Telegram API hash configured")
        ]
        
        for var, description in checks:
            if var in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - Missing")
    else:
        print("❌ .env file not found")
    
    # Check service account file
    service_account = Path("google_service_account.json")
    if service_account.exists():
        print("✅ Service account JSON file exists")
    else:
        print("❌ Service account JSON file missing")
    
    # Check data directory
    data_dir = Path("data")
    if data_dir.exists():
        print("✅ Data directory exists")
    else:
        print("❌ Data directory missing")

def test_imports():
    """Test module imports"""
    print("\n📦 Testing Module Imports")
    print("=" * 40)
    
    try:
        from google_sheets_integration import GoogleSheetsManager
        print("✅ Google Sheets integration module")
    except ImportError as e:
        print(f"❌ Google Sheets integration: {e}")
    
    try:
        from chat_history_manager import ChatHistoryManager
        print("✅ Chat history manager module")
    except ImportError as e:
        print(f"❌ Chat history manager: {e}")
    
    try:
        import telethon
        print("✅ Telethon library")
    except ImportError as e:
        print(f"❌ Telethon library: {e}")
    
    try:
        from cryptography.fernet import Fernet
        print("✅ Cryptography library")
    except ImportError as e:
        print(f"❌ Cryptography library: {e}")

def test_google_sheets():
    """Test Google Sheets functionality"""
    print("\n📊 Testing Google Sheets")
    print("=" * 40)
    
    try:
        from google_sheets_integration import GoogleSheetsManager
        
        # Test creating manager
        manager = GoogleSheetsManager()
        print("✅ GoogleSheetsManager created successfully")
        
        # Test creating sheets
        try:
            briefs_sheet = manager.create_business_briefs_sheet()
            print("✅ Business Briefs sheet created/accessed")
        except Exception as e:
            print(f"⚠️  Business Briefs sheet: {e}")
        
        try:
            leads_sheet = manager.create_leads_sheet()
            print("✅ Lead Tracking sheet created/accessed")
        except Exception as e:
            print(f"⚠️  Lead Tracking sheet: {e}")
        
        try:
            analytics_sheet = manager.create_message_analytics_sheet()
            print("✅ Message Analytics sheet created/accessed")
        except Exception as e:
            print(f"⚠️  Message Analytics sheet: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
        return False

def test_encryption():
    """Test encryption functionality"""
    print("\n🔐 Testing Encryption")
    print("=" * 40)
    
    try:
        from chat_history_manager import ChatHistoryManager
        manager = ChatHistoryManager()
        
        # Test encryption/decryption
        test_data = "Hello, this is a test message!"
        encrypted = manager.encrypt_data(test_data)
        decrypted = manager.decrypt_data(encrypted)
        
        if test_data == decrypted:
            print("✅ Encryption/decryption working")
        else:
            print("❌ Encryption/decryption failed")
        
        # Test database
        stats = manager.get_database_stats()
        print(f"✅ Database stats: {stats}")
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")

def main():
    """Main test function"""
    print("🧪 Quick Test - Google Sheets & Chat History")
    print("=" * 50)
    
    test_environment()
    test_imports()
    test_google_sheets()
    test_encryption()
    
    print("\n🎯 Next Steps:")
    print("1. ✅ Google Sheet ID updated: 1joPGzc4KOf78Q_HKjo1q7S5yTWl0ypXcqG-Icit5IJE")
    print("2. Share the sheet with: tg-manager-bot@tgmanager-463607.iam.gserviceaccount.com")
    print("3. Test with: python test_google_sheets.py")
    print("4. Try bot commands in Telegram: /start, /generate, /brief")

if __name__ == "__main__":
    main() 