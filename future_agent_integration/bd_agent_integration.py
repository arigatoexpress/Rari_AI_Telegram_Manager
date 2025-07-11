#!/usr/bin/env python3
"""
BD Analytics Agent Integration
=============================
This script bridges your existing BD analytics system with Google Cloud Agent Starter Pack
to create a production-ready AI agent for business development intelligence.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import existing BD system components
from core.local_database_manager import get_local_db_manager
from core.sheets_sync_manager import get_sheets_sync_manager

class BDAgentDataBridge:
    """Bridge between existing BD data and Google Cloud Agent"""
    
    def __init__(self):
        self.db_manager = None
        self.data_cache = {}
        
    async def initialize(self):
        """Initialize the database connection"""
        self.db_manager = await get_local_db_manager()
        
    async def get_contacts_for_agent(self) -> List[Dict[str, Any]]:
        """Get formatted contact data for the agent"""
        if not self.db_manager:
            await self.initialize()
            
        if not self.db_manager:
            print("❌ Database manager not available")
            return []
            
        contacts = await self.db_manager.search_contacts(limit=1000)
        
        # Format for agent consumption
        agent_contacts = []
        for contact in contacts:
            agent_contact = {
                "id": contact.get('contact_id'),
                "name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                "username": contact.get('username'),
                "email": contact.get('email'),
                "organization": contact.get('organization_name'),
                "lead_score": contact.get('lead_score', 0),
                "lead_status": contact.get('lead_status'),
                "estimated_value": contact.get('estimated_value', 0),
                "tags": contact.get('tags', []),
                "last_interaction": contact.get('last_interaction'),
                "notes": contact.get('notes', '')
            }
            agent_contacts.append(agent_contact)
            
        return agent_contacts
    
    async def get_interactions_for_agent(self, contact_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get formatted interaction data for the agent"""
        if not self.db_manager:
            await self.initialize()
            
        if not self.db_manager:
            print("❌ Database manager not available")
            return []
            
        # Get interactions from database
        dataframes = await self.db_manager.export_to_dataframes()
        interactions_df = dataframes.get('interactions', None)
        
        if interactions_df is None or interactions_df.empty:
            return []
            
        # Filter by contact if specified
        if contact_id:
            interactions_df = interactions_df[interactions_df['contact_id'] == contact_id]
            
        # Format for agent
        agent_interactions = []
        for _, interaction in interactions_df.iterrows():
            agent_interaction = {
                "id": interaction.get('interaction_id'),
                "contact_id": interaction.get('contact_id'),
                "date": interaction.get('interaction_date'),
                "type": interaction.get('interaction_type', 'message'),
                "content": interaction.get('content', ''),
                "sentiment": interaction.get('sentiment_score'),
                "topics": interaction.get('key_topics', []),
                "opportunities": interaction.get('opportunities_identified', []),
                "follow_up_required": interaction.get('follow_up_required', False)
            }
            agent_interactions.append(agent_interaction)
            
        return agent_interactions
    
    async def create_agent_knowledge_base(self) -> Dict[str, Any]:
        """Create a comprehensive knowledge base for the agent"""
        print("🔄 Creating agent knowledge base from BD data...")
        
        # Get all data
        contacts = await self.get_contacts_for_agent()
        interactions = await self.get_interactions_for_agent()
        
        # Get database statistics
        if not self.db_manager:
            stats = {"error": "Database not available"}
        else:
            stats = await self.db_manager.get_database_stats()
        
        knowledge_base = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_contacts": len(contacts),
                "total_interactions": len(interactions),
                "database_stats": stats
            },
            "contacts": contacts,
            "interactions": interactions,
            "business_intelligence": {
                "hot_leads": [c for c in contacts if c.get('lead_score', 0) >= 70],
                "follow_ups_needed": [c for c in contacts if c.get('last_interaction') and 
                                    (datetime.now() - datetime.fromisoformat(c['last_interaction'])).days > 3],
                "high_value_prospects": [c for c in contacts if c.get('estimated_value', 0) > 10000],
                "recent_opportunities": [i for i in interactions if i.get('opportunities')]
            }
        }
        
        # Save knowledge base
        knowledge_file = Path('agent_knowledge_base.json')
        with open(knowledge_file, 'w') as f:
            json.dump(knowledge_base, f, indent=2, default=str)
            
        print(f"✅ Knowledge base created: {knowledge_file}")
        print(f"   📊 {len(contacts)} contacts, {len(interactions)} interactions")
        
        return knowledge_base

