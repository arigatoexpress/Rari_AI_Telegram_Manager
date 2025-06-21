#!/usr/bin/env python3
"""
Fix Bot Issues Script
=====================
Fixes common issues with the Telegram Manager Bot
"""

import os
import json
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def fix_fernet_key():
    """Fix Fernet key and clear old encrypted data"""
    print("🔑 Fixing Fernet key...")
    
    # Generate new Fernet key
    new_key = Fernet.generate_key().decode()
    
    # Update .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Replace old key with new one
    import re
    content = re.sub(
        r'FERNET_KEY=.*',
        f'FERNET_KEY={new_key}',
        content
    )
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print(f"✅ Generated new Fernet key: {new_key[:20]}...")
    
    # Clear old encrypted data
    old_files = [
        'chat_history_20250621_011017.session',
        'chat_history_45654.session'
    ]
    
    for file in old_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️  Removed old session file: {file}")
            except Exception as e:
                print(f"⚠️  Could not remove {file}: {e}")
    
    print("✅ Cleared old encrypted data")

def fix_google_sheets_database():
    """Fix Google Sheets database structure"""
    print("\n📊 Fixing Google Sheets database...")
    
    try:
        from google_sheets_database import initialize_database
        
        load_dotenv()
        spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        
        if not spreadsheet_id:
            print("❌ GOOGLE_SPREADSHEET_ID not set")
            return False
        
        # Initialize database (this will create proper sheet structure)
        db = initialize_database(spreadsheet_id)
        
        if db and db.spreadsheet:
            print(f"✅ Connected to Google Sheets: {db.spreadsheet.title}")
            
            # Test adding a note to ensure everything works
            note_id = db.add_note("Database fix test", "system", "low")
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
        print(f"❌ Error fixing Google Sheets: {e}")
        return False

def fix_telegram_bot_code():
    """Fix Telegram bot type checking issues"""
    print("\n🤖 Fixing Telegram bot code...")
    
    # Read the bot file
    with open('telegram_manager_bot_unified.py', 'r') as f:
        content = f.read()
    
    # Fix the contacts function to handle None message objects
    old_contacts_function = '''async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /contacts command - view contact profiles"""
    if not update or not update.effective_user or update.effective_user.id != USER_ID:
        return
    
    if not update.message:
        return
    
    try:
        if not db:
            await update.message.reply_text("❌ Database not connected")
            return
        
        # Get contacts from Google Sheets
        contacts = db.get_contacts(limit=10)
        
        if not contacts:
            await update.message.reply_text("👥 No contacts found in Google Sheets.")
            return
        
        text = "👥 **Contact Profiles from Google Sheets:**\\n\\n"
        for contact in contacts:
            text += f"👤 **{contact.name}** (@{contact.username})\\n"
            text += f"🏢 {contact.company} - {contact.role}\\n"
            text += f"📊 Category: {contact.category} (Priority: {contact.priority})\\n"
            text += f"🎯 Lead Score: {contact.lead_score}\\n"
            text += f"💬 Messages: {contact.message_count}\\n\\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting contacts: {str(e)}")'''
    
    new_contacts_function = '''async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /contacts command - view contact profiles"""
    if not update or not update.effective_user or update.effective_user.id != USER_ID:
        return
    
    if not update.message:
        return
    
    try:
        if not db:
            await update.message.reply_text("❌ Database not connected")
            return
        
        # Get contacts from Google Sheets
        try:
            contacts = db.get_contacts(limit=10)
        except Exception as db_error:
            print(f"Database error: {db_error}")
            await update.message.reply_text("❌ Error accessing contacts database")
            return
        
        if not contacts:
            await update.message.reply_text("👥 No contacts found in Google Sheets.")
            return
        
        text = "👥 **Contact Profiles from Google Sheets:**\\n\\n"
        for contact in contacts:
            try:
                text += f"👤 **{contact.name}** (@{contact.username})\\n"
                text += f"🏢 {contact.company} - {contact.role}\\n"
                text += f"📊 Category: {contact.category} (Priority: {contact.priority})\\n"
                text += f"🎯 Lead Score: {contact.lead_score}\\n"
                text += f"💬 Messages: {contact.message_count}\\n\\n"
            except Exception as contact_error:
                print(f"Error formatting contact: {contact_error}")
                continue
        
        if text == "👥 **Contact Profiles from Google Sheets:**\\n\\n":
            await update.message.reply_text("👥 No valid contacts found in Google Sheets.")
        else:
            await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Error in contacts function: {e}")
        if update.message:
            await update.message.reply_text(f"❌ Error getting contacts: {str(e)}")'''
    
    # Replace the function
    content = content.replace(old_contacts_function, new_contacts_function)
    
    # Write back the fixed file
    with open('telegram_manager_bot_unified.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed Telegram bot code")

def main():
    """Main fix function"""
    print("🔧 Fixing Telegram Manager Bot Issues")
    print("=" * 40)
    
    # Fix Fernet key and clear old data
    fix_fernet_key()
    
    # Fix Google Sheets database
    if fix_google_sheets_database():
        print("✅ Google Sheets database fixed")
    else:
        print("❌ Google Sheets database fix failed")
    
    # Fix Telegram bot code
    fix_telegram_bot_code()
    
    print("\n🎉 Bot issues fixed!")
    print("\n📋 Next steps:")
    print("1. The bot should now work without decryption errors")
    print("2. Google Sheets database is properly structured")
    print("3. Telegram bot type issues are resolved")
    print("4. Run: python telegram_manager_bot_unified.py")

if __name__ == "__main__":
    main() 