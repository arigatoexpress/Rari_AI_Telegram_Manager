#!/usr/bin/env python3
"""
Telegram BD Intelligence System Setup
====================================
Interactive setup script to configure your BD intelligence system.
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

def print_header():
    """Print setup header"""
    print("🚀 Telegram BD Intelligence System Setup")
    print("=" * 60)
    print("📱 Extract all Telegram chat history")
    print("🗄️ Store in secure local database")
    print("📊 Export to Google Sheets with BD formatting")
    print("🧠 AI analysis for actionable insights")
    print("🎯 BD automation for deal closing")
    print("=" * 60)

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        ('telethon', 'Telegram API'),
        ('pandas', 'Data processing'),
        ('gspread', 'Google Sheets'),
        ('openai', 'AI analysis'),
        ('dotenv', 'Environment config'),
        ('rich', 'Beautiful console output')
    ]
    
    missing = []
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} ({description})")
        except ImportError:
            print(f"  ❌ {package} ({description}) - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n🔧 Install missing packages:")
        print(f"   pip install -r requirements_bd.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        'data',
        'logs',
        'backups',
        'exports',
        'sheets_exports',
        'cache'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ All directories created!")

def setup_environment():
    """Set up environment configuration"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_file = Path('.env')
    template_file = Path('config.env.template')
    
    if env_file.exists():
        print("  ℹ️ .env file already exists")
        response = input("  ❓ Overwrite existing .env file? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("  ⏭️ Keeping existing .env file")
            return True
    
    if template_file.exists():
        shutil.copy(template_file, env_file)
        print("  ✅ Created .env from template")
        print("  📝 Please edit .env with your actual values:")
        print("     1. TELEGRAM_API_ID & TELEGRAM_API_HASH from https://my.telegram.org/apps")
        print("     2. TELEGRAM_PHONE (your phone number)")
        print("     3. OPENAI_API_KEY from https://platform.openai.com/api-keys")
        print("     4. GOOGLE_SHEET_ID (optional - will be created if empty)")
        return False  # Need user to configure
    else:
        print("  ❌ Template file not found")
        return False

def check_telegram_api():
    """Check Telegram API configuration"""
    print("\n📱 Checking Telegram API configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    if not all([api_id, api_hash, phone]):
        print("  ❌ Missing Telegram API configuration")
        print("  🔧 Please set in .env file:")
        if not api_id:
            print("     - TELEGRAM_API_ID")
        if not api_hash:
            print("     - TELEGRAM_API_HASH")
        if not phone:
            print("     - TELEGRAM_PHONE")
        return False
    
    print("  ✅ Telegram API configuration found")
    return True

def check_openai_api():
    """Check OpenAI API configuration"""
    print("\n🧠 Checking OpenAI API configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key or openai_key == 'sk-proj-your-openai-key-here':
        print("  ❌ Missing or placeholder OpenAI API key")
        print("  🔧 Please set OPENAI_API_KEY in .env file")
        print("  🌐 Get your key from: https://platform.openai.com/api-keys")
        return False
    
    print("  ✅ OpenAI API key configured")
    return True

def test_telegram_connection():
    """Test Telegram API connection"""
    print("\n🔌 Testing Telegram connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_id = int(os.getenv('TELEGRAM_API_ID'))
        api_hash = os.getenv('TELEGRAM_API_HASH')
        phone = os.getenv('TELEGRAM_PHONE')
        
        # Import here to avoid dependency issues during setup
        from telethon import TelegramClient
        
        # Test connection (without starting session)
        client = TelegramClient('test_session', api_id, api_hash)
        print("  ✅ Telegram client created successfully")
        print("  ℹ️ Connection test will happen during first run")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Telegram connection test failed: {e}")
        return False

def create_google_sheets_setup():
    """Create Google Sheets setup instructions"""
    print("\n📊 Google Sheets Setup Instructions")
    print("=" * 40)
    
    service_account = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'your_service_account@your_project.iam.gserviceaccount.com')
    
    print(f"📧 Your service account: {service_account}")
    print("\n📋 To set up Google Sheets integration:")
    print("1. Create a new Google Sheet or use existing one")
    print("2. Share the sheet with your service account email:")
    print(f"   {service_account}")
    print("3. Give 'Editor' permissions")
    print("4. Copy the Google Sheet ID from the URL")
    print("5. Add it to your .env file as GOOGLE_SHEET_ID")
    print("\n💡 Sheet ID is the long string in the URL between '/d/' and '/edit'")
    print("   Example: https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit")

def display_next_steps():
    """Display next steps after setup"""
    print("\n🎯 Next Steps")
    print("=" * 30)
    print("1. ✅ Configure your .env file with actual API keys")
    print("2. 📊 Set up Google Sheets integration (see instructions above)")
    print("3. 🚀 Run the BD Intelligence System:")
    print("   python telegram_bd_intelligence.py")
    print("\n📱 First run will:")
    print("   - Connect to Telegram (may require phone verification)")
    print("   - Extract your chat history")
    print("   - Organize by contact/lead")
    print("   - Generate AI insights")
    print("   - Export to Google Sheets")

def main():
    """Main setup function"""
    print_header()
    
    setup_success = True
    
    # Check dependencies
    if not check_dependencies():
        setup_success = False
    
    # Setup directories
    setup_directories()
    
    # Setup environment
    env_configured = setup_environment()
    if not env_configured:
        setup_success = False
    
    # Only check APIs if environment is configured
    if env_configured:
        if not check_telegram_api():
            setup_success = False
        
        if not check_openai_api():
            setup_success = False
        
        # Test Telegram connection
        test_telegram_connection()
    
    # Google Sheets setup instructions
    create_google_sheets_setup()
    
    # Results
    print(f"\n📊 Setup Results")
    print("=" * 30)
    
    if setup_success:
        print("🎉 Setup Complete!")
        print("✅ System is ready for first run")
        display_next_steps()
    else:
        print("🔧 Setup Incomplete")
        print("❌ Please fix the issues above and run setup again")
        print("\n🚨 Common Issues:")
        print("   1. Install dependencies: pip install -r requirements_bd.txt")
        print("   2. Configure .env file with your actual API keys")
        print("   3. Get Telegram API credentials from https://my.telegram.org/apps")
        print("   4. Get OpenAI API key from https://platform.openai.com/api-keys")

if __name__ == "__main__":
    main() 