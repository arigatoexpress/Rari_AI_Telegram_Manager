#!/usr/bin/env python3
"""
Google Sheet Access Helper
=========================
Helps you find and access your Google Sheet
"""

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    service_account_email = "tgmanager@tgmanager-463607.iam.gserviceaccount.com"
    
    if not spreadsheet_id:
        print("❌ GOOGLE_SPREADSHEET_ID not set in .env")
        return
    
    print("📊 Your Google Sheet Information:")
    print("=" * 40)
    print(f"🆔 Spreadsheet ID: {spreadsheet_id}")
    print(f"🔗 Direct URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print(f"📧 Service Account: {service_account_email}")
    
    print("\n📋 How to access your Google Sheet:")
    print("1. Click the URL above to open your sheet")
    print("2. If you can't access it, you need to share it:")
    print("   - Click 'Share' button in top right")
    print(f"   - Add {service_account_email} as Editor")
    print("   - Make sure to give 'Editor' permissions")
    
    print("\n📊 Sheet Structure:")
    print("- Notes: Your saved notes and reminders")
    print("- Contacts: Contact profiles and information")
    print("- Messages: Chat message history")
    print("- Business_Briefs: Business meeting summaries")
    print("- Leads: Lead tracking and management")
    print("- Analytics: Usage statistics and insights")
    print("- Settings: Bot configuration settings")

if __name__ == "__main__":
    main()
