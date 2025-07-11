#!/usr/bin/env python3
"""
Create New Google Spreadsheet
============================
This script creates a new Google Spreadsheet for the BD Analytics system
and sets it up with proper formatting and sharing.
"""

import os
import sys
import gspread
import asyncio
from pathlib import Path
from google.oauth2.service_account import Credentials
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.local_database_manager import get_local_db_manager
from core.sheets_sync_manager import get_sheets_sync_manager

async def create_new_spreadsheet():
    """Create a new Google Spreadsheet for BD Analytics"""
    
    print("🔄 Creating new Google Spreadsheet for BD Analytics...")
    
    try:
        # Check for service account file
        service_account_files = [
            'google_service_account.json',
            'service-account.json',
            'credentials.json'
        ]
        
        service_account_path = None
        for file_path in service_account_files:
            if Path(file_path).exists():
                service_account_path = file_path
                break
        
        if not service_account_path:
            print("❌ Google service account file not found!")
            print("   Please ensure you have one of these files:")
            for file_path in service_account_files:
                print(f"   - {file_path}")
            return None
        
        print(f"✅ Found service account file: {service_account_path}")
        
        # Set up credentials
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            service_account_path,
            scopes=scopes
        )
        
        client = gspread.authorize(credentials)
        
        # Create new spreadsheet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        spreadsheet_title = f"BD Analytics Dashboard - {timestamp}"
        
        print(f"📊 Creating spreadsheet: {spreadsheet_title}")
        spreadsheet = client.create(spreadsheet_title)
        
        # Get the new spreadsheet ID
        spreadsheet_id = spreadsheet.id
        
        print(f"✅ Created spreadsheet successfully!")
        print(f"   📋 Title: {spreadsheet_title}")
        print(f"   🔗 ID: {spreadsheet_id}")
        print(f"   🌐 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        
        # Initialize with basic structure
        try:
            # Rename the default sheet
            default_sheet = spreadsheet.sheet1
            default_sheet.update_title("📊 Dashboard Overview")
            
            # Add welcome message
            default_sheet.update('A1:B3', [
                ['🎉 BD Analytics Dashboard', ''],
                ['Created:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ['Status:', 'Ready for data sync']
            ])
            
            print("✅ Basic structure created")
            
        except Exception as e:
            print(f"⚠️ Could not set up basic structure: {e}")
        
        # Create .env file with new spreadsheet ID
        env_content = f"""# BD Analytics Environment Configuration
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Google Sheets Configuration
GOOGLE_SPREADSHEET_ID={spreadsheet_id}
GOOGLE_SERVICE_ACCOUNT_FILE={service_account_path}

# OpenAI Configuration (optional)
# OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
DATABASE_PATH=data/local_bd_database.db
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with new spreadsheet ID")
        
        # Test the connection
        print("\n🔄 Testing connection to new spreadsheet...")
        
        # Create sync manager with new credentials
        sync_manager = get_sheets_sync_manager(service_account_path, spreadsheet_id)
        sync_status = sync_manager.get_sync_status()
        
        if sync_status.get('spreadsheet_connected'):
            print("✅ Connection test successful!")
            
            # Try a quick sync to populate the spreadsheet
            print("\n🔄 Performing initial sync...")
            db_manager = await get_local_db_manager()
            
            # First create contacts from messages if they don't exist
            stats = await db_manager.get_database_stats()
            if stats.get('total_contacts', 0) == 0 and stats.get('total_messages', 0) > 0:
                print("📝 Creating contacts from imported messages...")
                contacts_created = await db_manager._create_contacts_from_messages()
                interactions_created = await db_manager._create_interactions_from_messages()
                print(f"   ✅ Created {contacts_created} contacts")
                print(f"   ✅ Created {interactions_created} interactions")
            
            # Perform sync
            sync_result = await sync_manager.full_sync(db_manager)
            
            if sync_result.get('success'):
                print(f"✅ Initial sync completed!")
                print(f"   📊 Records synced: {sync_result.get('total_records', 0)}")
                print(f"   📋 Tables synced: {len(sync_result.get('tables_synced', {}))}")
            else:
                print(f"⚠️ Initial sync had issues: {sync_result.get('error')}")
        else:
            print("⚠️ Connection test failed - you may need to share the spreadsheet manually")
        
        print(f"\n🎉 Setup Complete!")
        print(f"   🔗 Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print(f"   📁 Environment file: .env")
        print(f"\n📋 Next Steps:")
        print(f"   1. python run_analytics.py config    # Verify configuration")
        print(f"   2. python run_analytics.py dashboard # View analytics")
        print(f"   3. python run_analytics.py db-sync   # Sync latest data")
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
            'title': spreadsheet_title
        }
        
    except Exception as e:
        print(f"❌ Error creating spreadsheet: {e}")
        print(f"\n🔍 Troubleshooting:")
        print(f"   1. Ensure your service account file exists and is valid")
        print(f"   2. Check that the Google Sheets API is enabled")
        print(f"   3. Verify the service account has necessary permissions")
        return None

if __name__ == "__main__":
    result = asyncio.run(create_new_spreadsheet())
    if result:
        print(f"\n✅ Success! New spreadsheet created: {result['spreadsheet_id']}")
    else:
        print(f"\n❌ Failed to create spreadsheet") 