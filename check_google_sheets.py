#!/usr/bin/env python3
"""
Check and fix Google Sheets configuration
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def check_google_sheets():
    """Check Google Sheets configuration and connectivity"""
    print("🔍 Checking Google Sheets Configuration")
    print("=" * 50)
    
    # Check environment variables
    credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'google_service_account.json')
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    print(f"📁 Credentials file: {credentials_file}")
    print(f"📊 Spreadsheet ID: {spreadsheet_id}")
    
    # Check if files exist
    if not os.path.exists(credentials_file):
        print("❌ Credentials file not found!")
        print("Please download your Google Service Account JSON file and save it as 'google_service_account.json'")
        return False
    
    if not spreadsheet_id:
        print("❌ Spreadsheet ID not configured!")
        print("Please set GOOGLE_SHEETS_SPREADSHEET_ID in your .env file")
        return False
    
    # Test Google Sheets API
    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Test connection by getting spreadsheet info
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        print("✅ Google Sheets connection successful!")
        print(f"📋 Spreadsheet title: {spreadsheet['properties']['title']}")
        
        # List existing sheets
        sheets = spreadsheet.get('sheets', [])
        print(f"📄 Existing worksheets: {len(sheets)}")
        
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"   • {sheet_name}")
        
        # Create required worksheets if they don't exist
        required_sheets = ['Messages', 'Contacts', 'Notes', 'Analyses']
        existing_sheet_names = [sheet['properties']['title'] for sheet in sheets]
        
        missing_sheets = [sheet for sheet in required_sheets if sheet not in existing_sheet_names]
        
        if missing_sheets:
            print(f"\n📝 Creating missing worksheets: {', '.join(missing_sheets)}")
            
            requests = []
            for sheet_name in missing_sheets:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 26
                            }
                        }
                    }
                })
            
            if requests:
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': requests}
                ).execute()
                
                print("✅ Missing worksheets created successfully!")
        
        # Add headers to worksheets
        print("\n📋 Adding headers to worksheets...")
        
        headers = {
            'Messages': ['ID', 'Message ID', 'Chat ID', 'Chat Title', 'User ID', 'Username', 'First Name', 'Last Name', 'Message Text', 'Message Type', 'Timestamp', 'Sentiment Score', 'Keywords', 'Is Duplicate', 'Synced At'],
            'Contacts': ['User ID', 'Username', 'Name', 'Message Count', 'Lead Score', 'Category', 'Company', 'Role', 'Industry', 'Last Message Date', 'Synced At'],
            'Notes': ['ID', 'Text', 'Timestamp', 'Category', 'Priority', 'Tags', 'Completed', 'Synced At'],
            'Analyses': ['Chat ID', 'Chat Title', 'Sentiment Score', 'Key Topics', 'Business Opportunities', 'Recommendations', 'Message Count', 'Participants', 'Timestamp', 'Synced At']
        }
        
        for sheet_name, header_row in headers.items():
            try:
                # Check if headers already exist
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A1:Z1"
                ).execute()
                
                if not result.get('values') or not result['values'][0]:
                    # Add headers
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f"{sheet_name}!A1",
                        valueInputOption='RAW',
                        body={'values': [header_row]}
                    ).execute()
                    print(f"✅ Added headers to {sheet_name}")
                else:
                    print(f"ℹ️  Headers already exist in {sheet_name}")
                    
            except Exception as e:
                print(f"⚠️  Could not add headers to {sheet_name}: {e}")
        
        print(f"\n🔗 Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print("✅ Google Sheets configuration is ready!")
        return True
        
    except HttpError as e:
        print(f"❌ Google Sheets API error: {e}")
        if e.resp.status == 404:
            print("   The spreadsheet ID might be incorrect or you don't have access")
        elif e.resp.status == 403:
            print("   Permission denied. Check your service account permissions")
        return False
        
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return False

if __name__ == "__main__":
    success = check_google_sheets()
    if success:
        print("\n🎉 Google Sheets is properly configured!")
        print("Your bot can now sync data to Google Sheets.")
    else:
        print("\n❌ Google Sheets configuration needs attention.")
        print("Please fix the issues above and try again.") 