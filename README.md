# Telegram Manager Bot - Consolidated

## 🚀 Quick Start

```bash
# 1. Setup environment
cp env.example .env
# Edit .env with your credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the bot
python telegram_manager_bot.py

# 4. Deploy to Nosana
python deploy_to_nosana.py
```

## 📁 Project Structure

```
tg_manager_v2/
├── telegram_manager_bot.py              # Main bot (NEW!)
├── telegram_manager_bot_unified.py      # Setup tests
├── ollama_client.py                     # Ollama AI client
├── atoma_client.py                      # Atoma AI client
├── nosana_client.py                     # Nosana SDK
├── google_sheets_integration.py         # Google Sheets
├── team_access_manager.py               # Team management
├── deploy_to_nosana.py                  # Nosana deployment
├── test_suite.py                        # Testing
├── requirements.txt                     # Dependencies
├── env.example                          # Configuration template
├── README_UNIFIED.md                    # Full documentation
├── deployment/                          # Deployment scripts
├── testing/                             # Test files
├── docs/                                # Documentation
├── config/                              # Configuration files
├── scripts/                             # Utility scripts
└── deployment_package/                  # Clean deployment package
```

## 🎯 Key Features

- 🤖 **AI Integration**: Ollama, Atoma, OpenAI
- 📊 **Business Intelligence**: Automated analysis and insights
- 👥 **Team Management**: Role-based access control
- 📈 **Google Sheets**: Automated data export
- 🚀 **Nosana Deployment**: GPU-powered hosting
- 🔒 **Security**: API keys, rate limiting, logging
- 🧪 **Testing**: Comprehensive test suite

## 📱 Bot Commands

### Basic Commands
- `/start` - Show main menu and welcome message
- `/help` - Show detailed help and command reference
- `/status` - Check bot and component status

### Notes & Organization
- `/note <text>` - Save a note to Google Sheets
- `/summary` - View recent notes and summaries
- `/brief` - Generate business brief from your data

### AI Features
- `/generate <prompt>` - Generate text with AI
- `/ai_status` - Check AI backend status

### Data Management
- `/leads` - View leads from Google Sheets
- `/contacts` - View contact profiles
- `/analytics` - View usage analytics

### Utilities
- `/meeting [topic]` - Generate meeting link
- `/status` - Check bot status

## 📚 Documentation

- **Main Guide**: `README_UNIFIED.md`
- **Nosana GPU Guide**: `nosana_gpu_guide.md`
- **Security Guide**: `SECURITY_GUIDE.md`
- **Deployment**: `deployment/` directory

## 🛠️ Development

```bash
# Run tests
python test_suite.py

# Check bot status
python test_bot_status.py

# Manage team access
python team_access_manager.py

# Deploy to Nosana
python deploy_to_nosana.py
```

## 📞 Support

- Check `docs/` for detailed documentation
- Run `python test_suite.py` for diagnostics
- See `README_UNIFIED.md` for complete guide
