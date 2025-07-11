#!/usr/bin/env python3
"""
Google Service Account Setup Guide
=================================
This script provides step-by-step instructions for creating a new Google service account
for the BD Analytics system and optionally integrating with Google Cloud Agent Starter Pack.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def print_service_account_setup():
    """Print step-by-step instructions for creating a service account"""
    print("🔧 Google Service Account Setup")
    print("="*60)
    
    print("\n📋 Step 1: Create New Service Account")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com")
    print("2. Select or create a project")
    print("3. Navigate to 'IAM & Admin' > 'Service Accounts'")
    print("4. Click 'CREATE SERVICE ACCOUNT'")
    print("5. Service account details:")
    print("   - Name: bd-analytics-service")
    print("   - ID: bd-analytics-service") 
    print("   - Description: Service account for BD Analytics system")
    
    print("\n🔐 Step 2: Grant Permissions")
    print("Required roles for your service account:")
    print("   ✅ Editor (for general Google Sheets access)")
    print("   ✅ Storage Admin (if using Google Cloud Storage)")
    print("   ✅ Vertex AI User (if using AI features)")
    print("   ✅ Cloud Run Developer (if deploying to Cloud Run)")
    
    print("\n🔑 Step 3: Create Key")
    print("1. Click on your new service account")
    print("2. Go to 'Keys' tab")
    print("3. Click 'ADD KEY' > 'Create new key'")
    print("4. Choose 'JSON' format")
    print("5. Download the key file")
    print("6. Rename it to 'google_service_account.json'")
    print("7. Place it in your project directory")
    
    print("\n📊 Step 4: Enable Required APIs")
    print("Enable these APIs in Google Cloud Console:")
    print("   ✅ Google Sheets API")
    print("   ✅ Google Drive API") 
    print("   ✅ Vertex AI API (for advanced AI features)")
    print("   ✅ Cloud Run API (for deployment)")
    print("   ✅ Cloud Build API (for CI/CD)")

def print_agent_starter_pack_integration():
    """Print information about integrating with Google Cloud Agent Starter Pack"""
    print("\n\n🚀 Google Cloud Agent Starter Pack Integration")
    print("="*60)
    
    print("\n🎯 Why This Is Perfect For Your System:")
    print("✅ Production-ready AI agent infrastructure")
    print("✅ Built-in monitoring and observability") 
    print("✅ Automated CI/CD pipelines")
    print("✅ RAG agents perfect for BD intelligence")
    print("✅ Integration with Vertex AI for advanced AI")
    print("✅ Scalable deployment on Cloud Run")
    
    print("\n🏗️ Migration Strategy:")
    print("1. **Phase 1**: Create agent with your existing data")
    print("2. **Phase 2**: Deploy BD analytics as Cloud Run service")
    print("3. **Phase 3**: Add advanced AI features with Vertex AI")
    print("4. **Phase 4**: Implement multi-agent workflows")
    
    print("\n📋 Available Agent Templates for BD Analytics:")
    print("🤖 agentic_rag - Perfect for BD document/contact analysis")
    print("🤖 adk_gemini_fullstack - Complex BD workflows with human-in-loop")
    print("🤖 live_api - Real-time BD interactions with multimodal support")
    print("🤖 crewai_coding_crew - Multi-agent BD teams")

def generate_migration_plan():
    """Generate a migration plan to Google Cloud Agent Starter Pack"""
    
    migration_plan = {
        "phase_1_local_agent": {
            "description": "Create local agent using your existing BD data",
            "steps": [
                "Install agent-starter-pack: pip install --upgrade agent-starter-pack",
                "Create agent project: agent-starter-pack create bd-analytics-agent",
                "Choose 'agentic_rag' template for BD intelligence",
                "Integrate your local database as data source",
                "Test agent locally with your contact/interaction data"
            ],
            "timeline": "1-2 days",
            "benefits": ["Immediate AI enhancement", "Local testing", "Familiar environment"]
        },
        "phase_2_cloud_deployment": {
            "description": "Deploy to Google Cloud Run with full infrastructure",
            "steps": [
                "Configure Google Cloud project and APIs",
                "Set up Terraform for infrastructure as code",
                "Deploy agent to Cloud Run",
                "Set up monitoring and logging", 
                "Configure auto-scaling and load balancing"
            ],
            "timeline": "2-3 days",
            "benefits": ["Production scalability", "Built-in monitoring", "Auto-scaling"]
        },
        "phase_3_ai_enhancement": {
            "description": "Add advanced Vertex AI capabilities",
            "steps": [
                "Integrate Vertex AI Search for contact intelligence",
                "Add Gemini for advanced conversation analysis",
                "Implement vector search for semantic contact matching",
                "Add real-time lead scoring with AI",
                "Create predictive BD analytics"
            ],
            "timeline": "3-5 days", 
            "benefits": ["Advanced AI insights", "Predictive analytics", "Intelligent automation"]
        },
        "phase_4_multi_agent": {
            "description": "Multi-agent BD workflows",
            "steps": [
                "Lead qualification agent",
                "Follow-up scheduling agent", 
                "Proposal generation agent",
                "Performance monitoring agent",
                "Human-in-the-loop approval workflows"
            ],
            "timeline": "1-2 weeks",
            "benefits": ["Automated BD workflows", "Specialized agents", "Human oversight"]
        }
    }
    
    return migration_plan

def create_agent_starter_pack_setup():
    """Create setup instructions for Google Cloud Agent Starter Pack"""
    
    setup_content = """# BD Analytics Agent Setup with Google Cloud Agent Starter Pack

