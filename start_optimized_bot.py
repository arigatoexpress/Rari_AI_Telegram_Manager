#!/usr/bin/env python3
"""
Start Optimized Telegram Bot
===========================
Startup script for the optimized Telegram Manager Bot.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import nest_asyncio

# Load environment variables
load_dotenv()

def main():
    print("🚀 Starting Optimized Telegram Manager Bot...")
    print("=" * 60)
    
    # Check if bot token is available
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Please set your bot token in the .env file")
        sys.exit(1)
    
    try:
        # Import and run the optimized bot
        from telegram_bot_optimized import OptimizedTelegramBot
        
        bot = OptimizedTelegramBot()
        
        # Validate bot token
        if not bot.bot_token:
            print("❌ Error: Bot token is None or empty")
            sys.exit(1)
        
        print("✅ Bot components initialized successfully")
        print("🔄 Starting optimized bot...")
        
        # Apply nest_asyncio for robust event loop handling on macOS
        nest_asyncio.apply()
        
        # Run the bot
        asyncio.get_event_loop().run_until_complete(bot.start_bot())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure telegram_bot_optimized.py exists and is properly formatted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 