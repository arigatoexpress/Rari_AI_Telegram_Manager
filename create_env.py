#!/usr/bin/env python3
"""
Simple script to create .env file with your credentials
"""

import os
from cryptography.fernet import Fernet

def create_env_file():
    """Create the .env file with your credentials"""
    
    # Generate a new Fernet key
    fernet_key = Fernet.generate_key().decode()
    
    # Your credentials
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8131634251:AAHAlssgeFocTHTHLLW-v-WT6t-nX64v6fI
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_telegram_api_hash_here
USER_ID=your_telegram_user_id_here

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
GOOGLE_SPREADSHEET_ID=your_google_spreadsheet_id_here

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
    print(f"🔑 New Fernet key generated: {fernet_key[:20]}...")
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file and update:")
    print("   - TELEGRAM_API_ID (your Telegram API ID)")
    print("   - TELEGRAM_API_HASH (your Telegram API Hash)")
    print("   - USER_ID (your Telegram User ID)")
    print("   - GOOGLE_SPREADSHEET_ID (your Google Sheet ID)")
    print("2. Download your Google service account JSON file")
    print("3. Save it as 'google_service_account.json' in this directory")
    print("4. Share your Google Sheet with the service account email")
    print("5. Test the bot with: python telegram_manager_bot_unified.py")

if __name__ == "__main__":
    create_env_file() 