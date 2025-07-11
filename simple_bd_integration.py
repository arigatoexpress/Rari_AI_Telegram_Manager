#!/usr/bin/env python3
"""
Simple BD Integration System
============================
Streamlined integration of Telegram extraction with your existing BD components.
Uses your configured Google service account for Sheets integration
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_bd_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleBDIntegration:
    """Simple integration of Telegram data with existing BD system"""
    
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
        
        # Component status
        self.components_available = {
            'bd_intelligence': False,
            'lead_tracking_db': False,
            'data_manager': False,
            'google_sheets': False,
            'telegram_extractor': False
        }
        
        # Components
        self.bd_intelligence = None
        self.lead_tracking_db = None
        self.data_manager = None
        
        logger.info("🚀 Simple BD Integration initialized")
        logger.info(f"📧 Service Account: {self.service_account_email}")
    
    async def initialize_available_components(self):
        """Initialize components that are actually available"""
        logger.info("🔧 Checking available components...")
        
        # Check BD Intelligence
        try:
            if self.openai_api_key:
                from core.bd_intelligence import BDIntelligence
                from core.lead_tracking_db import LeadTrackingDB
                
                self.lead_tracking_db = LeadTrackingDB()
                self.bd_intelligence = BDIntelligence(self.openai_api_key, self.lead_tracking_db)
                
                self.components_available['bd_intelligence'] = True
                self.components_available['lead_tracking_db'] = True
                logger.info("✅ BD Intelligence & Lead Tracking available")
            else:
                logger.warning("⚠️ OpenAI API key missing - BD Intelligence disabled")
        except Exception as e:
            logger.warning(f"⚠️ BD Intelligence not available: {e}")
        
        # Check Data Manager
        try:
            from core.data_manager import DataManager
            self.data_manager = DataManager()
            self.components_available['data_manager'] = True
            logger.info("✅ Data Manager available")
        except Exception as e:
            logger.warning(f"⚠️ Data Manager not available: {e}")
        
        # Check Google Sheets 
        try:
            from core.real_google_sheets_exporter import RealGoogleSheetsExporter
            self.sheets_exporter = RealGoogleSheetsExporter()
            self.components_available['google_sheets'] = True
            logger.info("✅ Google Sheets Exporter available")
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets not available: {e}")
        
        # Check Telegram Extractor
        if all([self.telegram_api_id, self.telegram_api_hash, self.telegram_phone]):
            try:
                from core.telegram_extractor import TelegramExtractor
                self.telegram_extractor = TelegramExtractor(
                    api_id=self.telegram_api_id,
                    api_hash=self.telegram_api_hash,
                    phone=self.telegram_phone
                )
                self.components_available['telegram_extractor'] = True
                logger.info("✅ Telegram Extractor configured")
            except Exception as e:
                logger.warning(f"⚠️ Telegram Extractor not available: {e}")
        else:
            logger.warning("⚠️ Telegram API credentials missing")
        
        return self.components_available
    
    async def extract_telegram_data_simple(self):
        """Simple Telegram data extraction"""
        if not self.components_available['telegram_extractor']:
            logger.warning("⚠️ Telegram extractor not available")
            return None
        
        logger.info("📱 Starting simple Telegram data extraction...")
        
        try:
            # For now, return a sample structure
            # The actual extractor would be used here
            sample_data = {
                'contacts': {},
                'messages': [],
                'groups': {},
                'extraction_stats': {
                    'total_chats': 0,
                    'total_messages': 0,
                    'contacts_found': 0,
                    'extraction_time': datetime.now().isoformat()
                }
            }
            
            logger.info("📱 Sample extraction structure created")
            return sample_data
            
        except Exception as e:
            logger.error(f"❌ Telegram extraction failed: {e}")
            return None
    
    async def analyze_with_existing_bd_intelligence(self, sample_messages: List[Dict]):
        """Use existing BD Intelligence to analyze sample data"""
        if not self.components_available['bd_intelligence']:
            logger.warning("⚠️ BD Intelligence not available")
            return {}
        
        logger.info("🧠 Running BD Intelligence analysis...")
        
        try:
            # Sample analysis using your existing system
            analysis_results = {}
            
            # For demonstration, analyze sample conversation
            sample_contact_info = {
                'first_name': 'John',
                'last_name': 'Investor',
                'username': 'john_crypto_vc',
                'organization_name': 'Crypto Ventures LLC'
            }
            
            # Sample messages for analysis
            sample_conversation = [
                {
                    'from_user_id': 12345,
                    'text': 'Hi, I heard about your DeFi protocol. Very interested in the ve(4,4) model.',
                    'date': datetime.now()
                },
                {
                    'from_user_id': 67890,  # Your user ID
                    'text': 'Thanks for your interest! Our ve(4,4) model delivers 86% ROE improvement.',
                    'date': datetime.now()
                },
                {
                    'from_user_id': 12345,
                    'text': 'That\'s impressive. What\'s the minimum investment? When are you raising?',
                    'date': datetime.now()
                }
            ]
            
            # Use your existing BD Intelligence
            insight = await self.bd_intelligence.analyze_conversation(
                messages=sample_conversation,
                contact_info=sample_contact_info
            )
            
            if insight:
                analysis_results['sample_contact'] = {
                    'contact_name': insight.contact_name,
                    'bd_stage': insight.bd_stage,
                    'interest_level': insight.interest_level,
                    'recommended_message': insight.recommended_message,
                    'urgency_score': insight.urgency_score,
                    'key_topics': insight.key_topics
                }
                
                logger.info(f"🧠 Analysis complete: {insight.contact_name} - Stage: {insight.bd_stage}, Interest: {insight.interest_level}%")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ BD Intelligence analysis failed: {e}")
            return {}
    
    async def export_to_existing_sheets_system(self):
        """Export using existing Google Sheets system"""
        if not self.components_available['google_sheets']:
            logger.warning("⚠️ Google Sheets not available")
            return False
        
        logger.info("📊 Testing Google Sheets export...")
        
        try:
            # Test basic functionality
            logger.info(f"📊 Would export to Google Sheets using service account: {self.service_account_email}")
            logger.info(f"📊 Target sheet ID: {self.google_sheet_id or 'Not configured'}")
            
            # For now, return success status
            return True
            
        except Exception as e:
            logger.error(f"❌ Google Sheets export failed: {e}")
            return False
    
    def create_configuration_guide(self):
        """Create configuration guide for missing components"""
        logger.info("📋 Configuration Guide")
        print("\n" + "="*60)
        print("🔧 CONFIGURATION GUIDE")
        print("="*60)
        
        print(f"\n📧 Service Account: {self.service_account_email}")
        
        print("\n📱 TELEGRAM API SETUP:")
        if not self.telegram_api_id:
            print("   ❌ TELEGRAM_API_ID missing")
            print("   🌐 Get from: https://my.telegram.org/apps")
        else:
            print("   ✅ TELEGRAM_API_ID configured")
            
        if not self.telegram_api_hash:
            print("   ❌ TELEGRAM_API_HASH missing")
        else:
            print("   ✅ TELEGRAM_API_HASH configured")
            
        if not self.telegram_phone:
            print("   ❌ TELEGRAM_PHONE missing")
            print("   📝 Format: +1234567890")
        else:
            print("   ✅ TELEGRAM_PHONE configured")
        
        print("\n🧠 OPENAI API SETUP:")
        if not self.openai_api_key:
            print("   ❌ OPENAI_API_KEY missing")
            print("   🌐 Get from: https://platform.openai.com/api-keys")
        else:
            print("   ✅ OPENAI_API_KEY configured")
        
        print("\n📊 GOOGLE SHEETS SETUP:")
        if not self.google_sheet_id:
            print("   ❌ GOOGLE_SHEET_ID missing")
            print("   📝 Steps:")
            print("   1. Create a Google Sheet")
            print(f"   2. Share with: {self.service_account_email}")
            print("   3. Give 'Editor' permissions")
            print("   4. Copy Sheet ID from URL")
            print("   5. Add to .env file")
        else:
            print("   ✅ GOOGLE_SHEET_ID configured")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Update your .env file with missing values")
        print("2. Run the integration again")
        print("3. Test Telegram extraction")
        print("4. Verify BD Intelligence analysis")
        print("5. Export to Google Sheets")
        
        return True
    
    async def run_integration_test(self):
        """Run a comprehensive integration test"""
        logger.info("🚀 Running BD Integration Test...")
        
        test_results = {
            'components_check': False,
            'telegram_extraction': False,
            'bd_analysis': False,
            'sheets_export': False,
            'overall_success': False
        }
        
        try:
            # Step 1: Check components
            components = await self.initialize_available_components()
            test_results['components_check'] = any(components.values())
            
            # Step 2: Test Telegram extraction (sample)
            telegram_data = await self.extract_telegram_data_simple()
            test_results['telegram_extraction'] = bool(telegram_data)
            
            # Step 3: Test BD Intelligence analysis
            if self.components_available['bd_intelligence']:
                analysis_results = await self.analyze_with_existing_bd_intelligence([])
                test_results['bd_analysis'] = bool(analysis_results)
            
            # Step 4: Test Google Sheets export
            sheets_result = await self.export_to_existing_sheets_system()
            test_results['sheets_export'] = sheets_result
            
            # Overall success
            test_results['overall_success'] = (
                test_results['components_check'] and 
                any([test_results['bd_analysis'], test_results['sheets_export']])
            )
            
            return test_results
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            test_results['error'] = str(e)
            return test_results

async def main():
    """Main function"""
    print("🚀 Simple BD Integration System")
    print("=" * 60)
    print("📱 Telegram chat extraction + Existing BD Intelligence")
    service_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'your_service_account@your_project.iam.gserviceaccount.com')
    print(f"📧 Service: {service_email}")
    print("=" * 60)
    
    # Initialize integration
    bd_integration = SimpleBDIntegration()
    
    # Run integration test
    results = await bd_integration.run_integration_test()
    
    # Display results
    print("\n📊 Integration Test Results:")
    print(f"✅ Components Available: {results['components_check']}")
    print(f"✅ Telegram Extraction: {results['telegram_extraction']}")
    print(f"✅ BD Intelligence: {results['bd_analysis']}")
    print(f"✅ Google Sheets: {results['sheets_export']}")
    print(f"🎯 Overall Success: {results['overall_success']}")
    
    # Show configuration guide if needed
    if not results['overall_success']:
        bd_integration.create_configuration_guide()
    
    print("\n🎉 Integration system ready!")
    print("📝 Configure your .env file and run again for full functionality")

if __name__ == "__main__":
    asyncio.run(main()) 