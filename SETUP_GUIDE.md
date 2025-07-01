# 🤖 Telegram Manager Bot - Setup Guide

This guide will help you fix and configure your Telegram Manager Bot with all features working correctly.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
# Make sure the script is executable
chmod +x startup.sh

# Start everything with one command
./startup.sh
```

This will:
- ✅ Check and start Ollama server
- ✅ Install required AI models
- ✅ Test all components
- ✅ Start the Telegram bot with all features

### Option 2: Manual Startup
```bash
# 1. Start Ollama server (if not running)
ollama serve &

# 2. Pull required AI model
ollama pull llama3.2:3b

# 3. Test your setup
python3 test_features.py

# 4. Start the bot
python3 start_optimized_bot.py
```

### 3. Test in Telegram
Send `/help` to your bot to see all available commands.

## 🔧 Environment Setup

### Required Environment Variables
Create a `.env` file in your project root with:

```env
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Telegram API Credentials (for reading chats)
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here

# Authorized Users (comma-separated user IDs)
AUTHORIZED_USERS=your_user_id_here

# Optional: Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS_FILE=google_service_account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

### Getting Telegram API Credentials
1. Go to https://my.telegram.org/auth
2. Log in with your phone number
3. Go to 'API Development Tools'
4. Create a new application
5. Copy API ID and API Hash

### Installing Ollama (AI Backend)
The bot uses Ollama for AI-powered analysis and outreach generation.

#### Install Ollama:
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download
```

#### Start Ollama Server:
```bash
# Start the server
ollama serve

# In another terminal, pull the required model
ollama pull llama3.2:3b
```

#### Verify Ollama Installation:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test with a simple query
ollama run llama3.2:3b "Hello, how are you?"
```

## 📋 Available Commands

### Core Features
- `/start` - Welcome message
- `/help` - Show all commands
- `/status` - Check bot status
- `/stats` - View performance statistics

### Chat Management
- `/read_chats` - Sync all Telegram chats
- `/sync` - Check sync status
- `/auto_sync` - Toggle automatic sync

### Contact Management
- `/contacts` - View all contacts
- `/leads` - View high-value leads
- `/crm` - CRM dashboard

### 🎯 NEW: Outreach Features
- `/outreach` - Generate outreach blurbs for all contacts
- `/blurbs` - View existing outreach blurbs
- `/followup` - Get follow-up recommendations

### Analysis & Insights
- `/analyze [chat_id]` - Analyze specific chat
- `/insights` - Generate business insights
- `/dailybrief` - Daily summary

### Note Management
- `/note <text>` - Create a note
- `/notes [category]` - View notes

## 🔄 Workflow

### 1. Initial Setup
```bash
# Test everything works
python test_features.py

# Start the bot
python start_optimized_bot.py
```

### 2. Sync Your Chats
In Telegram, send:
```
/read_chats
```
This will:
- Read all your Telegram chats
- Extract contact information
- Calculate lead scores
- Store everything in the database

### 3. Generate Outreach Blurbs
```
/outreach
```
This will:
- Generate personalized outreach messages for each contact
- Store them for easy access
- Prioritize high-value leads

### 4. View Your Data
```
/contacts    # View all contacts
/leads       # View high-value leads
/blurbs      # View outreach messages
/followup    # Get follow-up recommendations
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "TELEGRAM_BOT_TOKEN not found"
- Make sure you have a `.env` file
- Get your bot token from @BotFather
- Add it to the `.env` file

#### 2. "Telegram API credentials not configured"
- Get API credentials from https://my.telegram.org/auth
- Add them to your `.env` file

#### 3. "No contacts found"
- Run `/read_chats` first to sync your chats
- Make sure you have conversations in Telegram

#### 4. Import errors
```bash
pip install -r requirements.txt
```

#### 5. Database errors
```bash
# Remove old database (if corrupted)
rm -rf data/
# Restart the bot
python start_optimized_bot.py
```

### Testing Individual Components

#### Test Data Manager
```python
from core.data_manager import DataManager
dm = DataManager()
# Test adding a message
success, msg = await dm.add_message(test_message)
```

#### Test AI Analyzer
```python
from core.ai_analyzer import AIAnalyzer
analyzer = AIAnalyzer(dm)
# Test sentiment analysis
sentiment = await analyzer._analyze_sentiment("Test message")
```

#### Test Outreach Features
```python
from telegram_bot_optimized import OptimizedTelegramBot
bot = OptimizedTelegramBot()
# Test blurb generation
blurb = await bot._generate_outreach_blurb(test_contact)
```

## 📊 Features Overview

### ✅ Working Features
- **Chat Synchronization**: Read and sync all Telegram chats
- **Contact Management**: Automatic contact extraction and lead scoring
- **Outreach Automation**: Generate personalized outreach blurbs
- **Follow-up Recommendations**: Get actionable follow-up suggestions
- **AI Analysis**: Sentiment analysis and business insights
- **Note Management**: Create and organize notes
- **Google Sheets Integration**: Sync data to spreadsheets
- **Performance Monitoring**: Track bot statistics

### 🎯 Outreach System
The outreach system automatically:
1. **Analyzes Contacts**: Evaluates lead scores and engagement
2. **Generates Blurbs**: Creates personalized outreach messages
3. **Categorizes Leads**: High-value, medium-value, general contacts
4. **Recommends Actions**: Suggests follow-up activities
5. **Tracks Progress**: Monitors outreach effectiveness

### 📈 Lead Scoring
Contacts are scored based on:
- **Message Count** (40%): More messages = higher engagement
- **Sentiment Score** (30%): Positive sentiment = better relationship
- **Engagement Ratio** (30%): Positive vs negative message ratio

## 🔒 Security

### Authorization
- Set `AUTHORIZED_USERS` in `.env` to restrict access
- Bot will only respond to authorized users
- All data is stored locally by default

### Data Privacy
- Messages are processed locally
- No data is sent to external services (except Google Sheets if configured)
- Database is encrypted and secure

## 🚀 Advanced Configuration

### Custom Lead Scoring
Edit `core/data_manager.py` to customize scoring:
```python
def _calculate_lead_score(self, message_count, avg_sentiment, positive_messages, negative_messages):
    # Customize weights here
    message_score = min(message_count / 100, 0.4)
    sentiment_score = max(0, avg_sentiment) * 0.3
    engagement_score = (positive_messages / total_messages) * 0.3
    return min(message_score + sentiment_score + engagement_score, 1.0)
```

### Custom Outreach Templates
Edit the `_generate_outreach_blurb` method in `telegram_bot_optimized.py` to customize outreach messages.

### Google Sheets Integration
1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a service account
4. Download credentials as `google_service_account.json`
5. Share your spreadsheet with the service account email

## 📞 Support

If you encounter issues:

1. **Run the test script**: `python test_features.py`
2. **Check the logs**: Look at `telegram_bot_optimized.log`
3. **Verify environment**: Make sure all variables are set
4. **Test components**: Use the individual test functions above

## 🎉 Success Checklist

- [ ] Environment variables configured
- [ ] Bot starts without errors
- [ ] `/help` command works
- [ ] `/read_chats` syncs your chats
- [ ] `/contacts` shows your contacts
- [ ] `/outreach` generates blurbs
- [ ] `/blurbs` shows outreach messages
- [ ] `/followup` gives recommendations
- [ ] All commands respond correctly

Once all items are checked, your bot is fully functional! 🚀 