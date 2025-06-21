#!/usr/bin/env python3
"""
Launcher script for Telegram Manager Bot
"""

import os
import sys
import subprocess

def check_setup():
    """Check if the bot is properly set up"""
    print("🔍 Checking setup...")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Run: python setup_env.py")
        return False
    
    # Check if main bot file exists
    if not os.path.exists("telegram_manager_bot_unified.py"):
        print("❌ telegram_manager_bot_unified.py not found")
        return False
    
    print("✅ Setup looks good")
    return True

def run_tests():
    """Run setup tests"""
    print("🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "test_suite.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Tests failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main launcher function"""
    print("🚀 Telegram Manager Bot Launcher")
    print("=" * 40)
    
    # Check setup
    if not check_setup():
        sys.exit(1)
    
    # Ask if user wants to run tests
    response = input("Run setup tests? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        if not run_tests():
            print("❌ Setup issues detected. Please fix them before running the bot.")
            sys.exit(1)
    
    print("\n🤖 Starting Telegram Manager Bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 40)
    
    try:
        # Run the bot
        subprocess.run([sys.executable, "telegram_manager_bot_unified.py"])
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")

if __name__ == "__main__":
    main() 