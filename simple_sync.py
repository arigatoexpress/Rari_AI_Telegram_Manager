#!/usr/bin/env python3
"""
Simple Chat History Sync
=======================
Syncs your Telegram chat history to the database
"""

import os
import asyncio
from dotenv import load_dotenv
from chat_history_manager import ChatHistoryManager

async def sync_history():
    """Sync chat history"""
    load_dotenv()
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    user_id = os.getenv('USER_ID')
    
    if not all([api_id, api_hash, user_id]):
        print("❌ Missing Telegram credentials in .env")
        print("Please set TELEGRAM_API_ID, TELEGRAM_API_HASH, and USER_ID")
        return
    
    print("📥 Starting chat history sync...")
    print("📱 You'll receive a Telegram code - enter it when prompted")
    
    try:
        manager = ChatHistoryManager()
        
        # Fetch history (we know these are not None due to the check above)
        result = manager.fetch_full_chat_history(
            api_id=str(api_id),
            api_hash=str(api_hash),
            phone=str(user_id),  # Using user_id as phone for simplicity
            limit=1000  # Reasonable limit
        )
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return
        
        if not result.get('messages'):
            print("❌ No messages found")
            return
        
        # Store in database
        success = manager.store_encrypted_history(result)
        
        if success:
            print(f"✅ Successfully synced {len(result['messages'])} messages")
            print("💡 You can now use /readall in the bot")
        else:
            print("❌ Failed to store messages")
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    asyncio.run(sync_history()) 