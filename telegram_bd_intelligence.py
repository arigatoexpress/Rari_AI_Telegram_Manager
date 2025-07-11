#!/usr/bin/env python3
"""
Telegram BD Intelligence System
===============================
A comprehensive system to extract, organize, and analyze Telegram chat history
for business development intelligence and deal flow optimization.

Core Functions:
1. Extract all Telegram chat history (groups + individual)
2. Store in secure local database organized by contact/lead
3. Export to Google Sheets with readable BD-focused formatting
4. AI analysis for actionable insights and message recommendations
5. BD automation for conversion, engagement, and deal closing

Author: Telegram BD Intelligence System with Google Sheets integration
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_bd_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TelegramContact:
    """Represents a contact/lead from Telegram"""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    is_verified: bool
    is_premium: bool
    last_seen: Optional[datetime]
    
    # BD specific fields
    lead_score: int = 0
    deal_stage: str = "prospect"
    total_messages: int = 0
    last_interaction: Optional[datetime] = None
    notes: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def full_name(self) -> str:
        """Get full name of contact"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) or self.username or f"User_{self.user_id}"
    
    @property
    def display_name(self) -> str:
        """Get display name for UI"""
        if self.username:
            return f"{self.full_name} (@{self.username})"
        return self.full_name

@dataclass
class TelegramChat:
    """Represents a chat (group or individual)"""
    chat_id: int
    chat_type: str  # 'private', 'group', 'supergroup', 'channel'
    title: Optional[str]
    username: Optional[str]
    description: Optional[str]
    member_count: int = 0
    is_verified: bool = False
    is_business_related: bool = False
    
    # BD analysis
    opportunity_score: int = 0
    last_activity: Optional[datetime] = None
    key_topics: List[str] = None
    
    def __post_init__(self):
        if self.key_topics is None:
            self.key_topics = []

@dataclass
class TelegramMessage:
    """Represents a message with BD context"""
    message_id: int
    chat_id: int
    from_user_id: Optional[int]
    date: datetime
    text: Optional[str]
    message_type: str  # 'text', 'photo', 'document', etc.
    
    # BD analysis fields
    sentiment_score: float = 0.0
    interest_level: int = 0
    contains_business_keywords: bool = False
    is_question: bool = False
    is_follow_up_needed: bool = False
    ai_summary: Optional[str] = None

