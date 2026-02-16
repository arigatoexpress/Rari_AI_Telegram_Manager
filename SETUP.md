# 🚀 Telegram BD Intelligence System - Setup Guide

Complete setup guide for the Telegram Business Development Intelligence System.

---

## 📋 Prerequisites

### **System Requirements**
- **Python 3.8+** (Required)
- **Internet Connection** (For AI analysis and API calls)
- **Telegram Account** (For Telegram integration)
- **OpenAI Account** (For AI analysis)

### **Optional Services**
- **Google Cloud Account** (For Google Sheets integration)
- **Telegram Bot** (For bot interface features)

---

## 🎯 Step-by-Step Setup

### **Step 1: Installation**

```bash
# Clone the repository
git clone https://github.com/arigatoexpress/Rari_AI_Telegram_Manager.git
cd Rari_AI_Telegram_Manager

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python main.py health
```

### **Step 2: Environment Configuration**

```bash
# Copy the environment template
cp env.template .env

# Edit the environment file
nano .env  # or use your preferred editor
```

**Configure the following in your `.env` file:**

#### **🔑 Required: OpenAI API Key**
```env
OPENAI_API_KEY=sk-proj-your-openai-key-here
```

**How to get:**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account (if needed)
3. Generate a new API key
4. Copy and paste into `.env`

#### **📱 Required: Telegram API Credentials**
```env
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
```

**How to get:**
1. Visit [my.telegram.org/apps](https://my.telegram.org/apps)
2. Log in with your Telegram account
3. Create a new application
4. Copy API ID and API Hash
5. Add your phone number (format: +1234567890)

#### **🤖 Optional: Telegram Bot**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_user_id_here
```

**How to get:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Message [@userinfobot](https://t.me/userinfobot) to get your User ID

#### **📊 Optional: Google Sheets Integration**
```env
GOOGLE_SERVICE_ACCOUNT_EMAIL=your_service_account@project.iam.gserviceaccount.com
GOOGLE_SHEET_ID=your_sheet_id_here
```

**How to get:**
1. Create a [Google Cloud Project](https://console.cloud.google.com/)
2. Enable Google Sheets API
3. Create a Service Account
4. Download credentials JSON file
5. Share your Google Sheet with the service account email

### **Step 3: Initial Setup and Verification**

```bash
# Run the setup wizard
python main.py setup

# Verify configuration
python main.py config

# Check system health
python main.py health
```

### **Step 4: First Run**

```bash
# Start the application
python main.py

# Or run specific commands
python main.py dashboard    # View analytics
python main.py analyze      # Run AI analysis
python main.py import       # Import Telegram data
```

---

## 🔧 Detailed Configuration

### **Database Configuration**
```env
# Database settings (optional customization)
DATABASE_PATH=data/bd_database.db
LOG_LEVEL=INFO
LOG_FILE=logs/main.log
```

### **Processing Configuration**
```env
# Data processing limits (optional)
MAX_MESSAGES_PER_CHAT=1000
EXTRACTION_DAYS_BACK=180
BATCH_SIZE=100
```

### **AI Configuration**
```env
# AI model settings (optional)
AI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1500
```

---

## 🚀 Usage Examples

### **Basic Analytics Workflow**

```bash
# 1. Import your Telegram data
python main.py import

# 2. Run AI analysis
python main.py analyze

# 3. View dashboard
python main.py dashboard

# 4. Export to Google Sheets
python main.py export
```

### **Interactive Mode**

```bash
# Start interactive mode
python main.py

# Available commands in interactive mode:
# - help          Show all commands
# - dashboard     Analytics dashboard
# - analyze       AI analysis
# - export        Google Sheets export
# - status        System status
# - exit          Quit application
```

### **Bot Interface**

```bash
# Start Telegram bot (requires bot configuration)
python main.py bot
```

---

## 🔒 Security Best Practices

### **Environment File Security**
- **Never commit `.env` files** to version control
- **Use strong, unique API keys** for all services
- **Regularly rotate API keys** for security
- **Keep environment template** (`env.template`) updated

### **Data Protection**
- **All data is stored locally** in SQLite databases
- **No sensitive data is sent to third parties** (except OpenAI for analysis)
- **Regular backups recommended** using `python main.py backup`
- **Database files are excluded from git** automatically

### **API Key Security**
```bash
# Check that your .env file is not tracked by git
git status

# Your .env file should NOT appear in the output
# If it does, run:
git rm --cached .env
```

---

## 🛠️ Troubleshooting

### **Common Installation Issues**

#### **Python Module Import Errors**
```bash
# Solution: Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### **Permission Errors**
```bash
# Solution: Check directory permissions
chmod 755 .
mkdir -p data logs cache
chmod 755 data logs cache
```

#### **API Connection Issues**
```bash
# Test API connections
python main.py config
python main.py health
```

### **Configuration Issues**

#### **Invalid API Keys**
- Double-check API key format in `.env`
- Ensure no extra spaces or quotes
- Verify keys are active and have sufficient credits

#### **Telegram Authentication**
- Ensure phone number format: `+1234567890`
- Complete phone verification when prompted
- Check that Telegram API app is active

#### **Google Sheets Issues**
- Verify service account has access to the sheet
- Check that the Google Sheets API is enabled
- Ensure the sheet ID is correct

### **Performance Issues**

#### **Slow Processing**
```bash
# Check system resources
python main.py status

# Optimize database
python main.py db-optimize

# Clear cache if needed
rm -rf cache/*
```

#### **Memory Issues**
```env
# Reduce batch sizes in .env
BATCH_SIZE=50
MAX_MESSAGES_PER_CHAT=500
```

---

## 📊 Verification & Testing

### **Basic Functionality Test**

```bash
# 1. Health check
python main.py health

# 2. Configuration check
python main.py config

# 3. Database status
python main.py status

# 4. Quick analysis test
python main.py analyze --limit 10
```

### **Full System Test**

```bash
# Complete workflow test
python main.py import
python main.py analyze
python main.py dashboard
python main.py export
python main.py backup
```

---

## 🔄 Maintenance

### **Regular Maintenance Tasks**

```bash
# Weekly: Create backup
python main.py backup

# Monthly: Database optimization
python main.py db-optimize

# As needed: Update system
git pull
pip install -r requirements.txt --upgrade
```

### **Data Management**

```bash
# View data statistics
python main.py status

# Export data for external use
python main.py export

# Clean old logs (if needed)
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 🆘 Getting Help

### **Self-Diagnosis**
```bash
# Run comprehensive health check
python main.py health

# Check configuration
python main.py config

# View system status
python main.py status
```

### **Log Analysis**
```bash
# View recent logs
tail -f logs/main.log

# Search for errors
grep "ERROR" logs/main.log
```

### **Reset and Recovery**
```bash
# Reset configuration (keeps data)
cp env.template .env
python main.py setup

# Fresh start (warning: deletes all data)
rm -rf data/ cache/ logs/
python main.py setup
```

---

## 📈 Advanced Features

### **Custom Integrations**
- Extend `core/` modules for custom functionality
- Add new export formats in data management layer
- Create custom AI prompts for specific industries

### **Performance Optimization**
- Configure caching settings for your usage patterns
- Adjust batch sizes based on system resources
- Implement custom database indexing for large datasets

### **Enterprise Features**
- Multi-user database setup
- Centralized configuration management
- Advanced security and audit logging

---

**🎯 You're now ready to harness AI-powered business intelligence from your Telegram conversations!**

For additional support, check the main README.md or create an issue in the repository. 
