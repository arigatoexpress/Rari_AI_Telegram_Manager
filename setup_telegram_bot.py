#!/usr/bin/env python3
"""
Telegram BD Bot Setup & Testing
===============================
This script helps you set up and test your Telegram BD Bot.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

def check_environment_setup():
    """Check if environment is properly configured"""
    print("🔧 Telegram BD Bot Setup")
    print("="*40)
    
    # Check for .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ No .env file found!")
        print("📋 Creating .env file from template...")
        
        # Copy template
        template_file = Path('env.example')
        if template_file.exists():
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            with open('.env', 'w') as f:
                f.write(template_content)
            
            print("✅ Created .env file from template")
            print("📝 Please edit .env with your actual values:")
            print("   1. TELEGRAM_BOT_TOKEN - Get from @BotFather")
            print("   2. TELEGRAM_USER_ID - Get from @userinfobot") 
            print("   3. OPENAI_API_KEY - Get from OpenAI platform")
            print("   4. GOOGLE_SHEET_ID - Optional for sheets integration")
            return False
        else:
            print("❌ No template file found")
            return False
    
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Get from @BotFather on Telegram',
        'TELEGRAM_USER_ID': 'Get from @userinfobot on Telegram',
        'OPENAI_API_KEY': 'Get from https://platform.openai.com/api-keys'
    }
    
    missing = []
    placeholder_values = ['your_bot_token_here', 'your_user_id_here', 'your_openai_api_key_here']
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value in placeholder_values:
            missing.append(f"   ❌ {var}: {description}")
    
    if missing:
        print("\n📝 Missing or placeholder environment variables:")
        for item in missing:
            print(item)
        print("\n🔧 Please update your .env file with actual values")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        'python-telegram-bot',
        'openai',
        'python-dotenv',
        'asyncio',
        'pandas',
        'sqlite3'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'python-telegram-bot':
                import telegram
            elif package == 'openai':
                import openai
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'asyncio':
                import asyncio
            elif package == 'pandas':
                import pandas
            elif package == 'sqlite3':
                import sqlite3
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("💾 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def test_telegram_connection():
    """Test telegram bot connection"""
    print("\n🤖 Testing Telegram Bot Connection...")
    
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token or token == 'your_bot_token_here':
        print("❌ Invalid bot token")
        return False
    
    try:
        import asyncio
        from telegram import Bot
        
        async def test_bot():
            bot = Bot(token=token)
            bot_info = await bot.get_me()
            return bot_info
        
        # Run the test
        bot_info = asyncio.run(test_bot())
        print(f"✅ Bot connected: @{bot_info.username}")
        print(f"   Bot Name: {bot_info.first_name}")
        print(f"   Bot ID: {bot_info.id}")
        return True
        
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        print("🔧 Check your TELEGRAM_BOT_TOKEN in .env")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🧠 Testing OpenAI API Connection...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ Invalid OpenAI API key")
        return False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test connection"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API connected successfully")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        print("🔧 Check your OPENAI_API_KEY in .env")
        return False

def setup_database():
    """Set up database directories and check core modules"""
    print("\n🗄️ Setting up Database...")
    
    # Create directories
    dirs = ['data', 'logs', 'cache', 'backups', 'exports']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   ✅ {dir_name}/ directory ready")
    
    # Check core modules
    try:
        from core.lead_tracking_db import LeadTrackingDB
        from core.bd_intelligence import BDIntelligence
        from core.ai_deal_analyzer import AIDealAnalyzer
        print("✅ Core BD modules loaded successfully")
        return True
    except ImportError as e:
        print(f"❌ Core module import failed: {e}")
        return False

def run_quick_bot_test():
    """Run a quick test of the bot functionality"""
    print("\n🚀 Running Quick Bot Test...")
    
    try:
        from ultimate_bd_bot import UltimateBDBot
        
        async def test_bot_init():
            bot = UltimateBDBot()
            success = await bot.initialize()
            if success:
                print("✅ Bot initialization successful")
                await bot.stop()
                return True
            else:
                print("❌ Bot initialization failed")
                return False
        
        result = asyncio.run(test_bot_init())
        return result
        
    except Exception as e:
        print(f"❌ Bot test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 Telegram BD Bot Setup & Testing")
    print("="*50)
    
    success_count = 0
    total_tests = 6
    
    # 1. Environment setup
    if check_environment_setup():
        success_count += 1
    
    # 2. Dependencies check
    if check_dependencies():
        success_count += 1
    
    # 3. Database setup
    if setup_database():
        success_count += 1
    
    # 4. Telegram connection test
    if test_telegram_connection():
        success_count += 1
    
    # 5. OpenAI connection test  
    if test_openai_connection():
        success_count += 1
    
    # 6. Bot initialization test
    if run_quick_bot_test():
        success_count += 1
    
    print(f"\n📊 Setup Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("\n🎉 Setup Complete!")
        print("🚀 Your Telegram BD Bot is ready to start!")
        print("\n📋 Start your bot:")
        print("   python start_ultimate_bd_bot.py")
        print("\n📱 Test in Telegram:")
        print("   /start - Welcome message")
        print("   /help - Command reference")
        print("   /leads - Lead dashboard")
        print("   /analyze - AI conversation analysis")
        
    else:
        print(f"\n🔧 Setup incomplete ({total_tests - success_count} issues)")
        print("📝 Please fix the issues above and run setup again")
        
        if success_count == 0:
            print("\n🚨 Getting Started:")
            print("   1. Edit .env with your actual API keys")
            print("   2. Install dependencies: pip install -r requirements.txt")
            print("   3. Run setup again: python setup_telegram_bot.py")

if __name__ == "__main__":
    main() 