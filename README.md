# Telegram BD Intelligence System 🚀

**Advanced AI-powered business development and lead management platform with Telegram integration.**

Transform your Telegram conversations into actionable business intelligence using ChatGPT analysis, automated lead scoring, and professional Google Sheets reporting.

---

## ✨ Key Features

### 🧠 **AI-Powered Business Intelligence**
- **ChatGPT Analysis** - Deep conversation analysis for business opportunities
- **Smart Lead Scoring** - Automated scoring (0-100) based on interaction patterns
- **Sentiment Analysis** - Track engagement levels and buying signals
- **Deal Intelligence** - AI-powered insights for closing strategies

### 📊 **Advanced Analytics & CRM**
- **Contact Management** - Comprehensive contact and organization tracking
- **Pipeline Analytics** - Visual deal progression and conversion metrics
- **Performance Dashboards** - Real-time KPIs and business metrics
- **Follow-up Automation** - Smart reminders and action recommendations

### 📱 **Telegram Integration**
- **Chat History Analysis** - Extract insights from existing conversations
- **Real-time Monitoring** - Live conversation analysis and opportunity detection
- **Group Chat Intelligence** - Business network analysis and relationship mapping
- **Contact Enrichment** - Automatic contact information and lead scoring

### 📈 **Professional Reporting**
- **Google Sheets Integration** - Automated dashboard creation and sync
- **Executive Reports** - AI-generated summaries and recommendations
- **Export Capabilities** - CSV, Excel, and JSON export formats
- **Team Collaboration** - Shareable dashboards and insights

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repository-url>
cd tg_manager_v2

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and configure your credentials:

```bash
# Copy environment template
cp env.template .env

# Edit .env with your actual credentials
nano .env
```

**Required Configuration:**

```env
# OpenAI API (Required for AI analysis)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Telegram API (Required for Telegram integration)
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890

# Google Sheets (Optional - for reporting)
GOOGLE_SERVICE_ACCOUNT_EMAIL=your_service_account@your_project.iam.gserviceaccount.com
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Telegram Bot (Optional - for bot interface)
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_USER_ID=your_telegram_user_id
```

### 3. First Run

```bash
# Run system setup and health check
python main.py setup
python main.py health

# Start the application
python main.py
```

---

## 🎯 Usage

### **Main Application Interface**

```bash
# Interactive mode (default)
python main.py

# Direct commands
python main.py dashboard    # Analytics dashboard
python main.py analyze      # Run AI analysis
python main.py export       # Export to Google Sheets
python main.py bot          # Start Telegram bot
```

### **Key Commands**

#### 🔍 **Analytics & Insights**
- `dashboard` - Real-time analytics dashboard with key metrics
- `analyze` - Comprehensive AI analysis of conversations and leads
- `report` - Generate executive reports with actionable insights

#### 📊 **Data Management**
- `import` - Import and analyze Telegram chat history
- `export` - Export data to Google Sheets with professional formatting
- `backup` - Create secure backups of your data
- `status` - Show system status and database health

#### 🤖 **Interactive Modes**
- `bot` - Start Telegram bot for real-time interaction
- `interactive` - Interactive CLI mode with all commands

#### ⚙️ **Setup & Configuration**
- `setup` - Initial system setup and configuration
- `config` - Show current configuration and requirements
- `health` - Comprehensive system health check

---

## 🏗️ Architecture

### **Core Components**

```
📱 Telegram Integration Layer
    ↓
🧠 AI Analysis Engine (OpenAI/ChatGPT)
    ↓
🗄️ Local Database (SQLite)
    ↓
📊 Analytics & Reporting Layer
    ↓
📈 Google Sheets Export
```

### **Core Modules (`core/`)**
- **`ai_analyzer.py`** - AI-powered conversation analysis
- **`lead_tracking_db.py`** - CRM database and lead management
- **`data_manager.py`** - Database operations and sync
- **`bd_intelligence.py`** - Business development intelligence
- **`google_sheets_manager.py`** - Google Sheets integration
- **`telegram_extractor.py`** - Telegram data extraction

