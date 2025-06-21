# Telegram Manager Bot - Unified Documentation

## 🚀 Overview

A comprehensive Telegram bot system with AI backends, team management, Google Sheets integration, and multiple deployment options including Nosana, Akash, and local deployment.

## 📋 Features

### 🤖 Core Bot Features
- **Message Processing**: Read and analyze all Telegram messages
- **AI Integration**: Multiple AI backends (Ollama, Atoma, ChatGPT)
- **Business Intelligence**: Generate business briefs, summaries, and insights
- **Team Management**: Role-based access control with whitelist
- **Google Sheets**: Automated data export and lead tracking
- **Security**: API key authentication, rate limiting, logging

### 🏗️ Deployment Options
- **Nosana**: GPU-powered decentralized compute
- **Akash**: Alternative decentralized hosting
- **Local**: Development and testing
- **Docker**: Containerized deployment
- **Jupyter**: Notebook-based deployment

## 🛠️ Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo>
cd tg_manager_v2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` with your credentials:
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
USER_ID=your_user_id

# AI Backends
OLLAMA_BASE_URL=http://localhost:11434
ATOMA_API_KEY=your_atoma_key
OPENAI_API_KEY=your_openai_key

# Google Sheets (Optional)
GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id

# Nosana (Optional)
NOSANA_API_KEY=your_nosana_key

# Security
SECRET_KEY=your_secret_key
```

### 3. Run the Bot

```bash
# Basic bot
python telegram_manager_bot.py

# Unified bot with all features
python telegram_manager_bot_unified.py

# Team access management
python team_access_manager.py
```

## 🚀 Deployment Options

### Option 1: Nosana GPU Deployment (Recommended)

**Best for:** Production teams, AI workloads, 24/7 operation

#### Quick Deploy:
```bash
# Create deployment package
python deploy_to_nosana.py

# Follow the web interface instructions
# Go to https://nosana.com → Deploy Now
```

