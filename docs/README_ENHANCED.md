# Enhanced Telegram Manager v2.0

A comprehensive business development platform with AI-powered message analysis, Google Sheets integration, agentic framework, and decentralized compute deployment.

## 🚀 New Features

### 1. **Google Sheets Integration**
- **Business Briefs**: Automatic generation and storage of professional business briefs
- **Lead Tracking**: Comprehensive lead management with follow-up scheduling
- **Message Analytics**: Detailed analytics and insights from all conversations
- **Dashboard**: Real-time business metrics and conversion tracking

### 2. **Elizao Agentic Framework**
- **Autonomous Agents**: Business analyst and lead manager agents
- **Intelligent Processing**: AI-powered message analysis and recommendations
- **Learning System**: Agents learn from interactions and improve over time
- **Task Orchestration**: Coordinated multi-agent workflows

### 3. **DePIN Deployment**
- **24/7 Cloud Deployment**: Run without local machine dependency
- **Multiple Providers**: Nosana, Akash, Sui Compute, Flux support
- **Cost Optimization**: Automatic provider selection based on cost/performance
- **Scalable Infrastructure**: Enterprise-grade reliability

### 4. **Enhanced Message Reading**
- **Full Message Access**: Read all Telegram messages using user-level API
- **Business Intelligence**: Professional, conversion-optimized analysis
- **Export Capabilities**: JSON, CSV, and text export formats
- **Interactive Mode**: Real-time message browsing and search

## 📋 Prerequisites