class TelegramBDIntelligence:
    """Main Telegram BD Intelligence System"""
    
    def __init__(self):
        self.session_name = "telegram_bd_session"
        self.api_id = None
        self.api_hash = None
        self.phone = None
        
        # Google Sheets configuration
        self.service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'your_service_account@your_project.iam.gserviceaccount.com')
        self.google_sheet_id = None
        
        # Components
        self.db_manager = None
        self.sheets_manager = None
        self.ai_analyzer = None
        
        # Data
        self.contacts: Dict[int, TelegramContact] = {}
        self.chats: Dict[int, TelegramChat] = {}
        self.messages: List[TelegramMessage] = []
        
        logger.info("🚀 Telegram BD Intelligence System initialized")
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("🔧 Initializing Telegram BD Intelligence System...")
            
            # Create directories
            self._setup_directories()
            
            # Initialize database
            await self._init_database()
            
            # Initialize Google Sheets
            await self._init_google_sheets()
            
            # Initialize AI analyzer
            await self._init_ai_analyzer()
            
            logger.info("✅ Telegram BD Intelligence System ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            'data',
            'logs', 
            'exports',
            'cache',
            'backups',
            'sheets_exports'
        ]
        
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
            logger.info(f"📁 {dir_name}/ directory ready")
    
    async def _init_database(self):
        """Initialize local database system"""
        try:
            from core.telegram_bd_database import TelegramBDDatabase
            self.db_manager = TelegramBDDatabase()
            await self.db_manager.initialize()
            logger.info("✅ Database manager initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def _init_google_sheets(self):
        """Initialize Google Sheets integration"""
        try:
            from core.bd_sheets_manager import BDSheetsManager
            self.sheets_manager = BDSheetsManager(
                service_account_email=self.service_account_email
            )
            await self.sheets_manager.initialize()
            logger.info("✅ Google Sheets manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets initialization failed: {e}")
            self.sheets_manager = None
    
    async def _init_ai_analyzer(self):
        """Initialize AI analysis engine"""
        try:
            from core.telegram_ai_analyzer import TelegramAIAnalyzer
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.ai_analyzer = TelegramAIAnalyzer(openai_key)
                logger.info("✅ AI analyzer initialized")
            else:
                logger.warning("⚠️ No OpenAI API key - AI features disabled")
                self.ai_analyzer = None
        except Exception as e:
            logger.warning(f"⚠️ AI analyzer initialization failed: {e}")
            self.ai_analyzer = None
    
    async def extract_telegram_data(self):
        """Extract all Telegram chat history"""
        logger.info("📥 Starting Telegram data extraction...")
        
        try:
            # This will use Telethon to extract data
            from core.telegram_extractor import TelegramExtractor
            
            extractor = TelegramExtractor(
                api_id=self.api_id,
                api_hash=self.api_hash,
                phone=self.phone,
                session_name=self.session_name
            )
            
            # Extract all data
            extraction_stats = await extractor.extract_all_data()
            
            logger.info(f"✅ Extraction complete: {extraction_stats}")
            return extraction_stats
            
        except Exception as e:
            logger.error(f"❌ Data extraction failed: {e}")
            return None
    
    async def organize_contacts(self):
        """Organize all data by contact/lead"""
        logger.info("📊 Organizing contacts and chat history...")
        
        try:
            # Load data from database
            contacts = await self.db_manager.get_all_contacts()
            
            # Organize by contact
            organized_data = {}
            for contact in contacts:
                contact_data = {
                    'contact_info': contact,
                    'chat_history': await self.db_manager.get_contact_messages(contact.user_id),
                    'groups': await self.db_manager.get_contact_groups(contact.user_id),
                    'bd_metrics': await self._calculate_bd_metrics(contact.user_id)
                }
                organized_data[contact.user_id] = contact_data
            
            logger.info(f"✅ Organized {len(organized_data)} contacts")
            return organized_data
            
        except Exception as e:
            logger.error(f"❌ Contact organization failed: {e}")
            return {}
    
    async def _calculate_bd_metrics(self, contact_id: int) -> Dict[str, Any]:
        """Calculate BD metrics for a contact"""
        try:
            messages = await self.db_manager.get_contact_messages(contact_id)
            
            metrics = {
                'total_messages': len(messages),
                'response_rate': 0.0,
                'avg_response_time': 0.0,
                'sentiment_trend': [],
                'engagement_score': 0,
                'last_interaction': None,
                'follow_up_needed': False
            }
            
            if messages:
                metrics['last_interaction'] = max(msg.date for msg in messages)
                
                # Calculate response patterns
                my_messages = [msg for msg in messages if msg.from_user_id == contact_id]
                their_messages = [msg for msg in messages if msg.from_user_id != contact_id]
                
                if their_messages:
                    metrics['response_rate'] = len(my_messages) / len(their_messages)
                
                # Check if follow-up needed (3+ days since last interaction)
                if metrics['last_interaction']:
                    days_since = (datetime.now() - metrics['last_interaction']).days
                    metrics['follow_up_needed'] = days_since >= 3
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ BD metrics calculation failed: {e}")
            return {}
    
    async def export_to_sheets(self, organized_data: Dict):
        """Export organized data to Google Sheets"""
        if not self.sheets_manager:
            logger.warning("⚠️ Google Sheets manager not available")
            return False
        
        logger.info("📊 Exporting to Google Sheets...")
        
        try:
            # Create comprehensive BD dashboard
            export_result = await self.sheets_manager.create_bd_dashboard(
                contacts_data=organized_data,
                service_account_email=self.service_account_email
            )
            
            logger.info(f"✅ Export complete: {export_result}")
            return export_result
            
        except Exception as e:
            logger.error(f"❌ Google Sheets export failed: {e}")
            return False
    
    async def analyze_with_ai(self, organized_data: Dict):
        """Run AI analysis on organized data"""
        if not self.ai_analyzer:
            logger.warning("⚠️ AI analyzer not available")
            return {}
        
        logger.info("🧠 Running AI analysis...")
        
        try:
            analysis_results = {}
            
            for contact_id, contact_data in organized_data.items():
                contact_analysis = await self.ai_analyzer.analyze_contact(
                    contact_info=contact_data['contact_info'],
                    chat_history=contact_data['chat_history'],
                    bd_metrics=contact_data['bd_metrics']
                )
                
                analysis_results[contact_id] = contact_analysis
            
            logger.info(f"✅ AI analysis complete for {len(analysis_results)} contacts")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return {}
    
    async def generate_bd_insights(self, analysis_results: Dict):
        """Generate actionable BD insights and recommendations"""
        logger.info("💡 Generating BD insights...")
        
        try:
            insights = {
                'hot_leads': [],
                'follow_up_needed': [],
                'recommended_messages': {},
                'deal_opportunities': [],
                'engagement_strategies': {}
            }
            
            for contact_id, analysis in analysis_results.items():
                # Identify hot leads
                if analysis.get('lead_score', 0) > 70:
                    insights['hot_leads'].append({
                        'contact_id': contact_id,
                        'score': analysis['lead_score'],
                        'reasons': analysis.get('hot_lead_reasons', [])
                    })
                
                # Check follow-up needs
                if analysis.get('follow_up_needed', False):
                    insights['follow_up_needed'].append({
                        'contact_id': contact_id,
                        'days_since_contact': analysis.get('days_since_contact', 0),
                        'suggested_approach': analysis.get('follow_up_strategy', '')
                    })
                
                # Generate recommended messages
                if analysis.get('recommended_message'):
                    insights['recommended_messages'][contact_id] = {
                        'message': analysis['recommended_message'],
                        'reasoning': analysis.get('message_reasoning', ''),
                        'best_time': analysis.get('best_contact_time', 'anytime')
                    }
            
            logger.info(f"✅ Generated insights for {len(analysis_results)} contacts")
            return insights
            
        except Exception as e:
            logger.error(f"❌ BD insights generation failed: {e}")
            return {}
    
    async def run_full_analysis(self):
        """Run the complete BD intelligence pipeline"""
        logger.info("🚀 Starting full BD intelligence analysis...")
        
        results = {
            'extraction_stats': None,
            'organized_data': {},
            'ai_analysis': {},
            'bd_insights': {},
            'sheets_export': False
        }
        
        try:
            # Step 1: Extract Telegram data
            logger.info("Step 1: Extracting Telegram data...")
            results['extraction_stats'] = await self.extract_telegram_data()
            
            # Step 2: Organize by contact
            logger.info("Step 2: Organizing contacts...")
            results['organized_data'] = await self.organize_contacts()
            
            # Step 3: AI analysis
            logger.info("Step 3: AI analysis...")
            results['ai_analysis'] = await self.analyze_with_ai(results['organized_data'])
            
            # Step 4: Generate BD insights
            logger.info("Step 4: Generating BD insights...")
            results['bd_insights'] = await self.generate_bd_insights(results['ai_analysis'])
            
            # Step 5: Export to Google Sheets
            logger.info("Step 5: Exporting to Google Sheets...")
            results['sheets_export'] = await self.export_to_sheets(results['organized_data'])
            
            logger.info("🎉 Full BD intelligence analysis complete!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Full analysis failed: {e}")
            return results

async def main():
    """Main function"""
    print("🚀 Telegram BD Intelligence System")
    print("=" * 50)
    print("📱 Extract all Telegram chat history")
    print("🗄️ Organize by contact/lead in secure database") 
    print("📊 Export to Google Sheets with BD formatting")
    print("🧠 AI analysis for actionable insights")
    print("🎯 BD automation for deal closing")
    print("=" * 50)
    
    # Initialize system
    bd_system = TelegramBDIntelligence()
    
    success = await bd_system.initialize()
    if not success:
        logger.error("❌ System initialization failed")
        return
    
    # Run full analysis
    results = await bd_system.run_full_analysis()
    
    # Display results summary
    print("\n📊 Analysis Results:")
    print(f"✅ Extraction: {results['extraction_stats']}")
    print(f"✅ Contacts organized: {len(results['organized_data'])}")
    print(f"✅ AI analysis: {len(results['ai_analysis'])} contacts")
    print(f"✅ BD insights generated: {bool(results['bd_insights'])}")
    print(f"✅ Google Sheets export: {results['sheets_export']}")

if __name__ == "__main__":
    asyncio.run(main()) 