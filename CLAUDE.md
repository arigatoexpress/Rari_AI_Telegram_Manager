# Rari_AI_Telegram_Manager

Telegram BD intelligence system with AI-powered conversation analysis, CRM database, and Google Sheets sync.

## Commands

| Command | Description |
|---------|-------------|
| `python main.py dashboard` | Launch analytics dashboard |
| `python main.py analyze` | Run AI analysis on conversations |
| `python main.py export` | Export data to Google Sheets |
| `python main.py bot` | Start Telegram bot |
| `python main.py import` | Import Telegram data |
| `python main.py setup` | Initial configuration wizard |
| `python main.py --help` | Show all available commands |
| `python setup_telegram_bot.py` | Configure Telegram bot credentials |

## Architecture

```
Rari_AI_Telegram_Manager/
  main.py                    # CLI router with subcommands
  start_ultimate_bd_bot.py   # Telegram bot entry point
  setup_telegram_bot.py      # Initial setup wizard
  core/
    ai_analyzer.py           # OpenAI conversation analysis
    lead_tracking_db.py      # SQLite CRM database
    telegram_extractor.py    # Telethon API client
    google_sheets_manager.py # Google Sheets sync
    smart_cache.py           # JSON disk cache (pickle removed)
  data/
    bd_database.db           # Local SQLite database (auto-created)
```

## Environment

Required:
- `OPENAI_API_KEY` - AI conversation analysis
- `TELEGRAM_API_ID` + `TELEGRAM_API_HASH` - From my.telegram.org/apps
- `TELEGRAM_PHONE` - Phone number for Telegram login

Optional:
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_USER_ID` - Bot mode
- `GOOGLE_SERVICE_ACCOUNT_EMAIL` + `GOOGLE_SHEET_ID` - Sheets sync
- `AI_MODEL=gpt-3.5-turbo` - LLM model choice
- `DATABASE_PATH=data/bd_database.db`

## Gotchas

- Telegram requires phone number authentication (interactive 2FA code during setup)
- Disk cache serialization is JSON-only (pickle was removed for security)
- Google Sheets integration optional but requires service account JSON file
- AI analysis: ~$0.02 per conversation
- SQLite database auto-created in `data/` directory on first run
- Max 1000 messages per chat by default (configurable)
- `requirements.txt` had merged lines - now fixed (openai and gspread on separate lines)
- `requirements_analytics.txt` and `requirements_bd.txt` had stdlib modules removed