1. **Telegram API Credentials** (https://my.telegram.org)
2. **Google Service Account** (for Sheets integration)
3. **DePIN Provider Accounts** (optional, for cloud deployment)
4. **AI Backend** (Ollama local or Atoma DePIN)

## 🔧 Setup

### 1. Environment Configuration

Copy `env.example` to `.env` and configure:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# AI Backend
AI_BACKEND=ollama  # or "atoma"
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id

# DePIN Providers (optional)
NOSANA_API_KEY=your_nosana_key
SUI_RPC_URL=https://fullnode.mainnet.sui.io
SUI_PRIVATE_KEY=your_sui_key
AKASH_WALLET_ADDRESS=your_akash_wallet
AKASH_PRIVATE_KEY=your_akash_key

# Agentic Framework
AGENT_ENABLED=true
AGENT_CYCLE_INTERVAL=300
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Google Sheets

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a service account
4. Download the JSON key file
5. Share your spreadsheet with the service account email

### 4. Setup DePIN Providers (Optional)

#### Nosana (Recommended)
- Sign up at https://nosana.compute
- Get API key
- Add to `.env`

#### Sui Compute (Future)
- Set up Sui wallet
- Configure RPC and private key
- Add to `.env`

#### Akash Network
- Create Akash wallet
- Get wallet address and private key
- Add to `.env`

## 🎯 Usage

### Quick Start

```bash
# Run the comprehensive deployment manager
python deploy_to_depin.py
```

### Message Reading & Analysis

```bash
# Read all messages with business analysis
python telegram_message_reader.py --summarize --export-format json

# Interactive mode
python telegram_message_reader.py --interactive

# Recent messages only
python telegram_message_reader.py --recent-days 7 --chats-only
```

### Google Sheets Integration

```bash
# Test Google Sheets setup
python google_sheets_integration.py

# Export business briefs to sheets
python telegram_message_reader.py --summarize
```

### Agentic Framework

```bash
# Test agentic framework
python elizao_agentic_framework.py

# Run with agents enabled
AGENT_ENABLED=true python deploy_to_depin.py
```

### DePIN Deployment

```bash
# Deploy to best available provider
python deploy_to_depin.py

# Deploy to specific provider
python deploy_to_depin.py --provider nosana
```

## 📊 Google Sheets Structure

The system creates three main sheets:

### 1. Business Briefs
- Chat Title, Type, Date
- Executive Brief, Key Insights
- Conversion Opportunities
- Actionable Recommendations
- Priority, Status

### 2. Lead Tracking
- Contact Name, Company
- Phone, Email, Source
- Status, Last Contact
- Next Follow Up, Notes

### 3. Message Analytics
- Date, Chat Title
- Message Counts, Response Times
- Keywords, Sentiment
- Business Opportunities

## 🤖 Agentic Framework

### Available Agents

1. **Business Analyst Agent**
   - Analyzes messages for business opportunities
   - Generates professional briefs
   - Identifies conversion triggers

2. **Lead Manager Agent**
   - Manages lead follow-ups
   - Schedules next actions
   - Updates lead status

### Agent Capabilities

- **Think**: AI-powered analysis and decision making
- **Act**: Execute actions and update systems
- **Observe**: Learn from results and improve
- **Memory**: Maintain context and patterns

## 🌐 DePIN Providers

### Cost Comparison (per hour)

| Provider | Cost/Hour | Monthly (24/7) |
|----------|-----------|----------------|
| Sui Compute | $0.001 | $0.72 |
| Akash | $0.0015 | $1.08 |
| Nosana | $0.002 | $1.44 |
| Flux | $0.003 | $2.16 |
| Fly.io | $0.004 | $2.88 |
| Render | $0.005 | $3.60 |

### Provider Features

- **Nosana**: Easy deployment, good documentation
- **Sui Compute**: Lowest cost, Sui ecosystem
- **Akash**: Mature network, good reliability
- **Flux**: High performance, enterprise features

## 🔒 Security & Privacy

- **Local Processing**: AI analysis happens locally
- **Encrypted Storage**: All data encrypted at rest
- **Secure APIs**: OAuth2 for Google Sheets
- **Private Keys**: Stored securely in environment variables

## 📈 Business Intelligence

### Automated Insights

1. **Lead Scoring**: Automatic lead prioritization
2. **Conversion Tracking**: Monitor deal progression
3. **Response Analysis**: Optimize communication
4. **Opportunity Detection**: Identify business opportunities

### Professional Output

- **Executive Briefs**: C-level ready summaries
- **Actionable Recommendations**: Specific next steps
- **Conversion Optimization**: Focus on business growth
- **Stoic Tone**: Professional, authoritative communication

## 🛠️ Troubleshooting

### Common Issues

1. **Google Sheets Access**
   - Verify service account permissions
   - Check spreadsheet sharing settings
   - Ensure API is enabled

2. **DePIN Deployment**
   - Verify API keys and credentials
   - Check provider status
   - Review deployment logs

3. **Agentic Framework**
   - Check AI backend availability
   - Verify environment variables
   - Review agent logs

### Getting Help

1. Check the logs for specific error messages
2. Verify all environment variables are set
3. Test individual components separately
4. Review provider documentation

## 🚀 Advanced Features

### Custom AI Prompts

Modify `context.md` for custom business analysis:

```markdown
You are a senior business development executive.
Focus on conversion opportunities and actionable insights.
Maintain professional, stoic communication style.
```

### Automated Workflows

Set up automated tasks:

```bash
# Daily business briefs
0 9 * * * python telegram_message_reader.py --summarize

# Weekly lead follow-ups
0 10 * * 1 python elizao_agentic_framework.py --task lead_followup
```

### Custom DePIN Deployment

Create custom deployment configurations:

```python
from depin_solutions import DeploymentConfig, ComputeResource

config = DeploymentConfig(
    provider=DePINProvider.NOSANA,
    resources=ComputeResource(cpu_cores=2, memory_gb=4, storage_gb=20),
    docker_image="your-custom-image:latest",
    environment_vars={"CUSTOM_VAR": "value"},
    ports=[8080, 8081]
)
```

## 📝 Examples

### Business Brief Output

```
Executive Brief:
Recent conversation with TechCorp shows strong interest in our AI solution.
Client expressed budget approval and timeline constraints.

Key Insights:
• Budget: $50K-100K range confirmed
• Timeline: Q1 2024 implementation
• Decision maker: CTO Sarah Johnson
• Technical requirements: API integration needed

Conversion Opportunities:
• Schedule technical demo
• Prepare proposal within budget range
• Address API integration concerns

Actionable Recommendations:
1. Schedule demo with technical team
2. Prepare detailed proposal by Friday
3. Follow up on API documentation request

Next Steps:
• Send calendar invite for demo
• Prepare technical proposal
• Schedule follow-up call
```

### Lead Management

```
Lead: John Smith (TechCorp)
Status: Proposal Sent
Next Follow-up: 2024-01-15
Priority: High
Notes: Interested in AI integration, budget approved
```

## 🎉 Getting Started

1. **Setup**: Configure environment variables
2. **Test**: Run individual components
3. **Deploy**: Choose local or cloud deployment
4. **Monitor**: Track business metrics in Google Sheets
5. **Optimize**: Adjust AI prompts and agent behavior

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review provider documentation
3. Test with minimal configuration
4. Check logs for detailed error messages

---

**Transform your Telegram conversations into actionable business intelligence with AI-powered analysis, automated lead management, and professional insights.** 🚀 