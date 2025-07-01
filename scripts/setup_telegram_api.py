#!/usr/bin/env python3
"""
Telegram API Setup Script
Helps users configure Telegram API credentials for chat reading functionality
"""

import os
import sys
import asyncio
from pathlib import Path

def setup_telegram_api():
    """Setup Telegram API credentials"""
    print("🔧 Telegram API Setup for Chat Reading")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please create one from env.template")
        return False
    
    print("\n📱 To read your Telegram chats, you need to get API credentials:")
    print("1. Go to https://my.telegram.org/auth")
    print("2. Log in with your phone number")
    print("3. Go to 'API Development Tools'")
    print("4. Create a new application")
    print("5. Copy the API ID and API Hash\n")
    
    # Get API credentials
    api_id = input("Enter your Telegram API ID: ").strip()
    api_hash = input("Enter your Telegram API Hash: ").strip()
    phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
    
    if not all([api_id, api_hash, phone]):
        print("❌ All fields are required!")
        return False
    
    # Update .env file
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        # Replace or add the new variables
        lines = content.split('\n')
        updated_lines = []
        
        # Track if we found the variables
        found_api_id = False
        found_api_hash = False
        found_phone = False
        
        for line in lines:
            if line.startswith('TELEGRAM_API_ID='):
                updated_lines.append(f'TELEGRAM_API_ID={api_id}')
                found_api_id = True
            elif line.startswith('TELEGRAM_API_HASH='):
                updated_lines.append(f'TELEGRAM_API_HASH={api_hash}')
                found_api_hash = True
            elif line.startswith('TELEGRAM_PHONE='):
                updated_lines.append(f'TELEGRAM_PHONE={phone}')
                found_phone = True
            else:
                updated_lines.append(line)
        
        # Add missing variables
        if not found_api_id:
            updated_lines.append(f'TELEGRAM_API_ID={api_id}')
        if not found_api_hash:
            updated_lines.append(f'TELEGRAM_API_HASH={api_hash}')
        if not found_phone:
            updated_lines.append(f'TELEGRAM_PHONE={phone}')
        
        # Write back to .env
        with open(".env", "w") as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ Telegram API credentials saved to .env file")
        
        # Test the credentials
        print("\n🧪 Testing API credentials...")
        if test_telegram_api(api_id, api_hash, phone):
            print("✅ API credentials are valid!")
            print("\n🚀 You can now use the following commands:")
            print("• /read_chats - Read and sync all your Telegram chats")
            print("• /contacts - View contacts from your chats")
            print("• /leads - View business leads")
            print("• /crm - CRM dashboard")
            print("• /insights - Business insights")
            return True
        else:
            print("❌ API credentials test failed. Please check your credentials.")
            return False
            
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_telegram_api(api_id: str, api_hash: str, phone: str) -> bool:
    """Test Telegram API credentials"""
    try:
        # Try to import telethon
        try:
            from telethon import TelegramClient
        except ImportError:
            print("❌ Telethon not installed. Installing...")
            os.system("pip install telethon")
            from telethon import TelegramClient
        
        # Create a test client
        client = TelegramClient('test_session', api_id, api_hash)
        
        # Try to connect
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(client.connect())
            if loop.run_until_complete(client.is_user_authorized()):
                print("✅ User already authorized")
                loop.run_until_complete(client.disconnect())
                return True
            else:
                print("📱 Sending authorization code...")
                loop.run_until_complete(client.send_code_request(phone))
                code = input("Enter the authorization code sent to your phone: ").strip()
                
                try:
                    loop.run_until_complete(client.sign_in(phone, code))
                    print("✅ Authorization successful!")
                    loop.run_until_complete(client.disconnect())
                    return True
                except Exception as e:
                    print(f"❌ Authorization failed: {e}")
                    return False
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_telegram_api()
    if success:
        print("\n🎉 Setup complete! You can now use chat reading features.")
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")
        sys.exit(1) 