#!/usr/bin/env python3
"""
Start Ultimate BD Bot
=====================
Simplified startup with comprehensive error handling
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ultimate_bd_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check environment configuration"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY',
        'GOOGLE_SHEET_ID'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing environment variables: {missing}")
        return False
    
    return True

def setup_directories():
    """Setup required directories"""
    dirs = ['logs', 'data', 'backups']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

async def main():
    """Main startup function"""
    try:
        logger.info("🚀 Starting Ultimate BD Bot...")
        
        # Setup
        setup_directories()
        
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        # Import and start bot
        from ultimate_bd_bot import UltimateBDBot
        
        bot = UltimateBDBot()
        logger.info("✅ Bot initialized successfully")
        
        # Initialize bot
        success = await bot.initialize()
        if not success:
            logger.error("❌ Bot initialization failed")
            sys.exit(1)
        
        logger.info("🎯 Starting bot...")
        await bot.start()
        
        # Keep running
        while bot.is_running:
            await asyncio.sleep(1)
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure all required modules are available")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        sys.exit(1)
    finally:
        if 'bot' in locals():
            await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1) 