# 🚀 Setup Guide - Google Sheets & Chat History Encryption

## ✅ Current Status

Your setup is **partially complete**! Here's what's working and what needs to be done:

### ✅ **What's Working:**
- ✅ Google Cloud API key added to `.env`
- ✅ Service account JSON file created
- ✅ Encryption key generated and configured
- ✅ Chat history manager tested and working
- ✅ Bot is running with Ollama

### 🔧 **What Needs Setup:**

## 1. **Google Sheets Setup**

### Step 1: Create a Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Copy the **Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```

### Step 2: Share with Service Account
1. Click **Share** in your Google Sheet
2. Add this email as **Editor**:
   ```
   tg-manager-bot@tgmanager-463607.iam.gserviceaccount.com
   ```

### Step 3: Update .env File
Edit your `.env` file and replace:
```
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```
with your actual sheet ID.

### Step 4: Test Google Sheets
```bash
python test_google_sheets.py
```

## 2. **Chat History Encryption Setup**

### Step 1: Install Telethon (for full chat history)
```bash
pip install telethon
```

### Step 2: Your Telegram API Credentials
You already have these in your `.env`:
- ✅ `TELEGRAM_API_ID=20785477`
- ✅ `TELEGRAM_API_HASH=331de234a1c2b2937a054912379b91e1`
- ✅ `TELEGRAM_PHONE=+12814154111`

### Step 3: Test Chat History Manager
```bash
python chat_history_manager.py
```

## 3. **Bot Commands for Testing**

Once everything is set up, you can test these commands in Telegram:

### Google Sheets Commands:
- `/brief` - Generate business brief from notes
- `/export` - Export data to Google Sheets
- `/lead` - Track leads in your sheet

### Chat History Commands:
- `/history` - Get chat history insights
- `/search <query>` - Search encrypted chat history
- `/export_history` - Export encrypted chat history

## 4. **Security Features**

### 🔐 **Encryption:**
- All chat history is encrypted with AES-256
- Encryption key stored in `.env` file
- Data encrypted at rest and in transit
- Database stored in `data/chat_history.db`

### 🔒 **Access Control:**
- Service account has limited permissions
- API keys stored securely in `.env`
- Chat history requires authentication

## 5. **Quick Test Commands**

### Test Google Sheets:
```bash
# Test connection
python test_google_sheets.py

# Test with your bot
# Send /brief in Telegram
```

### Test Chat History:
```bash
# Test encryption
python chat_history_manager.py

# Fetch your chat history (will prompt for authentication)
python -c "
from chat_history_manager import ChatHistoryManager
manager = ChatHistoryManager()
# This will prompt for Telegram authentication
"
```

## 6. **Troubleshooting**

### Google Sheets Issues:
- **"Permission denied"**: Make sure you shared the sheet with the service account email
- **"File not found"**: Check the spreadsheet ID in your `.env`
- **"API not enabled"**: Enable Google Sheets API in Google Cloud Console

### Chat History Issues:
- **"Telethon not installed"**: Run `pip install telethon`
- **"Authentication failed"**: Check your API ID and hash in `.env`
- **"Encryption error"**: Regenerate encryption key in `.env`

## 7. **Next Steps**

1. **Create your Google Sheet** and get the ID
2. **Share it with the service account**
3. **Update your `.env` with the sheet ID**
4. **Test both integrations**
5. **Start using the bot commands!**

## 🎯 **Ready to Test?**

Your bot is already running! Try these commands in Telegram:

1. **Test basic functionality**: `/start`
2. **Test AI responses**: `/generate Hello, how are you?`
3. **Test Google Sheets** (after setup): `/brief`
4. **Test chat history** (after setup): `/history`

---

**Need help?** Check the logs in your terminal where the bot is running, or run the test scripts to diagnose issues. 