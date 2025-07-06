#!/usr/bin/env python3
"""
Startup script for Unified Telegram Bot
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_API_ID', 
        'TELEGRAM_API_HASH',
        'TELEGRAM_PHONE',
        'USER_ID',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("💡 Please check your .env file")
        return False
    
    print("✅ All environment variables found")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import telegram
        import telethon
        import openai
        import nest_asyncio
        import apscheduler
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Unified Telegram Bot")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("✅ Pre-flight checks passed")
    print("🚀 Starting bot...")
    
    # Import and run bot
    try:
        from telegram_bd_bot import main as bot_main
        asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 