def create_agent_config():
    """Create configuration for the BD analytics agent"""
    
    config = {
        "agent_name": "bd-analytics-agent",
        "description": "AI agent for business development analytics and intelligence",
        "template": "agentic_rag",
        "data_sources": {
            "local_database": "data/local_bd_database.db",
            "knowledge_base": "agent_knowledge_base.json",
            "google_sheets": "sync via existing system"
        },
        "capabilities": [
            "Contact analysis and lead scoring",
            "Interaction history analysis", 
            "Opportunity identification",
            "Follow-up recommendations",
            "Executive reporting",
            "Pipeline forecasting"
        ],
        "example_queries": [
            "Who are my hottest leads this week?",
            "What opportunities were discussed with [Company Name]?",
            "Which contacts need immediate follow-up?",
            "Generate a quarterly BD summary",
            "What's the total pipeline value for Q4?",
            "Show me contacts in the technology sector"
        ]
    }
    
    with open('bd_agent_config.json', 'w') as f:
        json.dump(config, f, indent=2)
        
    print("✅ Created bd_agent_config.json")
    return config

async def prepare_for_agent_migration():
    """Prepare the system for Google Cloud Agent integration"""
    
    print("🚀 Preparing BD Analytics for Google Cloud Agent Migration")
    print("="*60)
    
    # Create data bridge
    bridge = BDAgentDataBridge()
    await bridge.initialize()
    
    # Create knowledge base
    knowledge_base = await bridge.create_agent_knowledge_base()
    
    # Create agent configuration
    config = create_agent_config()
    
    # Create sample agent prompts
    prompts = {
        "system_prompt": """You are a BD Analytics AI agent with access to comprehensive business development data.
        
Your capabilities include:
- Analyzing contact and lead information
- Tracking interaction history and sentiment
- Identifying business opportunities
- Providing follow-up recommendations
- Generating executive reports

Always provide specific, actionable insights based on the data.""",
        
        "sample_queries": [
            "Analyze my lead pipeline and identify the top 5 opportunities",
            "Which contacts haven't been contacted in the last 30 days?",
            "What are the common topics in recent high-value conversations?",
            "Create a summary of BD activities for this month"
        ]
    }
    
    with open('bd_agent_prompts.json', 'w') as f:
        json.dump(prompts, f, indent=2)
    
    print("✅ Created bd_agent_prompts.json")
    
    # Create migration checklist
    checklist = {
        "pre_migration": [
            "✅ Local database operational with BD data",
            "✅ Knowledge base created from existing data", 
            "✅ Agent configuration prepared",
            "⏳ Google service account setup",
            "⏳ Google Cloud APIs enabled"
        ],
        "migration_steps": [
            "1. Create Google service account and download key",
            "2. Install agent-starter-pack",
            "3. Run: agent-starter-pack create bd-analytics-agent",
            "4. Choose 'agentic_rag' template",
            "5. Configure data integration",
            "6. Test locally with BD data",
            "7. Deploy to Cloud Run"
        ],
        "post_migration": [
            "Set up monitoring and alerts",
            "Configure auto-scaling",
            "Integrate with existing Google Sheets workflow",
            "Train team on agent interactions",
            "Set up automated reporting"
        ]
    }
    
    with open('migration_checklist.json', 'w') as f:
        json.dump(checklist, f, indent=2)
    
    print("✅ Created migration_checklist.json")
    
    print(f"\n🎉 Migration Preparation Complete!")
    print(f"   📊 Knowledge Base: {knowledge_base['metadata']['total_contacts']} contacts")
    print(f"   💬 Interactions: {knowledge_base['metadata']['total_interactions']} messages")
    print(f"   🔥 Hot Leads: {len(knowledge_base['business_intelligence']['hot_leads'])}")
    
    print(f"\n📋 Files Created:")
    print(f"   📄 agent_knowledge_base.json - Your BD data for the agent")
    print(f"   ⚙️ bd_agent_config.json - Agent configuration")
    print(f"   💭 bd_agent_prompts.json - Sample prompts and queries")
    print(f"   ✅ migration_checklist.json - Step-by-step migration guide")
    
    print(f"\n🚀 Ready for Agent Creation!")
    print(f"   Next: Create your Google service account, then run:")
    print(f"   → agent-starter-pack create bd-analytics-agent")

if __name__ == "__main__":
    asyncio.run(prepare_for_agent_migration()) 