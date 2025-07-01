#!/usr/bin/env python3
"""
Test Bot
========
Simple test to verify bot functionality.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_bot():
    """Test the bot functionality"""
    print("🧪 Testing bot functionality...")
    
    try:
        # Import the bot
        from telegram_bot_optimized import OptimizedTelegramBot
        
        print("✅ Bot import successful")
        
        # Create bot instance
        bot = OptimizedTelegramBot()
        print("✅ Bot instance created")
        
        # Check bot token
        if bot.bot_token:
            print(f"✅ Bot token found: {bot.bot_token[:20]}...")
        else:
            print("❌ Bot token not found")
            return False
        
        # Check if application was created
        if bot.application:
            print("✅ Application created")
        else:
            print("❌ Application not created")
            return False
        
        # Test bot info
        try:
            bot_info = await bot.application.bot.get_me()
            print(f"✅ Bot info: @{bot_info.username} ({bot_info.first_name})")
        except Exception as e:
            print(f"❌ Error getting bot info: {e}")
            return False
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("🚀 Bot Test Tool")
    print("=" * 40)
    
    success = await test_bot()
    
    if success:
        print("\n✅ Bot is ready to run!")
        print("🔄 Start with: python start_optimized_bot.py")
    else:
        print("\n❌ Bot test failed")
        print("Please check the errors above")

if __name__ == "__main__":
    asyncio.run(main()) 