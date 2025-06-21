#!/usr/bin/env python3
"""
Google Sheets Setup Helper
=========================
Helps you set up Google Sheets integration for the Telegram Manager Bot
"""

import os
import json
from dotenv import load_dotenv

def check_google_service_account():
    """Check if Google service account file exists"""
    possible_names = [
        "google_service_account.json",
        "NEWtgmanager-463607-f239aa9518f0 copy.json",
        "tgmanager-463607-f239aa9518f0.json",
        "service-account.json"
    ]
    
    for filename in possible_names:
        if os.path.exists(filename):
            print(f"✅ Found Google service account file: {filename}")
            return filename
    
    print("❌ Google service account file not found")
    print("\n📋 Please download your service account JSON file:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Navigate to 'IAM & Admin' > 'Service Accounts'")
    print("3. Find: tgmanager@tgmanager-463607.iam.gserviceaccount.com")
    print("4. Click on it > 'Keys' tab > 'Add Key' > 'Create new key' > 'JSON'")
    print("5. Download and save as 'google_service_account.json' in this directory")
    return None

def validate_service_account_file(filename):
    """Validate the service account JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ Invalid service account file. Missing fields: {missing_fields}")
            return False
        
        print(f"✅ Valid service account file for project: {data.get('project_id', 'Unknown')}")
        print(f"📧 Service account email: {data.get('client_email', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        return False

def create_google_sheet():
    """Create a new Google Sheet for the bot"""
    print("\n📊 Creating Google Sheet for bot data...")
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Load credentials with proper scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        creds = Credentials.from_service_account_file(
            'google_service_account.json',
            scopes=scopes
        )
        
        # Create client
        client = gspread.authorize(creds)
        
        # Create new spreadsheet
        spreadsheet = client.create('Telegram Manager Bot Data')
        
        # Get the spreadsheet ID
        spreadsheet_id = spreadsheet.id
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        print(f"✅ Created Google Sheet: {spreadsheet.title}")
        print(f"🔗 URL: {spreadsheet_url}")
        print(f"🆔 ID: {spreadsheet_id}")
        
        # Update .env file
        update_env_file(spreadsheet_id)
        
        return spreadsheet_id, spreadsheet_url
        
    except Exception as e:
        print(f"❌ Error creating Google Sheet: {e}")
        print("\n🔧 To fix this, you need to:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Navigate to 'APIs & Services' > 'Enabled APIs'")
        print("3. Click '+ ENABLE APIS AND SERVICES'")
        print("4. Search for and enable:")
        print("   - Google Sheets API")
        print("   - Google Drive API")
        print("5. Go to 'IAM & Admin' > 'Service Accounts'")
        print("6. Click on your service account")
        print("7. Go to 'Permissions' tab")
        print("8. Click 'Grant Access'")
        print("9. Add these roles:")
        print("   - Editor (for Google Sheets)")
        print("   - Editor (for Google Drive)")
        print("10. Or create a Google Sheet manually and share it with:")
        print(f"    tgmanager@tgmanager-463607.iam.gserviceaccount.com")
        return None, None

def update_env_file(spreadsheet_id):
    """Update .env file with Google Sheet ID"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual spreadsheet ID
        content = content.replace(
            'GOOGLE_SPREADSHEET_ID=your_google_spreadsheet_id_here',
            f'GOOGLE_SPREADSHEET_ID={spreadsheet_id}'
        )
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated .env file with Google Sheet ID: {spreadsheet_id}")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

def test_google_sheets_connection():
    """Test Google Sheets connection"""
    print("\n🧪 Testing Google Sheets connection...")
    
    try:
        from google_sheets_database import initialize_database
        
        load_dotenv()
        spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        
        if not spreadsheet_id:
            print("❌ GOOGLE_SPREADSHEET_ID not set in .env")
            return False
        
        db = initialize_database(spreadsheet_id)
        
        if db and db.spreadsheet:
            print(f"✅ Connected to Google Sheets: {db.spreadsheet.title}")
            print(f"📋 Database URL: {db.get_spreadsheet_url()}")
            
            # Test adding a note
            note_id = db.add_note("Test note from setup script", "setup", "low")
            if note_id:
                print(f"✅ Test note added successfully (ID: {note_id})")
                return True
            else:
                print("❌ Failed to add test note")
                return False
        else:
            print("❌ Failed to connect to Google Sheets")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Google Sheets Setup for Telegram Manager Bot")
    print("=" * 50)
    
    # Check for service account file
    service_account_file = check_google_service_account()
    
    if not service_account_file:
        return
    
    # Validate service account file
    if not validate_service_account_file(service_account_file):
        return
    
    # Rename to standard name if needed
    if service_account_file != "google_service_account.json":
        try:
            os.rename(service_account_file, "google_service_account.json")
            print(f"✅ Renamed {service_account_file} to google_service_account.json")
        except Exception as e:
            print(f"❌ Error renaming file: {e}")
            return
    
    # Create Google Sheet
    spreadsheet_id, spreadsheet_url = create_google_sheet()
    
    if not spreadsheet_id:
        return
    
    # Test connection
    if test_google_sheets_connection():
        print("\n🎉 Google Sheets setup complete!")
        print(f"📊 Your bot data will be stored in: {spreadsheet_url}")
        print("\n📋 Next steps:")
        print("1. Get your Telegram API credentials from https://my.telegram.org/")
        print("2. Update TELEGRAM_API_ID and TELEGRAM_API_HASH in .env")
        print("3. Run: python telegram_manager_bot_unified.py")
    else:
        print("\n❌ Google Sheets setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 