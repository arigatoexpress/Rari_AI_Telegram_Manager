# BD Analytics Agent Setup Instructions

## 🎯 **Your Personalized Setup Guide**

Generated: 2025-07-09 21:53:55

## ✅ **What's Already Done**

- ✅ Agent created with Google Cloud Agent Starter Pack
- ✅ BD data files copied to agent project
- ✅ Environment configuration prepared
- ✅ BD agent integration code created

## 🔧 **Next Steps**

### 1. Create Google Service Account

Follow the detailed guide in `../AGENT_INTEGRATION_STEPS.md` to:
- Create a new Google Cloud project (recommended)
- Set up service account with proper permissions
- Download service account key
- Enable required APIs

### 2. Configure Environment

Edit `deployment/terraform/vars/my-env.tfvars`:

```hcl
# Update these with your actual values:
project_name           = "bd-analytics"
prod_project_id        = "YOUR_GOOGLE_CLOUD_PROJECT_ID"
staging_project_id     = "YOUR_GOOGLE_CLOUD_PROJECT_ID" 
cicd_runner_project_id = "YOUR_GOOGLE_CLOUD_PROJECT_ID"
region                 = "us-central1"
```

### 3. Test Locally

```bash
# Install dependencies
make install

# Launch development playground
make playground
```

### 4. Test BD Queries

In the playground, try:
- "Who are my hottest leads this week?"
- "Which contacts need follow-up?"
- "What's my pipeline value for Q4?"
- "Generate a BD summary report"

### 5. Deploy to Production

```bash
# Set up infrastructure
cd deployment/terraform
terraform init
terraform apply --var-file vars/my-env.tfvars

# Deploy application
cd ../..
make backend
```

## 🔗 **Integration Points**

### BD Database Connection
Your agent will automatically connect to your existing BD database via the `core.local_database_manager` module.

### Google Sheets Sync
The agent maintains compatibility with your existing Google Sheets workflow.

### AI Capabilities
- Natural language BD queries
- Intelligent lead scoring
- Automated insights and reporting
- Predictive analytics

## 📊 **Expected Capabilities**

After setup, you'll have:
- 🤖 AI-powered BD assistant
- 📈 Real-time pipeline analytics  
- 🎯 Intelligent lead recommendations
- 📊 Automated executive reporting
- 🌐 Web interface for team collaboration
- 🔗 API access for integrations

## 🆘 **Troubleshooting**

### Common Issues:

1. **Database connection fails**
   - Ensure your original BD system is accessible
   - Check Python path in bd_agent.py

2. **Environment setup issues**
   - Verify Google Cloud project permissions
   - Check service account key placement

3. **Deployment failures**
   - Confirm all required APIs are enabled
   - Verify terraform configuration

## 📞 **Support Resources**

- **Main Guide**: `../AGENT_INTEGRATION_STEPS.md`
- **Agent Docs**: `README.md`
- **Deployment**: `deployment/README.md`
- **AI Assistant**: `GEMINI.md` (ask Gemini about your agent)

## 🎉 **Success Checklist**

- [ ] Google service account created
- [ ] Environment variables configured
- [ ] Local testing successful
- [ ] BD queries working
- [ ] Production deployment complete
- [ ] Team trained on new capabilities

**You're building an enterprise-grade AI agent platform! 🚀**
