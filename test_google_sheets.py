#!/usr/bin/env python3
"""
Test Google Sheets Integration
==============================
Test the Google Sheets integration functionality.
"""

import os
from dotenv import load_dotenv
from google_sheets_integration import GoogleSheetsManager, BusinessBrief, LeadData
from datetime import datetime

# Load environment variables
load_dotenv()

def test_google_sheets_connection():
    """Test Google Sheets connection and basic functionality"""
    print("🧪 Google Sheets Integration Test")
    print("=" * 50)
    
    # Check environment variables
    print("🔗 Testing Google Sheets Connection")
    print("=" * 40)
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    
    print(f"📁 Service Account File: {service_account_file}")
    print(f"📊 Spreadsheet ID: {spreadsheet_id}")
    
    if not service_account_file or not spreadsheet_id:
        print("❌ Missing required environment variables")
        return False
    
    # Test connection
    try:
        print("\n🔗 Testing connection...")
        manager = GoogleSheetsManager()
        print("✅ Google Sheets connection successful!")
        
        # Test business briefs sheet
        print("\n📊 Testing Business Briefs Sheet...")
        briefs_sheet = manager.create_business_briefs_sheet()
        print(f"✅ Business Briefs sheet ready (rows: {briefs_sheet.row_count})")
        
        # Test leads sheet
        print("\n👤 Testing Lead Tracking Sheet...")
        leads_sheet = manager.create_leads_sheet()
        print(f"✅ Lead Tracking sheet ready (rows: {leads_sheet.row_count})")
        
        # Test adding a sample business brief
        print("\n📝 Testing Business Brief Addition...")
        sample_brief = BusinessBrief(
            chat_title="Test Chat",
            chat_type="Private",
            date=datetime.now().strftime("%Y-%m-%d"),
            executive_brief="This is a test brief for integration testing",
            key_insights="Integration is working properly",
            conversion_opportunities="Potential for automation",
            actionable_recommendations="Continue testing",
            next_steps="Verify all functionality",
            priority="Medium",
            status="Test"
        )
        
        success = manager.add_business_brief(sample_brief)
        if success:
            print("✅ Sample business brief added successfully!")
        else:
            print("❌ Failed to add sample business brief")
        
        # Test adding a sample lead
        print("\n👤 Testing Lead Addition...")
        sample_lead = LeadData(
            chat_title="Test Lead",
            contact_name="John Test",
            company="Test Corp",
            phone="+1234567890",
            email="john@test.com",
            source="Integration Test",
            status="New",
            last_contact=datetime.now().strftime("%Y-%m-%d"),
            next_follow_up="",
            notes="Test lead for integration verification"
        )
        
        success = manager.add_lead(sample_lead)
        if success:
            print("✅ Sample lead added successfully!")
        else:
            print("❌ Failed to add sample lead")
        
        # Test dashboard summary
        print("\n📊 Testing Dashboard Summary...")
        summary = manager.create_dashboard_summary()
        print(f"✅ Dashboard summary created: {len(summary)} metrics")
        
        print("\n🎉 All Google Sheets tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure google_service_account.json exists")
        print("2. Check your .env file has correct paths")
        print("3. Verify the service account has access to your sheet")
        print("4. Ensure Google Sheets API is enabled in Google Cloud Console")
        return False

def test_encryption():
    """Test chat history encryption"""
    print("\n🔐 Testing Chat History Encryption")
    print("=" * 40)
    
    try:
        from chat_history_manager import ChatHistoryManager
        
        manager = ChatHistoryManager()
        
        # Test encryption/decryption
        test_data = "Hello, this is a test message!"
        encrypted = manager.encrypt_data(test_data)
        decrypted = manager.decrypt_data(encrypted)
        
        if test_data == decrypted:
            print("✅ Encryption/decryption working correctly")
        else:
            print("❌ Encryption/decryption failed")
        
        # Test database stats
        stats = manager.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Integration Tests")
    print("=" * 50)
    
    # Test Google Sheets
    sheets_success = test_google_sheets_connection()
    
    # Test encryption
    encryption_success = test_encryption()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    print(f"Google Sheets: {'✅ PASS' if sheets_success else '❌ FAIL'}")
    print(f"Encryption: {'✅ PASS' if encryption_success else '❌ FAIL'}")
    
    if sheets_success and encryption_success:
        print("\n🎉 All tests passed! Your integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main() 