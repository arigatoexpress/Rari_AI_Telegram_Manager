#!/usr/bin/env python3
"""
Setup Manual Spreadsheet
========================
This script helps you configure a manually created Google Spreadsheet
for the BD Analytics system.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def get_service_account_email():
    """Extract service account email from the JSON file"""
    try:
        service_account_files = [
            'google_service_account.json',
            'service-account.json', 
            'credentials.json'
        ]
        
        for file_path in service_account_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get('client_email'), file_path
        
        return None, None
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        return None, None

def create_env_file(spreadsheet_id, service_account_path):
    """Create .env file with the provided spreadsheet ID"""
    env_content = f"""# BD Analytics Environment Configuration
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Google Sheets Configuration
GOOGLE_SPREADSHEET_ID={spreadsheet_id}
GOOGLE_SERVICE_ACCOUNT_FILE={service_account_path}

# OpenAI Configuration (add your key if you have one)
# OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
DATABASE_PATH=data/local_bd_database.db
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your spreadsheet ID")

async def test_spreadsheet_connection(spreadsheet_id, service_account_path):
    """Test connection to the spreadsheet"""
    try:
        from core.sheets_sync_manager import get_sheets_sync_manager
        
        print("\n🔄 Testing connection to your spreadsheet...")
        
        sync_manager = get_sheets_sync_manager(service_account_path, spreadsheet_id)
        sync_status = sync_manager.get_sync_status()
        
        if sync_status.get('spreadsheet_connected'):
            print("✅ Connection successful!")
            print(f"   📋 Spreadsheet: {sync_status.get('spreadsheet_title')}")
            print(f"   📊 Worksheets: {sync_status.get('worksheets_count', 0)}")
            return True
        else:
            print("❌ Could not connect to spreadsheet")
            print("   Make sure you shared the spreadsheet with the service account email")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def populate_spreadsheet(spreadsheet_id, service_account_path):
    """Populate the spreadsheet with data"""
    try:
        from core.local_database_manager import get_local_db_manager
        from core.sheets_sync_manager import get_sheets_sync_manager
        
        print("\n🔄 Populating spreadsheet with your data...")
        
        # Get database manager
        db_manager = await get_local_db_manager()
        
        # Create contacts from messages if they don't exist
        stats = await db_manager.get_database_stats()
        if stats.get('total_contacts', 0) == 0 and stats.get('total_messages', 0) > 0:
            print("📝 Creating contacts from imported messages...")
            contacts_created = await db_manager._create_contacts_from_messages()
            interactions_created = await db_manager._create_interactions_from_messages()
            print(f"   ✅ Created {contacts_created} contacts")
            print(f"   ✅ Created {interactions_created} interactions")
        
        # Sync to spreadsheet
        sync_manager = get_sheets_sync_manager(service_account_path, spreadsheet_id)
        sync_result = await sync_manager.full_sync(db_manager)
        
        if sync_result.get('success'):
            print("✅ Spreadsheet populated successfully!")
            print(f"   📊 Records synced: {sync_result.get('total_records', 0)}")
            print(f"   📋 Tables created: {len(sync_result.get('tables_synced', {}))}")
            
            # Show what was created
            tables_synced = sync_result.get('tables_synced', {})
            for table, result in tables_synced.items():
                if result.get('success'):
                    records = result.get('records_synced', 0)
                    print(f"      ✅ {table}: {records:,} records")
                else:
                    print(f"      ❌ {table}: {result.get('error', 'Unknown error')}")
            
            return True
        else:
            print(f"❌ Failed to populate spreadsheet: {sync_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error populating spreadsheet: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 Manual Google Spreadsheet Setup")
    print("=" * 50)
    
    # Get service account email
    service_email, service_account_path = get_service_account_email()
    
    if not service_email:
        print("❌ Could not find service account file!")
        print("   Please ensure you have google_service_account.json in this directory")
        return
    
    print(f"✅ Found service account: {service_email}")
    print(f"   📁 File: {service_account_path}")
    
    print("\n📋 Manual Setup Instructions:")
    print("1. Go to Google Sheets: https://sheets.google.com")
    print("2. Create a new blank spreadsheet")
    print("3. Name it something like 'BD Analytics Dashboard'")
    print("4. Click the 'Share' button")
    print(f"5. Add this email with Editor permissions: {service_email}")
    print("6. Copy the spreadsheet ID from the URL")
    print("   (The long string between /d/ and /edit in the URL)")
    
    print("\n" + "="*50)
    spreadsheet_id = input("📝 Paste your spreadsheet ID here: ").strip()
    
    if not spreadsheet_id:
        print("❌ No spreadsheet ID provided. Exiting.")
        return
    
    # Validate the ID format (basic check)
    if len(spreadsheet_id) < 20:
        print("⚠️ That doesn't look like a valid spreadsheet ID. Continuing anyway...")
    
    # Create .env file
    create_env_file(spreadsheet_id, service_account_path)
    
    # Test connection
    print(f"\n🔄 Testing spreadsheet access...")
    
    try:
        import asyncio
        connection_success = asyncio.run(test_spreadsheet_connection(spreadsheet_id, service_account_path))
        
        if connection_success:
            # Populate with data
            populate_success = asyncio.run(populate_spreadsheet(spreadsheet_id, service_account_path))
            
            if populate_success:
                print(f"\n🎉 Setup Complete!")
                print(f"   📊 Your spreadsheet is ready: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                print(f"   📁 Environment file created: .env")
                print(f"\n📋 Next Steps:")
                print(f"   1. python run_analytics.py config    # Verify everything")
                print(f"   2. python run_analytics.py dashboard # View your data")
                print(f"   3. python run_analytics.py db-sync   # Sync future updates")
            else:
                print(f"\n⚠️ Setup partially complete")
                print(f"   📊 Spreadsheet connected but data sync failed")
                print(f"   Try: python run_analytics.py db-sync")
        else:
            print(f"\n❌ Setup incomplete")
            print(f"   Make sure you shared the spreadsheet with: {service_email}")
            print(f"   Grant 'Editor' permissions to the service account")
            
    except ImportError:
        print(f"\n✅ Configuration created!")
        print(f"   📁 .env file created with your spreadsheet ID")
        print(f"   🔄 Run: python run_analytics.py config to test")

if __name__ == "__main__":
    main() 