# 🤖 Unified Telegram Business Development Bot

A comprehensive Telegram bot that combines message syncing, AI-powered business development analysis, and automated insights for professional networking and investment opportunities.

## 🚀 Features

### 📊 Message Syncing
- **Automatic sync** of all Telegram messages every 30 minutes
- **Differential sync** - only syncs new messages since last sync
- **Multi-chat support** - syncs from all your Telegram chats
- **Persistent storage** - SQLite database for reliable data retention

### 🤖 AI-Powered Analysis
- **ChatGPT integration** for advanced business analysis
- **Contact classification** (investors, LPs, community, partners)
- **Engagement scoring** and sentiment analysis
- **Investment potential rating** (0-10 scale)
- **Automated insights** and recommendations

### 💼 Business Development Tools
- **Daily briefings** with actionable insights
- **Contact ratings** and engagement metrics
- **Follow-up recommendations** with personalized messages
- **Hot lead identification** and opportunity scoring
- **Partnership opportunity detection**

### 🛡️ Robust Infrastructure
- **Single instance management** - prevents multiple bot instances
- **Graceful error handling** and automatic recovery
- **Comprehensive logging** and monitoring
- **Signal handling** for clean shutdowns
- **Session persistence** across restarts

## 📁 Project Structure

```
tg_manager_v2/
├── telegram_bd_bot.py      # Main unified bot
├── start_bot.py           # Startup script with pre-flight checks
├── manage_bot.py          # Bot management commands
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── core/                  # Core modules
│   ├── data_manager.py    # Database and data operations
│   ├── bd_analyzer.py     # Business development AI analyzer
│   └── ai_analyzer.py     # General AI analysis functions
├── logs/                  # Log files
│   └── bot.log           # Main bot log
├── data/                  # Database files
│   └── chat_history.db   # SQLite database
└── sync_session.session   # Telethon session file
```

## 🔧 Setup

### 1. Environment Setup

Create a `.env` file with your credentials:

```bash
# Telegram Bot (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Telegram API (from my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# User Authorization
USER_ID=your_user_id
AUTHORIZED_USERS=user_id1,user_id2

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Bot

```bash
# Method 1: Direct startup
python3 start_bot.py

# Method 2: Using management script
python3 manage_bot.py start
```

## 🎮 Bot Commands

### 📊 Status & Info
- `/start` - Welcome message and bot overview
- `/help` - Complete command reference
- `/status` - Bot status, sync info, and statistics
- `/chats` - List all synced chats with message counts

### 🔄 Message Syncing
- `/sync` - Manually sync messages from all chats
- Auto-sync runs every 30 minutes automatically

### 🤖 AI Analysis
- `/analyze [days]` - Analyze recent messages (default: 7 days)
- `/analyze_all` - Comprehensive analysis of all chats

### 💼 Business Development
- `/briefing` - Daily BD briefing with key insights
- `/contacts` - Contact ratings and engagement analysis
- `/followups` - Personalized follow-up recommendations
- `/opportunities` - Hot leads and investment opportunities
- `/rate` - Top-rated contacts and potential scores

## 🛠️ Management Commands

```bash
# Start the bot
python3 manage_bot.py start

# Stop the bot
python3 manage_bot.py stop

# Restart the bot
python3 manage_bot.py restart

# Check status
python3 manage_bot.py status

# View logs
python3 manage_bot.py logs

# Clean up stale files
python3 manage_bot.py cleanup
```

## 📊 Business Context

This bot is designed for **DeFi protocol business development** with focus on:

- **Investment Fundraising**: VC/angel/institutional investor outreach
- **Liquidity Provision**: Attracting LPs and yield farmers
- **Community Building**: DeFi community partnerships
- **Strategic Partnerships**: Protocol integrations and collaborations

### Key Metrics Tracked:
- **TVL potential** and liquidity interest
- **Investment commitment** signals
- **Community engagement** levels
- **Partnership opportunities**

## 🔐 Security Features

- **User authorization** - Only authorized users can access commands
- **Environment isolation** - Sensitive data in environment variables
- **Session management** - Secure Telethon session handling
- **Instance locking** - Prevents multiple bot instances
- **Graceful shutdowns** - Clean resource cleanup

## 📈 Analytics & Insights

The bot provides:

1. **Contact Classification**:
   - Investors (VCs, angels, institutions)
   - Liquidity Providers (whales, yield farmers)
   - Community Leaders (influencers, builders)
   - Strategic Partners (protocols, platforms)

2. **Engagement Scoring**:
   - Hot (9-10): Immediate follow-up required
   - Warm (7-8): High potential, regular engagement
   - Cold (4-6): Occasional outreach
   - Unresponsive (0-3): Minimal engagement

3. **Investment Potential**:
   - Network value and connections
   - Financial capacity indicators
   - Engagement history and responsiveness
   - Strategic alignment with project goals

## 🚨 Daily Usage

### Morning Routine:
1. Check `/status` for overnight activity
2. Review `/briefing` for daily priorities
3. Check `/opportunities` for new leads

### Throughout the Day:
- Bot auto-syncs every 30 minutes
- Notifications for high-priority contacts
- Real-time message analysis and storage

### Evening Review:
1. Run `/analyze` for daily insights
2. Review `/followups` for next-day actions
3. Check `/contacts` for engagement updates

## 🔧 Troubleshooting

### Common Issues:

1. **Bot not starting**:
   ```bash
   python3 manage_bot.py cleanup
   python3 manage_bot.py start
   ```

2. **Sync issues**:
   - Check Telethon session file exists
   - Verify API credentials in .env
   - Run `/sync` manually to test

3. **AI analysis errors**:
   - Verify OpenAI API key is valid
   - Check API quota and billing
   - Review logs for specific errors

### Log Files:
- `logs/bot.log` - Main bot operations
- Check with: `python3 manage_bot.py logs`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For issues or questions:
1. Check the logs: `python3 manage_bot.py logs`
2. Review the troubleshooting section
3. Ensure all environment variables are set correctly
4. Verify all dependencies are installed

---

**Built for professional business development in the DeFi space** 🚀 