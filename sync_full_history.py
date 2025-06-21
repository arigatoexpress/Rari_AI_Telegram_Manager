#!/usr/bin/env python3
"""
sync_full_history.py
====================
Fetch all historical messages from a Telegram chat (or all chats) using a user account (not bot),
and store them encrypted in the local database for use by the Telegram Manager Bot.

Usage:
  python sync_full_history.py --api-id <id> --api-hash <hash> --phone <phone> [--chat <chat_id>] [--limit <n>]

Example:
  python sync_full_history.py --api-id 123456 --api-hash abcd1234 --phone +1234567890 --chat @mygroup
"""
import argparse
import asyncio
from chat_history_manager import ChatHistoryManager
import os

async def sync_history_async(api_id, api_hash, phone, chat_id=None, limit=100000):
    """Async function to sync chat history"""
    from telethon import TelegramClient
    
    print(f"📥 Fetching history for chat: {chat_id or 'ALL CHATS'} (limit: {limit})")
    
    # Create client
    session_name = f"chat_history_{os.getpid()}"
    client = TelegramClient(session_name, int(api_id), api_hash)
    
    try:
        # Connect and authenticate
        await client.connect()
        if not await client.is_user_authorized():
            print("🔐 Authentication required. Check your phone for Telegram code.")
            await client.send_code_request(phone)
            code = input("Enter the code from Telegram: ")
            await client.sign_in(phone, code)
        
        # Fetch messages
        messages = []
        if chat_id:
            # Fetch from specific chat
            entity = await client.get_entity(chat_id)
            async for message in client.iter_messages(entity, limit=limit):
                if message.text:
                    messages.append({
                        'id': message.id,
                        'sender_id': message.sender_id,
                        'sender_name': _get_sender_name(message),
                        'text': message.text,
                        'date': message.date.isoformat(),
                        'chat_id': str(chat_id)
                    })
        else:
            # Fetch from all dialogs
            async for dialog in client.iter_dialogs():
                print(f"📥 Syncing chat: {dialog.name}")
                chat_messages = []
                async for message in client.iter_messages(dialog, limit=limit//10):
                    if message.text:
                        chat_messages.append({
                            'id': message.id,
                            'sender_id': message.sender_id,
                            'sender_name': _get_sender_name(message),
                            'text': message.text,
                            'date': message.date.isoformat(),
                            'chat_id': str(dialog.id)
                        })
                if chat_messages:
                    messages.extend(chat_messages)
                    print(f"   ✅ Added {len(chat_messages)} messages from {dialog.name}")
        
        await client.disconnect()
        return messages
        
    except Exception as e:
        print(f"❌ Error fetching chat history: {e}")
        try:
            await client.disconnect()
        except:
            pass
        return []

def _get_sender_name(message):
    """Extract sender name from message"""
    try:
        if message.sender:
            if hasattr(message.sender, 'first_name'):
                return f"{message.sender.first_name} {message.sender.last_name or ''}".strip()
            elif hasattr(message.sender, 'title'):
                return message.sender.title
        return "Unknown"
    except:
        return "Unknown"

def main():
    parser = argparse.ArgumentParser(description="Sync full Telegram chat history using a user account.")
    parser.add_argument('--api-id', required=True, help='Telegram API ID (from https://my.telegram.org)')
    parser.add_argument('--api-hash', required=True, help='Telegram API Hash (from https://my.telegram.org)')
    parser.add_argument('--phone', required=True, help='Your Telegram phone number (with country code)')
    parser.add_argument('--chat', default=None, help='Chat ID, username, or phone (optional, sync all if omitted)')
    parser.add_argument('--limit', type=int, default=100000, help='Max messages per chat (default: 100000)')
    args = parser.parse_args()

    print("🔐 Initializing Chat History Manager...")
    manager = ChatHistoryManager()

    print(f"📥 Fetching history for chat: {args.chat or 'ALL CHATS'} (limit: {args.limit})")
    
    # Run the async sync function
    messages = asyncio.run(sync_history_async(
        api_id=args.api_id,
        api_hash=args.api_hash,
        phone=args.phone,
        chat_id=args.chat,
        limit=args.limit
    ))

    if messages:
        print(f"💾 Storing {len(messages)} messages in encrypted database...")
        success = manager.store_encrypted_history({
            'messages': messages,
            'chat_id': args.chat or 'all',
            'chat_name': args.chat or 'All Chats',
            'chat_type': 'unknown',
        })
        if success:
            print("✅ History sync and storage complete!")
            print(f"📊 You can now use /readall, /analytics, and /search_history in your bot!")
        else:
            print("❌ Failed to store messages.")
    else:
        print(f"❌ No messages fetched. Check your credentials and try again.")

if __name__ == "__main__":
    main() 