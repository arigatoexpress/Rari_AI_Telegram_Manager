#!/usr/bin/env python3
"""
Integrated BD Intelligence System
=================================
Comprehensive system that combines:
- Existing BD Intelligence (ChatGPT analysis)
- Existing Lead Tracking Database 
- Existing Google Sheets Integration
- NEW: Telegram chat history extraction
- Configure your Google service account for Sheets integration

This leverages ALL your existing sophisticated BD components!
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Import your existing BD components
from core.bd_intelligence import BDIntelligence, BDMessageGenerator
from core.lead_tracking_db import LeadTrackingDB
from core.ai_deal_analyzer import AIDealAnalyzer
from core.local_database_manager import LocalDatabaseManager, get_local_db_manager
from core.sheets_sync_manager import get_sheets_sync_manager
from core.real_google_sheets_exporter import RealGoogleSheetsExporter
from core.data_manager import DataManager
from core.async_data_manager import AsyncDataManager
from core.smart_cache import SmartCache
from core.batch_processor import BatchProcessor
from core.telegram_extractor import TelegramExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/integrated_bd_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedBDSystem:
    """
    Comprehensive BD Intelligence System integrating all existing components
    """
    
    def __init__(self):
        # Load environment
        load_dotenv()
        
        # Configuration
        self.service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'your_service_account@your_project.iam.gserviceaccount.com')
        self.telegram_api_id = os.getenv('TELEGRAM_API_ID')
        self.telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
        self.telegram_phone = os.getenv('TELEGRAM_PHONE')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        # Existing BD System Components
        self.bd_intelligence = None
        self.bd_message_generator = None
        self.lead_tracking_db = None
        self.ai_deal_analyzer = None
        self.local_db_manager = None
        self.sheets_sync_manager = None
        self.sheets_exporter = None
        self.data_manager = None
        self.async_data_manager = None
        self.smart_cache = None
        self.batch_processor = None
        
        # New Telegram Components
        self.telegram_extractor = None
        
        # System state
        self.initialized = False
        
        logger.info("🚀 Integrated BD System initialized with service account: %s", self.service_account_email)
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("🔧 Initializing Integrated BD System...")
            
            # Create directories
            self._setup_directories()
            
            # Initialize existing BD components
            await self._init_existing_bd_components()
            
            # Initialize new Telegram components
            await self._init_telegram_components()
            
            # Initialize Google Sheets integration
            await self._init_sheets_integration()
            
            self.initialized = True
            logger.info("✅ Integrated BD System fully initialized!")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            'data', 'logs', 'exports', 'cache', 'backups', 
            'sheets_exports', 'telegram_sessions'
        ]
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
            logger.info(f"📁 {dir_name}/ directory ready")
    
    async def _init_existing_bd_components(self):
        """Initialize your existing BD system components"""
        try:
            logger.info("🧠 Initializing existing BD Intelligence components...")
            
            # BD Intelligence (your existing ChatGPT analysis)
            if self.openai_api_key:
                self.lead_tracking_db = LeadTrackingDB()
                self.bd_intelligence = BDIntelligence(self.openai_api_key, self.lead_tracking_db)
                self.bd_message_generator = BDMessageGenerator(self.bd_intelligence)
                logger.info("✅ BD Intelligence System loaded")
            
            # AI Deal Analyzer (your existing deal analysis)
            self.ai_deal_analyzer = AIDealAnalyzer(self.openai_api_key)
            logger.info("✅ AI Deal Analyzer loaded")
            
            # Local Database Manager (your existing database system)
            self.local_db_manager = await get_local_db_manager()
            logger.info("✅ Local Database Manager loaded")
            
            # Data Manager (your existing data management)
            self.data_manager = DataManager()
            logger.info("✅ Data Manager loaded")
            
            # Async Data Manager (your high-performance system)
            self.async_data_manager = AsyncDataManager()
            await self.async_data_manager.initialize()
            logger.info("✅ Async Data Manager loaded")
            
            # Smart Cache (your caching system)
            self.smart_cache = SmartCache()
            logger.info("✅ Smart Cache loaded")
            
            # Batch Processor (your batch processing)
            self.batch_processor = BatchProcessor()
            logger.info("✅ Batch Processor loaded")
            
        except Exception as e:
            logger.error(f"❌ Error initializing existing BD components: {e}")
            raise
    
    async def _init_telegram_components(self):
        """Initialize new Telegram extraction components"""
        try:
            logger.info("📱 Initializing Telegram extraction components...")
            
            if not all([self.telegram_api_id, self.telegram_api_hash, self.telegram_phone]):
                logger.warning("⚠️ Telegram API credentials missing - extraction disabled")
                return
            
            self.telegram_extractor = TelegramExtractor(
                api_id=self.telegram_api_id,
                api_hash=self.telegram_api_hash,
                phone=self.telegram_phone,
                session_name="telegram_bd_session"
            )
            
            logger.info("✅ Telegram Extractor initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Telegram components initialization failed: {e}")
    
    async def _init_sheets_integration(self):
        """Initialize Google Sheets integration using existing components"""
        try:
            logger.info("📊 Initializing Google Sheets integration...")
            
            # Use your existing Google Sheets components
            self.sheets_sync_manager = await get_sheets_sync_manager()
            logger.info("✅ Sheets Sync Manager loaded")
            
            self.sheets_exporter = RealGoogleSheetsExporter()
            logger.info("✅ Real Google Sheets Exporter loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets integration failed: {e}")
    
    async def extract_telegram_data(self):
        """Extract all Telegram data using new extractor"""
        if not self.telegram_extractor:
            logger.warning("⚠️ Telegram extractor not available")
            return None
        
        logger.info("📥 Starting Telegram data extraction...")
        
        try:
            extraction_stats = await self.telegram_extractor.extract_all_data()
            logger.info(f"✅ Telegram extraction complete: {extraction_stats}")
            return extraction_stats
        except Exception as e:
            logger.error(f"❌ Telegram extraction failed: {e}")
            return None
    
    async def integrate_telegram_data_into_existing_system(self, telegram_data: Dict):
        """Integrate extracted Telegram data into your existing BD system"""
        if not telegram_data or not self.lead_tracking_db:
            return False
        
        logger.info("🔄 Integrating Telegram data into existing BD system...")
        
        try:
            integration_stats = {
                'contacts_added': 0,
                'messages_processed': 0,
                'opportunities_identified': 0,
                'leads_created': 0
            }
            
            # Process contacts using existing lead tracking system
            for contact_id, contact_data in telegram_data.get('contacts', {}).items():
                try:
                    # Use your existing contact creation logic
                    contact_result = self.lead_tracking_db.add_contact(
                        user_id=contact_data.get('user_id'),
                        first_name=contact_data.get('first_name', ''),
                        last_name=contact_data.get('last_name', ''),
                        username=contact_data.get('username', ''),
                        phone_number=contact_data.get('phone', ''),
                        contact_type='lead'  # Default to lead
                    )
                    
                    if contact_result:
                        integration_stats['contacts_added'] += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error adding contact {contact_id}: {e}")
            
            # Process messages using existing message processing
            for message in telegram_data.get('messages', []):
                try:
                    # Store message in your existing system
                    message_result = self.data_manager.store_message(
                        chat_id=message.get('chat_id'),
                        user_id=message.get('from_user_id'),
                        message_text=message.get('text', ''),
                        timestamp=message.get('date'),
                        message_type=message.get('message_type', 'text')
                    )
                    
                    if message_result:
                        integration_stats['messages_processed'] += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing message: {e}")
            
            logger.info(f"✅ Telegram data integration complete: {integration_stats}")
            return integration_stats
            
        except Exception as e:
            logger.error(f"❌ Telegram data integration failed: {e}")
            return False
    
    async def run_ai_analysis_on_integrated_data(self):
        """Run AI analysis using your existing BD Intelligence system"""
        if not self.bd_intelligence:
            logger.warning("⚠️ BD Intelligence not available")
            return {}
        
        logger.info("🧠 Running AI analysis on integrated data...")
        
        try:
            # Get all contacts from your existing system
            contacts = self.lead_tracking_db.get_all_contacts()
            analysis_results = {}
            
            for contact in contacts:
                try:
                    # Get messages for this contact
                    messages = self.data_manager.get_contact_messages(contact.user_id)
                    
                    if messages:
                        # Use your existing BD Intelligence analysis
                        contact_info = {
                            'first_name': contact.first_name,
                            'last_name': contact.last_name,
                            'username': contact.username,
                            'organization_name': getattr(contact, 'organization_name', '')
                        }
                        
                        insight = await self.bd_intelligence.analyze_conversation(
                            messages=messages,
                            contact_info=contact_info
                        )
                        
                        if insight:
                            analysis_results[contact.user_id] = insight
                            
                            # Update lead score in your existing system
                            if insight.interest_level > 70:
                                self.lead_tracking_db.update_contact_lead_score(
                                    contact.contact_id, 
                                    insight.interest_level
                                )
                
                except Exception as e:
                    logger.warning(f"⚠️ Error analyzing contact {contact.user_id}: {e}")
            
            logger.info(f"✅ AI analysis complete for {len(analysis_results)} contacts")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return {}
    
    async def export_to_google_sheets(self):
        """Export using your existing Google Sheets system"""
        if not self.sheets_exporter:
            logger.warning("⚠️ Google Sheets exporter not available")
            return False
        
        logger.info("📊 Exporting to Google Sheets using existing system...")
        
        try:
            # Use your existing sheets export functionality
            export_result = await self.sheets_exporter.create_comprehensive_dashboard(
                service_account_email=self.service_account_email,
                google_sheet_id=self.google_sheet_id
            )
            
            logger.info(f"✅ Google Sheets export complete: {export_result}")
            return export_result
            
        except Exception as e:
            logger.error(f"❌ Google Sheets export failed: {e}")
            return False
    
    async def run_comprehensive_bd_pipeline(self):
        """Run the complete integrated BD pipeline"""
        logger.info("🚀 Starting comprehensive BD intelligence pipeline...")
        
        pipeline_results = {
            'telegram_extraction': None,
            'data_integration': None,
            'ai_analysis': {},
            'sheets_export': False,
            'pipeline_success': False
        }
        
        try:
            # Step 1: Extract Telegram data (NEW)
            logger.info("Step 1: Extracting Telegram data...")
            telegram_data = await self.extract_telegram_data()
            pipeline_results['telegram_extraction'] = telegram_data
            
            # Step 2: Integrate into existing BD system
            if telegram_data:
                logger.info("Step 2: Integrating data into existing BD system...")
                integration_stats = await self.integrate_telegram_data_into_existing_system(telegram_data)
                pipeline_results['data_integration'] = integration_stats
            
            # Step 3: Run AI analysis using existing BD Intelligence
            logger.info("Step 3: Running AI analysis with existing BD Intelligence...")
            ai_results = await self.run_ai_analysis_on_integrated_data()
            pipeline_results['ai_analysis'] = ai_results
            
            # Step 4: Export to Google Sheets using existing system
            logger.info("Step 4: Exporting to Google Sheets...")
            sheets_result = await self.export_to_google_sheets()
            pipeline_results['sheets_export'] = sheets_result
            
            pipeline_results['pipeline_success'] = True
            logger.info("🎉 Comprehensive BD pipeline completed successfully!")
            
            return pipeline_results
            
        except Exception as e:
            logger.error(f"❌ BD pipeline failed: {e}")
            pipeline_results['error'] = str(e)
            return pipeline_results
    
    async def get_bd_dashboard_summary(self):
        """Get comprehensive BD dashboard using existing components"""
        try:
            summary = {
                'system_status': 'operational' if self.initialized else 'not_initialized',
                'components_loaded': {
                    'bd_intelligence': bool(self.bd_intelligence),
                    'lead_tracking_db': bool(self.lead_tracking_db),
                    'ai_deal_analyzer': bool(self.ai_deal_analyzer),
                    'local_db_manager': bool(self.local_db_manager),
                    'sheets_integration': bool(self.sheets_exporter),
                    'telegram_extractor': bool(self.telegram_extractor)
                },
                'service_account': self.service_account_email,
                'database_stats': {},
                'recent_activity': {}
            }
            
            # Get stats from existing systems
            if self.lead_tracking_db:
                summary['database_stats'] = self.lead_tracking_db.get_database_stats()
            
            if self.local_db_manager:
                health_status = await self.local_db_manager.get_health_status()
                summary['local_db_health'] = health_status
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting dashboard summary: {e}")
            return {'error': str(e)}

async def main():
    """Main function"""
    print("🚀 Integrated BD Intelligence System")
    print("=" * 70)
    print("📱 NEW: Telegram chat history extraction")
    print("🧠 EXISTING: BD Intelligence (ChatGPT analysis)")
    print("🗄️ EXISTING: Lead Tracking Database (CRM)")
    print("📊 EXISTING: Google Sheets Integration")
    print("🤖 EXISTING: AI Deal Analyzer")
    print("⚡ EXISTING: Async Data Manager & Smart Cache")
    service_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'your_service_account@your_project.iam.gserviceaccount.com')
    print(f"📧 Service Account: {service_email}")
    print("=" * 70)
    
    # Initialize system
    bd_system = IntegratedBDSystem()
    
    success = await bd_system.initialize()
    if not success:
        logger.error("❌ System initialization failed")
        return
    
    # Get dashboard summary
    dashboard = await bd_system.get_bd_dashboard_summary()
    print("\n📊 System Status:")
    print(f"✅ BD Intelligence: {dashboard['components_loaded']['bd_intelligence']}")
    print(f"✅ Lead Tracking: {dashboard['components_loaded']['lead_tracking_db']}")
    print(f"✅ AI Deal Analyzer: {dashboard['components_loaded']['ai_deal_analyzer']}")
    print(f"✅ Local Database: {dashboard['components_loaded']['local_db_manager']}")
    print(f"✅ Sheets Integration: {dashboard['components_loaded']['sheets_integration']}")
    print(f"✅ Telegram Extractor: {dashboard['components_loaded']['telegram_extractor']}")
    
    # Run comprehensive pipeline
    print("\n🚀 Running comprehensive BD pipeline...")
    results = await bd_system.run_comprehensive_bd_pipeline()
    
    # Display results
    print("\n📈 Pipeline Results:")
    print(f"✅ Telegram Extraction: {bool(results['telegram_extraction'])}")
    print(f"✅ Data Integration: {bool(results['data_integration'])}")
    print(f"✅ AI Analysis: {len(results['ai_analysis'])} contacts analyzed")
    print(f"✅ Google Sheets Export: {results['sheets_export']}")
    print(f"🎯 Pipeline Success: {results['pipeline_success']}")

if __name__ == "__main__":
    asyncio.run(main()) 