#### Manual Deploy:
1. **Get API Key**: Visit [nosana.com](https://nosana.com) → Dashboard → API Keys
2. **Create Package**: Run `python deploy_to_nosana.py`
3. **Upload Files**: Use web interface or CLI
4. **Select GPU**: RTX 3090 (24GB) recommended
5. **Set Environment**: Add all required variables
6. **Deploy**: Start your bot

**Costs:**
- RTX 3090: $350-400/month
- RTX 4090: $500-600/month
- RTX 3080 Ti: $250-300/month

### Option 2: Akash Deployment

**Best for:** Alternative decentralized hosting

```bash
# Deploy to Akash
python deploy_to_akash.py

# Follow Akash CLI instructions
akash tx deployment create deployment.yml
```

### Option 3: Local Development

**Best for:** Testing, development, small teams

```bash
# Install Ollama locally
curl -fsSL https://ollama.ai/install.sh | sh

# Pull AI model
ollama pull llama3.2:3b

# Run bot
python telegram_manager_bot_ollama.py
```

### Option 4: Docker Deployment

**Best for:** Consistent environments, easy scaling

```bash
# Build and run with Docker
docker build -t telegram-bot .
docker run -d --name telegram-bot telegram-bot

# Or use docker-compose
docker-compose up -d
```

### Option 5: Jupyter Notebook Deployment

**Best for:** Interactive development, testing

```bash
# Start Jupyter
jupyter notebook

# Open nosana_jupyter_setup.ipynb
# Follow the notebook instructions
```

## 🔧 Configuration Details

### AI Backend Configuration

#### Ollama (Local)
```python
# In your .env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Usage
from ollama_client import OllamaClient
client = OllamaClient()
response = client.generate("Hello, world!")
```

#### Atoma (DePIN)
```python
# In your .env
ATOMA_API_KEY=your_atoma_key

# Usage
from atoma_client import AtomaClient
client = AtomaClient()
response = client.generate("Hello, world!")
```

#### OpenAI (Cloud)
```python
# In your .env
OPENAI_API_KEY=your_openai_key

# Usage
import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}]
)
```

### Google Sheets Integration

1. **Create Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project → Enable Google Sheets API
   - Create service account → Download JSON key

2. **Configure Spreadsheet**:
   - Create Google Sheet
   - Share with service account email
   - Copy spreadsheet ID

3. **Set Environment**:
```env
GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

### Team Management

#### Add Team Members
```bash
python team_access_manager.py
# Follow interactive prompts
```

#### API Access
```python
# Team members can access via API
import requests

headers = {
    'Authorization': 'Bearer wl_user_987654321fedcba',
    'Content-Type': 'application/json'
}

response = requests.get('http://your-bot-url/api/status', headers=headers)
```

## 📊 Monitoring and Management

### Health Checks
```bash
# Check bot status
python test_bot_status.py

# Run comprehensive tests
python test_suite.py

# Monitor logs
tail -f bot.log
```

### Performance Monitoring
- **GPU Utilization**: Target 70-80%
- **Memory Usage**: Keep under 90%
- **Response Time**: Target <3 seconds
- **Cost per Request**: Optimize efficiency

### Scaling
- **User count > 10**: Consider RTX 4090
- **Response time > 5s**: Upgrade GPU or add instances
- **Memory usage > 80%**: Increase VRAM
- **Concurrent requests > 15**: Add load balancing

## 🔒 Security Features

### Authentication
- API key-based authentication
- Role-based access control
- Rate limiting
- Session management

### Data Protection
- Encrypted storage
- Secure API communication
- Audit logging
- Backup and recovery

### Best Practices
- Use strong API keys
- Rotate credentials regularly
- Monitor access logs
- Keep dependencies updated

## 🧪 Testing

### Run All Tests
```bash
python test_suite.py
```

### Individual Tests
```bash
# Test AI backends
python test_ai_backends.py

# Test message reader
python test_message_reader.py

# Test bot functionality
python test_bot_ai_only.py
```

### Test Report
Tests generate a comprehensive report in `test_report.txt` with:
- Environment validation
- Dependency checks
- Security audits
- Performance metrics
- Compatibility verification

## 📈 Cost Optimization

### Nosana Optimization
- **Spot Instances**: 30-50% savings
- **Reserved Instances**: 20-30% savings
- **Auto-scaling**: 40-60% savings
- **Multi-region**: Deploy in cheaper regions

### General Optimization
- Use model quantization (INT8/FP16)
- Implement request batching
- Cache frequently used responses
- Optimize model loading times

## 🆘 Troubleshooting

### Common Issues

#### Bot Not Starting
```bash
# Check environment variables
python test_suite.py

# Check logs
tail -f bot.log

# Verify dependencies
pip install -r requirements.txt
```

#### AI Backend Issues
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test Atoma
python test_ai_backends.py

# Check API keys
echo $ATOMA_API_KEY
```

#### Deployment Issues
```bash
# Check deployment package
ls -la nosana_deployment/

# Verify configuration
cat nosana_deployment/nosana_config.json

# Test Docker build
docker build -t test-bot .
```

### Getting Help
- **Documentation**: Check this README and code comments
- **Issues**: Create GitHub issue with logs
- **Community**: Join our Discord/Telegram
- **Support**: Contact for enterprise support

## 🔄 Updates and Maintenance

### Auto Updates
```bash
# Run update script
./auto_update.sh

# Or manually
git pull
pip install -r requirements.txt
```

### Backup
```bash
# Backup configuration
cp .env .env.backup
cp team_members.json team_members.backup.json

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz *.log
```

### Migration
```bash
# Export current setup
python export_config.py

# Import to new environment
python import_config.py
```

## 📚 Additional Resources

### Documentation
- [Nosana GPU Guide](nosana_gpu_guide.md)
- [Security Guide](SECURITY_GUIDE.md)
- [API Documentation](API_DOCS.md)

### Examples
- [Basic Bot](examples/basic_bot.py)
- [Advanced Features](examples/advanced_features.py)
- [Custom Integrations](examples/custom_integrations.py)

### Community
- [Discord](https://discord.gg/your-community)
- [Telegram](https://t.me/your-channel)
- [GitHub Issues](https://github.com/your-repo/issues)

## 🎯 Quick Reference

### Essential Commands
```bash
# Start bot
python telegram_manager_bot_unified.py

# Manage team
python team_access_manager.py

# Deploy to Nosana
python deploy_to_nosana.py

# Run tests
python test_suite.py

# Check status
python test_bot_status.py
```

### Environment Variables
```env
# Required
TELEGRAM_BOT_TOKEN=
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE=
USER_ID=

# Optional
OLLAMA_BASE_URL=http://localhost:11434
ATOMA_API_KEY=
NOSANA_API_KEY=
GOOGLE_SERVICE_ACCOUNT_FILE=
GOOGLE_SPREADSHEET_ID=
```

### File Structure
```
tg_manager_v2/
├── telegram_manager_bot_unified.py    # Main bot
├── team_access_manager.py             # Team management
├── deploy_to_nosana.py                # Nosana deployment
├── test_suite.py                      # Testing
├── requirements.txt                   # Dependencies
├── .env                              # Configuration
├── team_members.json                 # Team data
└── nosana_deployment/                # Deployment package
```

---

**Ready to deploy?** Choose your preferred option above and follow the step-by-step instructions!

# How to Use the Bot

## Getting Started

1. **Start the bot**
   ```bash
   python telegram_manager_bot_unified.py
   ```
2. **Invite the bot to your Telegram group or chat.**
3. **Use the following commands in your chat:**

---

## Major Commands & Examples

- `/start` — Show the welcome/help message
- `/help` — Show all available commands
- `/readall` — Dump all recent messages the bot can access
- `/add_brief Project X | Kickoff call | Client excited | Schedule next call` — Add a business brief to Google Sheets
- `/add_lead Jane Doe | Acme Corp | +123456789 | jane@acme.com | Referral` — Add a lead to Google Sheets
- `/analytics` — Get chat analytics and insights
- `/search_history invoice` — Search encrypted chat history for the word 'invoice'
- `/sheets_status` — Check Google Sheets connection and record count
- `/list_briefs` — List all business briefs from Google Sheets

---

## Google Sheets Integration
- Make sure your `.env` is set up with:
  ```env
  GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json
  GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
  ```
- Share your Google Sheet with the service account email (found in your JSON file).
- All `/add_brief` and `/add_lead` commands will sync to Google Sheets automatically.

---

## Full Chat History
- To sync all historical messages (even before the bot joined):
  ```bash
  python sync_full_history.py --api-id <your_id> --api-hash <your_hash> --phone <your_phone>
  ```
- To keep history up to date automatically:
  ```bash
  python scheduled_sync.py
  ```

---

## Troubleshooting
- If you see errors about service account files, make sure only `google_service_account.json` is present and referenced in `.env`.
- If you see errors about spreadsheet ID, check your `.env` and share permissions.
- For encryption errors, let the bot auto-generate a valid key (it will update `.env`).

--- 