## Quick Start Commands

```bash
# Install the agent starter pack
pip install --upgrade agent-starter-pack

# Create your BD analytics agent
agent-starter-pack create bd-analytics-agent

# Choose template: agentic_rag (recommended for BD intelligence)
cd bd-analytics-agent

# Configure for your BD data
# Edit the agent configuration to connect to your local database
```

## Recommended Template: Agentic RAG

The **agentic_rag** template is perfect for your BD system because:
- ✅ Retrieval-Augmented Generation for contact/interaction analysis
- ✅ Support for Vertex AI Search and Vector Search
- ✅ Document Q&A capabilities for BD intelligence
- ✅ Integration with your existing data sources

## Integration Points

### 1. Data Connection
- Connect agent to your local BD database
- Sync contact and interaction data to Vector Search
- Create embeddings for semantic search

### 2. BD Intelligence Features
- "Who are my hottest leads this week?"
- "What opportunities did we discuss with Company X?"
- "Which contacts need follow-up?"
- "Generate a BD summary for this quarter"

### 3. Automation Workflows
- Automatic lead scoring updates
- Follow-up reminders and scheduling
- Opportunity pipeline analysis
- Executive report generation

## Deployment Architecture

```
Local BD Database (Source of Truth)
    ↓
Google Cloud Agent (RAG + AI)
    ↓
Vertex AI Search (Contact Intelligence)
    ↓
Cloud Run (Scalable Deployment)
    ↓
Google Sheets (Reporting Dashboard)
```

## Next Steps After Service Account Setup

1. Run the agent creation command
2. Configure data integration
3. Test locally with your existing data
4. Deploy to Cloud Run for production use
"""
    
    with open('AGENT_SETUP_GUIDE.md', 'w') as f:
        f.write(setup_content)
    
    print("✅ Created AGENT_SETUP_GUIDE.md with detailed setup instructions")

def main():
    """Main setup function"""
    print_service_account_setup()
    print_agent_starter_pack_integration()
    
    # Generate migration plan
    plan = generate_migration_plan()
    
    print("\n📋 Migration Timeline & Phases:")
    for phase, details in plan.items():
        print(f"\n🔹 {phase.replace('_', ' ').title()}")
        print(f"   📝 {details['description']}")
        print(f"   ⏱️ Timeline: {details['timeline']}")
        print(f"   🎯 Benefits: {', '.join(details['benefits'])}")
    
    # Create setup guide
    create_agent_starter_pack_setup()
    
    print("\n🎉 Next Steps:")
    print("1. ⚡ Create your Google service account (instructions above)")
    print("2. 🚀 Install agent-starter-pack: pip install --upgrade agent-starter-pack")
    print("3. 🤖 Create your agent: agent-starter-pack create bd-analytics-agent")
    print("4. 📖 Follow AGENT_SETUP_GUIDE.md for detailed integration")
    
    print("\n🔗 Useful Links:")
    print("📚 Agent Starter Pack Docs: https://googlecloudplatform.github.io/agent-starter-pack/")
    print("🎬 Video Tutorial: https://youtu.be/your-tutorial-link")
    print("💾 GitHub Repository: https://github.com/GoogleCloudPlatform/agent-starter-pack")

if __name__ == "__main__":
    main() 