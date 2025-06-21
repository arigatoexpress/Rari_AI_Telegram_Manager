#!/usr/bin/env python3
"""
Manual Google Sheets Setup
=========================
Helps you set up Google Sheets manually and test the connection
"""

import os
from dotenv import load_dotenv

def main():
    """Main setup function"""
    print("📊 Manual Google Sheets Setup")
    print("=" * 40)
    
    print("\n📋 Step 1: Create a Google Sheet manually")
    print("1. Go to https://sheets.google.com/")
    print("2. Click '+' to create a new spreadsheet")
    print("3. Name it 'Telegram Manager Bot Data'")
    print("4. Copy the URL from your browser")
    print("   It should look like: https://docs.google.com/spreadsheets/d/1ABC123.../edit")
    
    print("\n📋 Step 2: Get the Spreadsheet ID")
    print("From the URL, copy the part between /d/ and /edit")
    print("Example: https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit")
    print("Spreadsheet ID would be: 1ABC123DEF456")
    
    print("\n📋 Step 3: Share the Sheet")
    print(f"1. Click 'Share' button in the top right")
    print(f"2. Add this email as Editor:")
    print(f"   tgmanager@tgmanager-463607.iam.gserviceaccount.com")
    print(f"3. Make sure to give 'Editor' permissions")
    
    print("\n📋 Step 4: Update your .env file")
    spreadsheet_id = input("\nEnter your Spreadsheet ID: ").strip()
    
    if spreadsheet_id:
        update_env_file(spreadsheet_id)
        test_connection(spreadsheet_id)
    else:
        print("❌ No spreadsheet ID provided")

def update_env_file(spreadsheet_id):
    """Update .env file with Google Sheet ID"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual spreadsheet ID
        if 'GOOGLE_SPREADSHEET_ID=your_google_spreadsheet_id_here' in content:
            content = content.replace(
                'GOOGLE_SPREADSHEET_ID=your_google_spreadsheet_id_here',
                f'GOOGLE_SPREADSHEET_ID={spreadsheet_id}'
            )
        else:
            # If the placeholder is not found, replace any existing value
            import re
            content = re.sub(
                r'GOOGLE_SPREADSHEET_ID=.*',
                f'GOOGLE_SPREADSHEET_ID={spreadsheet_id}',
                content
            )
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated .env file with Google Sheet ID: {spreadsheet_id}")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

def test_connection(spreadsheet_id):
    """Test Google Sheets connection"""
    print(f"\n🧪 Testing connection to spreadsheet: {spreadsheet_id}")
    
    try:
        from google_sheets_database import initialize_database
        
        load_dotenv()
        
        db = initialize_database(spreadsheet_id)
        
        if db and db.spreadsheet:
            print(f"✅ Connected to Google Sheets: {db.spreadsheet.title}")
            print(f"📋 Database URL: {db.get_spreadsheet_url()}")
            
            # Test adding a note
            note_id = db.add_note("Test note from setup script", "setup", "low")
            if note_id:
                print(f"✅ Test note added successfully (ID: {note_id})")
                print("\n🎉 Google Sheets setup complete!")
                print(f"📊 Your bot data will be stored in: {db.get_spreadsheet_url()}")
                print("\n📋 Next steps:")
                print("1. Get your Telegram API credentials from https://my.telegram.org/")
                print("2. Update TELEGRAM_API_ID and TELEGRAM_API_HASH in .env")
                print("3. Run: python telegram_manager_bot_unified.py")
                return True
            else:
                print("❌ Failed to add test note")
                return False
        else:
            print("❌ Failed to connect to Google Sheets")
            print("Make sure you:")
            print("1. Created the Google Sheet")
            print("2. Shared it with: tgmanager@tgmanager-463607.iam.gserviceaccount.com")
            print("3. Gave Editor permissions")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        print("Make sure you:")
        print("1. Created the Google Sheet")
        print("2. Shared it with: tgmanager@tgmanager-463607.iam.gserviceaccount.com")
        print("3. Gave Editor permissions")
        return False

if __name__ == "__main__":
    main() 