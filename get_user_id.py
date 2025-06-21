#!/usr/bin/env python3
"""
Quick script to get your Telegram User ID
"""

import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

async def get_user_id():
    """Get the current user's ID"""
    load_dotenv()
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Please set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file first")
        return
    
    try:
        # Convert api_id to int
        api_id = int(api_id)
        
        # Create client
        client = TelegramClient('session', api_id, api_hash)
        
        # Start client
        await client.start()
        
        # Get current user
        me = await client.get_me()
        
        if me:
            print(f"✅ Your Telegram User ID: {me.id}")
            print(f"👤 Username: @{me.username}")
            print(f"📱 Phone: {me.phone}")
            
            # Update .env file
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('USER_ID=your_telegram_user_id_here', f'USER_ID={me.id}')
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print(f"✅ Updated .env file with your User ID: {me.id}")
        else:
            print("❌ Could not get user information")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have the correct API_ID and API_HASH in your .env file")

if __name__ == "__main__":
    asyncio.run(get_user_id()) 