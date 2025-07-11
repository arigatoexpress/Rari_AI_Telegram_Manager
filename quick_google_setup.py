#!/usr/bin/env python3
"""
Quick Google Sheets Setup
=========================
Simplified script to upload your leads to Google Sheets using your personal account
"""

import os
from pathlib import Path

def check_setup():
    """Check if setup is ready"""
    print("🔍 Checking setup...")
    
    # Check for credentials
    if not Path("credentials.json").exists():
        print("❌ credentials.json not found")
        print("\n📋 Please:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Google Sheets API + Drive API")
        print("3. Create OAuth 2.0 credentials (Desktop application)")
        print("4. Download and save as 'credentials.json' in this folder")
        return False
    
    # Check for leads database
    if not Path("data/telegram_leads.db").exists():
        print("❌ Leads database not found")
        print("📋 Please run: python analyze_telegram_leads.py")
        return False
    
    print("✅ Setup looks good!")
    return True

def main():
    print("🚀 Quick Google Sheets Setup")
    print("=" * 40)
    
    if not check_setup():
        return
    
    print("\n🔄 Starting upload to your personal Google account...")
    
    # Import and run the personal sheets manager
    from setup_personal_google_sheets import PersonalGoogleSheetsManager
    
    manager = PersonalGoogleSheetsManager()
    
    # Authenticate
    if manager.authenticate():
        print("\n📊 Creating spreadsheet...")
        spreadsheet_id = manager.create_leads_spreadsheet()
        
        if spreadsheet_id:
            print("\n📤 Uploading your leads data...")
            if manager.upload_leads_data(spreadsheet_id):
                print("\n🎉 SUCCESS! Your leads are now in Google Sheets!")
                print(f"🔗 Open: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            else:
                print("❌ Upload failed")
        else:
            print("❌ Spreadsheet creation failed")
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    main() 