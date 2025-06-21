# Telegram Manager Bot - Usage Guide

## 🚀 Quick Start

1. **Start the bot:**
   ```bash
   python telegram_manager_bot_unified.py
   ```

2. **Access your Google Sheet:**
   ```bash
   python access_google_sheet.py
   ```

3. **Sync chat history (optional):**
   ```bash
   python simple_sync.py
   ```

## 📱 Bot Commands

### Basic Commands
- `/start` - Show main menu
- `/help` - Show help message
- `/status` - Check bot status

### Notes & Organization
- `/note <text>` - Save a note to Google Sheets
- `/summary` - View recent notes
- `/followup` - View pending follow-ups

### AI Features
- `/generate <prompt>` - Generate text with AI
- `/brief` - Generate daily briefing from your data

### Data Management
- `/readall` - View recent chat messages (requires sync)
- `/leads` - View leads from Google Sheets
- `/contacts` - View contact profiles
- `/analytics` - View usage analytics

### Utilities
- `/meeting [topic]` - Generate meeting link
- `/ai_status` - Check AI backend status

## 📊 Google Sheets Access

Your data is stored in Google Sheets with these sheets:
- **Notes**: Your saved notes and reminders
- **Contacts**: Contact profiles and information  
- **Messages**: Chat message history
- **Business_Briefs**: Meeting summaries
- **Leads**: Lead tracking
- **Analytics**: Usage statistics
- **Settings**: Bot configuration

## 🔧 Troubleshooting

### Bot not responding?
1. Check if bot is running: `ps aux | grep telegram_manager_bot_unified`
2. Restart the bot: `python telegram_manager_bot_unified.py`

### Can't access Google Sheet?
1. Run: `python access_google_sheet.py`
2. Follow the sharing instructions

### No chat history in /readall?
1. Run: `python simple_sync.py`
2. Enter the Telegram code when prompted

### Decryption errors?
1. Run: `python fix_bot_issues.py`
2. This will generate a new encryption key

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Ensure all environment variables are set in .env
3. Verify Google Sheets permissions
4. Restart the bot and try again 