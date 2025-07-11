#!/usr/bin/env python3
"""
Quick webhook reset script
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def reset_webhook():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ No TELEGRAM_BOT_TOKEN found")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted and pending updates dropped")
        
        # Get bot info to verify connection
        me = await bot.get_me()
        print(f"✅ Bot @{me.username} is ready for polling")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(reset_webhook()) 