---

## 📋 API Keys & Setup Guide

### **OpenAI API Key** (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create account and generate API key
3. Add to `.env`: `OPENAI_API_KEY=sk-proj-your-key-here`

### **Telegram API** (Required for Telegram features)
1. Visit [my.telegram.org/apps](https://my.telegram.org/apps)
2. Create an application and get API credentials
3. Add to `.env`:
   ```env
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=+1234567890
   ```

### **Telegram Bot** (Optional)
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Get your User ID from [@userinfobot](https://t.me/userinfobot)
4. Add to `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_USER_ID=your_user_id
   ```

### **Google Sheets** (Optional)
1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a service account and download credentials
4. Share your Google Sheet with the service account email
5. Add to `.env`:
   ```env
   GOOGLE_SERVICE_ACCOUNT_EMAIL=your_service_account@project.iam.gserviceaccount.com
   GOOGLE_SHEET_ID=your_sheet_id
   ```

---

## 🔒 Security & Privacy

### **Data Protection**
- **Local Storage** - All data stored locally in encrypted SQLite databases
- **No Cloud Dependencies** - Works completely offline (except for AI analysis)
- **Privacy First** - Your conversation data never leaves your machine
- **Secure APIs** - All API communications use industry-standard encryption

### **Environment Security**
- **`.env` Protection** - Environment files automatically excluded from git
- **Template System** - Safe templates provided for configuration
- **No Hardcoded Secrets** - All sensitive data configurable via environment

### **Git Safety**
The repository is configured to automatically exclude:
- Environment files (`.env*`)
- Database files (`data/`, `*.db`)
- Exports and reports (`exports/`, `reports/`)
- Cache and logs (`cache/`, `logs/`)
- Any files containing personal data

---

## 📊 Sample Outputs

### **Analytics Dashboard**
```
🚀 TELEGRAM BD INTELLIGENCE DASHBOARD
==========================================
📊 Total Contacts: 150
🎯 Active Leads: 23 (15% conversion rate)
💰 Pipeline Value: $125,000
📈 This Month: +12 new leads
🔥 Hot Leads: 5 requiring immediate follow-up
```

### **AI Analysis Report**
```
🧠 AI ANALYSIS SUMMARY
======================
✅ Processed 1,247 conversations
🎯 Identified 23 business opportunities
📈 Lead score improvements: +15% average
💡 Key insights: DeFi/crypto focus, institutional interest
🚀 Recommended actions: 5 immediate follow-ups
```

---

## 🔧 Advanced Configuration

### **Database Settings**
```env
DATABASE_PATH=data/bd_database.db
MAX_MESSAGES_PER_CHAT=1000
EXTRACTION_DAYS_BACK=180
BATCH_SIZE=100
```

### **AI Configuration**
```env
AI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1500
```

### **Performance Tuning**
```env
LOG_LEVEL=INFO
CACHE_SIZE=1000
BACKUP_RETENTION_DAYS=30
```

---

## 🛠️ Development

### **Project Structure**
```
tg_manager_v2/
├── main.py                 # Main application entry point
├── core/                   # Core modules
│   ├── ai_analyzer.py     # AI analysis engine
│   ├── lead_tracking_db.py # CRM database
│   └── ...                # Additional core modules
├── env.template           # Environment configuration template
├── requirements.txt       # Python dependencies
├── start_ultimate_bd_bot.py # Telegram bot interface
└── setup_telegram_bot.py  # System setup utilities
```

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### **Quick Troubleshooting**
```bash
python main.py health    # Check system status
python main.py config    # Verify configuration
python main.py setup     # Re-run setup if needed
```

### **Common Issues**
- **Module Import Errors**: Run `pip install -r requirements.txt`
- **API Key Issues**: Verify your `.env` configuration
- **Database Errors**: Check that `data/` directory is writable
- **Telegram Auth**: Re-run setup for phone verification

For additional support, please check the documentation in the repository or create an issue.

---

**🎯 Transform your business development with AI-powered conversation intelligence!** 