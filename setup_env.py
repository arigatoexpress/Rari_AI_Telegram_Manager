#!/usr/bin/env python3
"""
Environment Setup Script for Telegram Manager Bot
=================================================
Helps you set up your .env file with proper credentials and encryption keys.
"""

import os
import base64
from cryptography.fernet import Fernet
from pathlib import Path

def generate_fernet_key():
    """Generate a valid Fernet key"""
    return Fernet.generate_key().decode()

def create_env_file():
    """Create the .env file with user input"""
    print("🔧 Setting up your .env file...")
    print("=" * 50)
    
    # Get user input for required fields
    telegram_api_id = input("Enter your Telegram API ID: ").strip()
    telegram_api_hash = input("Enter your Telegram API Hash: ").strip()
    user_id = input("Enter your Telegram User ID: ").strip()
    google_spreadsheet_id = input("Enter your Google Spreadsheet ID (or press Enter to create new): ").strip()
    
    # Generate Fernet key
    fernet_key = generate_fernet_key()
    print(f"✅ Generated new Fernet key: {fernet_key[:20]}...")
    
    # Create .env content
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8131634251:AAHAlssgeFocTHTHLLW-v-WT6t-nX64v6fI
TELEGRAM_API_ID={telegram_api_id}
TELEGRAM_API_HASH={telegram_api_hash}
USER_ID={user_id}

# AI Backend Configuration
AI_BACKEND=ollama
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Atoma DePIN Configuration (if using)
ATOMA_API_KEY=your_atoma_api_key_here
ATOMA_BASE_URL=https://api.atoma.ai

# Google Sheets Integration
GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json
GOOGLE_SPREADSHEET_ID={google_spreadsheet_id}

# Encryption Key (for chat history)
FERNET_KEY={fernet_key}

# Meeting Configuration
MEETING_URL_BASE=https://meet.jit.si

# Context and Data Files
CONTEXT_FILE=context.md
DATA_FILE=data_store.json

# Sui Blockchain Configuration (if using)
SUI_NODE_URL=https://fullnode.mainnet.sui.io:443
SUI_PACKAGE=your_sui_package_id
SUI_MODULE=your_sui_module_name

# Logging Configuration
LOG_LEVEL=INFO
AGENT_LOG_LEVEL=INFO

# Development Configuration
DEBUG=false
TESTING=false

# Database Configuration
DATABASE_TYPE=google_sheets
BACKUP_ENABLED=true
BACKUP_INTERVAL=24

# Security Configuration
ENCRYPTION_ENABLED=true
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60

# Notification Configuration
NOTIFICATIONS_ENABLED=true
EMAIL_NOTIFICATIONS=false
TELEGRAM_NOTIFICATIONS=true

# Analytics Configuration
ANALYTICS_ENABLED=true
ANALYTICS_RETENTION_DAYS=90

# Deployment Configuration
DEPLOYMENT_ENVIRONMENT=development
NOSANA_API_KEY=your_nosana_api_key_here
NOSANA_PROJECT_ID=your_nosana_project_id_here
"""
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print(f"📁 Location: {os.path.abspath('.env')}")
    
    # Instructions for next steps
    print("\n📋 Next Steps:")
    print("1. Download your Google service account JSON file")
    print("2. Save it as 'google_service_account.json' in this directory")
    print("3. Share your Google Sheet with: tgmanager@tgmanager-463607.iam.gserviceaccount.com")
    print("4. Test the bot with: python telegram_manager_bot_unified.py")
    
    return True

def check_requirements():
    """Check if required files exist"""
    print("🔍 Checking requirements...")
    
    missing_files = []
    
    # Check for Google service account file
    if not os.path.exists('google_service_account.json'):
        missing_files.append('google_service_account.json')
    
    # Check for .env file
    if not os.path.exists('.env'):
        missing_files.append('.env')
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files found!")
        return True

def main():
    """Main setup function"""
    print("🚀 Telegram Manager Bot Environment Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Create .env file
    if create_env_file():
        print("\n🎉 Setup complete!")
        
        # Check requirements
        if check_requirements():
            print("\n✅ Ready to run the bot!")
        else:
            print("\n⚠️  Please complete the missing requirements before running the bot.")
    else:
        print("❌ Setup failed.")

if __name__ == "__main__":
    main() 