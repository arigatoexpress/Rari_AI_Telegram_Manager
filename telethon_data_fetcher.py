#!/usr/bin/env python3
"""
Telethon Data Fetcher for Telegram Manager Bot
==============================================
Fetches real-time data from Telegram using Telethon for use in bot functions.
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel

class TelethonDataFetcher:
    """Fetches real-time data from Telegram using Telethon"""
    
    def __init__(self):
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.user_id = os.getenv('USER_ID')
        self.client = None
        
    async def connect(self):
        """Connect to Telegram"""
        if not all([self.api_id, self.api_hash, self.user_id]):
            raise ValueError("Missing Telegram credentials in .env")
        
        session_name = f"bot_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.client = TelegramClient(session_name, int(str(self.api_id)), str(self.api_hash))
        await self.client.start(phone=lambda: str(self.user_id))
        
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.client:
            await self.client.disconnect()
    
    async def fetch_recent_messages(self, limit=50):
        """Fetch recent messages from all chats"""
        if not self.client:
            await self.connect()
        
        messages = []
        try:
            async for dialog in self.client.iter_dialogs(limit=5):  # Get recent 5 chats
                try:
                    async for message in self.client.iter_messages(dialog, limit=limit//5):
                        if message and message.text:
                            sender_name = "Unknown"
                            if message.sender:
                                if hasattr(message.sender, 'first_name'):
                                    sender_name = f"{message.sender.first_name}"
                                    if hasattr(message.sender, 'last_name') and message.sender.last_name:
                                        sender_name += f" {message.sender.last_name}"
                                elif hasattr(message.sender, 'title'):
                                    sender_name = message.sender.title
                            
                            messages.append({
                                'id': message.id,
                                'chat_id': str(dialog.id),
                                'chat_title': dialog.title or "Unknown Chat",
                                'sender_id': str(message.sender_id) if message.sender_id else "Unknown",
                                'sender_name': sender_name,
                                'text': message.text,
                                'date': message.date.isoformat(),
                                'is_outgoing': message.out
                            })
                except Exception as e:
                    print(f"Error fetching messages from {dialog.title}: {e}")
                    continue
        except Exception as e:
            print(f"Error in fetch_recent_messages: {e}")
        
        return messages
    
    async def fetch_today_messages(self):
        """Fetch messages from today only"""
        if not self.client:
            await self.connect()
        
        today = datetime.now().date()
        messages = []
        
        try:
            async for dialog in self.client.iter_dialogs(limit=10):
                try:
                    async for message in self.client.iter_messages(dialog, limit=100):
                        if message and message.text and message.date.date() == today:
                            sender_name = "Unknown"
                            if message.sender:
                                if hasattr(message.sender, 'first_name'):
                                    sender_name = f"{message.sender.first_name}"
                                    if hasattr(message.sender, 'last_name') and message.sender.last_name:
                                        sender_name += f" {message.sender.last_name}"
                                elif hasattr(message.sender, 'title'):
                                    sender_name = message.sender.title
                            
                            messages.append({
                                'id': message.id,
                                'chat_id': str(dialog.id),
                                'chat_title': dialog.title or "Unknown Chat",
                                'sender_id': str(message.sender_id) if message.sender_id else "Unknown",
                                'sender_name': sender_name,
                                'text': message.text,
                                'date': message.date.isoformat(),
                                'is_outgoing': message.out
                            })
                except Exception as e:
                    print(f"Error fetching today's messages from {dialog.title}: {e}")
                    continue
        except Exception as e:
            print(f"Error in fetch_today_messages: {e}")
        
        return messages
    
    async def generate_brief_from_messages(self, messages):
        """Generate a brief summary from messages"""
        if not messages:
            return "No recent messages found to generate briefing from."
        
        # Group messages by chat
        chat_messages = {}
        for msg in messages:
            chat_title = msg.get('chat_title', 'Unknown')
            if chat_title not in chat_messages:
                chat_messages[chat_title] = []
            chat_messages[chat_title].append(msg)
        
        # Create summary
        summary = f"📅 **Daily Message Summary** ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        summary += f"📊 **Total Messages:** {len(messages)}\n"
        summary += f"💬 **Active Chats:** {len(chat_messages)}\n\n"
        
        for chat_title, msgs in chat_messages.items():
            summary += f"**{chat_title}** ({len(msgs)} messages)\n"
            # Show a few key messages from each chat
            for msg in msgs[:3]:
                time = msg['date'][11:16]  # Just time
                sender = msg['sender_name']
                text = msg['text'][:100] + "..." if len(msg['text']) > 100 else msg['text']
                summary += f"• {time} - {sender}: {text}\n"
            summary += "\n"
        
        return summary

async def main():
    """Test the Telethon data fetcher"""
    print("🔍 Testing Telethon Data Fetcher...")
    
    fetcher = TelethonDataFetcher()
    
    try:
        await fetcher.connect()
        print("✅ Connected to Telegram")
        
        # Fetch recent messages
        messages = await fetcher.fetch_recent_messages(limit=20)
        print(f"✅ Fetched {len(messages)} recent messages")
        
        # Generate brief
        brief = await fetcher.generate_brief_from_messages(messages)
        print("\n📅 Generated Brief:")
        print(brief)
        
        # Fetch today's messages
        today_messages = await fetcher.fetch_today_messages()
        print(f"\n✅ Fetched {len(today_messages)} messages from today")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await fetcher.disconnect()
        print("✅ Disconnected from Telegram")

if __name__ == "__main__":
    asyncio.run(main()) 