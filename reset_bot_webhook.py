#!/usr/bin/env python3
"""
Reset Bot Webhook
================
Resets the bot's webhook to clear any conflicting states.
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def reset_bot_webhook():
    """Reset the bot's webhook"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    print("🔄 Resetting bot webhook...")
    
    # Delete webhook
    delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(delete_url) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Webhook deleted: {result.get('description', 'Success')}")
                else:
                    print(f"❌ Failed to delete webhook: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False
    
    # Get bot info to verify connection
    get_me_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(get_me_url) as response:
                if response.status == 200:
                    result = await response.json()
                    bot_info = result.get('result', {})
                    print(f"✅ Bot connected: @{bot_info.get('username', 'Unknown')}")
                    print(f"   Name: {bot_info.get('first_name', 'Unknown')}")
                    print(f"   ID: {bot_info.get('id', 'Unknown')}")
                else:
                    print(f"❌ Failed to get bot info: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return False
    
    return True

async def main():
    """Main function"""
    print("🚀 Bot Webhook Reset Tool")
    print("=" * 40)
    
    success = await reset_bot_webhook()
    
    if success:
        print("\n✅ Webhook reset successful!")
        print("🔄 You can now start the bot with: python start_optimized_bot.py")
    else:
        print("\n❌ Webhook reset failed")
        print("Please check your bot token and try again")

if __name__ == "__main__":
    asyncio.run(main()) 