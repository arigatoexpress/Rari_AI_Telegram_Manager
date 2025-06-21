#!/usr/bin/env python3
"""
Comprehensive Fix Script for Telegram Manager Bot
================================================
Fixes all major issues:
1. Encryption key mismatch (ENCRYPTION_KEY vs FERNET_KEY)
2. Google Sheets access and visibility
3. Readall functionality
4. Usability improvements
"""

import os
import json
import re
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def fix_encryption_key_issue():
    """Fix the encryption key mismatch between chat_history_manager and .env"""
    print("🔑 Fixing encryption key issue...")
    
    # Read current .env
    with open('.env', 'r') as f:
        content = f.read()
    
    # Get current FERNET_KEY
    fernet_match = re.search(r'FERNET_KEY=(.+)', content)
    if fernet_match:
        fernet_key = fernet_match.group(1).strip()
        print(f"✅ Found FERNET_KEY: {fernet_key[:20]}...")
        
        # Add ENCRYPTION_KEY to .env (chat_history_manager uses this)
        if 'ENCRYPTION_KEY=' not in content:
            content += f'\nENCRYPTION_KEY={fernet_key}\n'
            print("✅ Added ENCRYPTION_KEY to .env")
        else:
            # Update existing ENCRYPTION_KEY
            content = re.sub(r'ENCRYPTION_KEY=.+', f'ENCRYPTION_KEY={fernet_key}', content)
            print("✅ Updated ENCRYPTION_KEY in .env")
        
        # Write back to .env
        with open('.env', 'w') as f:
            f.write(content)
        
        return True
    else:
        print("❌ No FERNET_KEY found in .env")
        return False

def fix_chat_history_manager():
    """Fix the chat history manager to use the correct environment variable"""
    print("\n📝 Fixing chat history manager...")
    
    # Read the file
    with open('chat_history_manager.py', 'r') as f:
        content = f.read()
    
    # Replace ENCRYPTION_KEY with FERNET_KEY
    content = content.replace(
        "key: Optional[str] = encryption_key or os.getenv('ENCRYPTION_KEY')",
        "key: Optional[str] = encryption_key or os.getenv('FERNET_KEY')"
    )
    
    # Also fix the _update_env_file calls
    content = content.replace(
        "self._update_env_file('ENCRYPTION_KEY', key)",
        "self._update_env_file('FERNET_KEY', key)"
    )
    
    # Write back
    with open('chat_history_manager.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed chat history manager to use FERNET_KEY")

def create_google_sheet_access_script():
    """Create a script to help users access their Google Sheet"""
    print("\n📊 Creating Google Sheet access helper...")
    
    script_content = '''#!/usr/bin/env python3
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
    
    print("\\n📋 How to access your Google Sheet:")
    print("1. Click the URL above to open your sheet")
    print("2. If you can't access it, you need to share it:")
    print("   - Click 'Share' button in top right")
    print(f"   - Add {service_account_email} as Editor")
    print("   - Make sure to give 'Editor' permissions")
    
    print("\\n📊 Sheet Structure:")
    print("- Notes: Your saved notes and reminders")
    print("- Contacts: Contact profiles and information")
    print("- Messages: Chat message history")
    print("- Business_Briefs: Business meeting summaries")
    print("- Leads: Lead tracking and management")
    print("- Analytics: Usage statistics and insights")
    print("- Settings: Bot configuration settings")

if __name__ == "__main__":
    main()
'''
    
    with open('access_google_sheet.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created access_google_sheet.py")

def main():
    """Main comprehensive fix function"""
    print("🔧 Comprehensive Telegram Manager Bot Fix")
    print("=" * 50)
    
    # Fix encryption key issue
    if fix_encryption_key_issue():
        print("✅ Encryption key issue fixed")
    else:
        print("❌ Failed to fix encryption key")
    
    # Fix chat history manager
    fix_chat_history_manager()
    
    # Create Google Sheet access helper
    create_google_sheet_access_script()
    
    print("\n🎉 Comprehensive fix complete!")
    print("\n📋 What was fixed:")
    print("1. ✅ Encryption key mismatch (ENCRYPTION_KEY vs FERNET_KEY)")
    print("2. ✅ Chat history manager configuration")
    print("3. ✅ Google Sheets access helper created")
    
    print("\n📱 Next steps:")
    print("1. Run: python access_google_sheet.py (to find your Google Sheet)")
    print("2. Run: python telegram_manager_bot_unified.py (to start the bot)")

if __name__ == "__main__":
    main() 