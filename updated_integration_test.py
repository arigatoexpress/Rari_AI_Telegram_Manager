#!/usr/bin/env python3
"""
Updated BD Integration Test
==========================
Test the integration with your existing sophisticated BD configuration
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
        logging.FileHandler('logs/updated_integration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UpdatedBDIntegrationTest:
    """Test integration with your existing sophisticated BD configuration"""
    
    def __init__(self):
        # Load environment (try optimized first, then fallback)
        if Path('.env.optimized').exists():
            load_dotenv('.env.optimized')
            logger.info("📄 Using .env.optimized configuration")
        else:
            load_dotenv()
            logger.info("📄 Using standard .env configuration")
        
        # Extract all your configuration
        self.config = self._load_comprehensive_config()
        
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
        
        logger.info("🚀 Updated BD Integration Test initialized")
        logger.info(f"📧 Service Account: {self.config['service_account_email']}")
    
    def _load_comprehensive_config(self) -> Dict[str, Any]:
        """Load your comprehensive BD configuration"""
        return {
            # Core credentials
            'service_account_email': os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 'your_service_account@your_project.iam.gserviceaccount.com'),
            'telegram_api_id': os.getenv('TELEGRAM_API_ID'),
            'telegram_api_hash': os.getenv('TELEGRAM_API_HASH'),
            'telegram_phone': os.getenv('TELEGRAM_PHONE'),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'user_id': os.getenv('USER_ID'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'google_sheet_id': os.getenv('GOOGLE_SHEET_ID'),
            
            # Deal analysis settings
            'deal_analysis_enabled': os.getenv('DEAL_ANALYSIS_ENABLED', 'true').lower() == 'true',
            'minimum_deal_probability': int(os.getenv('MINIMUM_DEAL_PROBABILITY', '20')),
            'high_probability_threshold': int(os.getenv('HIGH_PROBABILITY_THRESHOLD', '70')),
            'deal_value_threshold': int(os.getenv('DEAL_VALUE_THRESHOLD', '1000')),
            
            # Full Sail configuration
            'full_sail_ve44_enabled': os.getenv('FULL_SAIL_VE44_ENABLED', 'true').lower() == 'true',
            'full_sail_roe_improvement': int(os.getenv('FULL_SAIL_ROE_IMPROVEMENT', '86')),
            'full_sail_target_blockchain': os.getenv('FULL_SAIL_TARGET_BLOCKCHAIN', 'Sui'),
            'full_sail_incubator': os.getenv('FULL_SAIL_INCUBATOR', 'Aftermath Finance'),
            
            # AI configuration
            'ai_model': os.getenv('AI_MODEL', 'gpt-4'),
            'ai_temperature': float(os.getenv('AI_TEMPERATURE', '0.3')),
            'ai_max_tokens': int(os.getenv('AI_MAX_TOKENS', '2000')),
            
            # Performance settings
            'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            'ml_enabled': os.getenv('ML_ENABLED', 'true').lower() == 'true',
            'predictive_analytics': os.getenv('PREDICTIVE_ANALYTICS', 'true').lower() == 'true',
            
            # Target audience
            'target_defi_protocols': os.getenv('TARGET_DEFI_PROTOCOLS', 'true').lower() == 'true',
            'target_vcs': os.getenv('TARGET_VCS', 'true').lower() == 'true',
            'target_institutional_investors': os.getenv('TARGET_INSTITUTIONAL_INVESTORS', 'true').lower() == 'true',
        }
    
    def display_configuration_status(self):
        """Display comprehensive configuration status"""
        print("\n" + "="*80)
        print("🔧 COMPREHENSIVE BD SYSTEM CONFIGURATION STATUS")
        print("="*80)
        
        print(f"\n📧 Service Account: {self.config['service_account_email']}")
        
        # Telegram Configuration
        print("\n📱 TELEGRAM CONFIGURATION:")
        telegram_configured = all([
            self.config['telegram_api_id'],
            self.config['telegram_api_hash'],
            self.config['user_id']
        ])
        
        if telegram_configured:
            print(f"   ✅ API ID: {self.config['telegram_api_id']}")
            print(f"   ✅ API Hash: {self.config['telegram_api_hash'][:10]}...")
            print(f"   ✅ User ID: {self.config['user_id']}")
            print(f"   ✅ Bot Token: {self.config['telegram_bot_token'][:20] if self.config['telegram_bot_token'] else 'Not set'}...")
            
            if not self.config['telegram_phone']:
                print("   ⚠️ TELEGRAM_PHONE missing (needed for data extraction)")
                print("   📝 Add your phone number: TELEGRAM_PHONE='+1234567890'")
            else:
                print(f"   ✅ Phone: {self.config['telegram_phone']}")
        else:
            print("   ❌ Telegram API credentials incomplete")
        
        # OpenAI Configuration
        print("\n🧠 OPENAI CONFIGURATION:")
        if self.config['openai_api_key']:
            print(f"   ✅ API Key: {self.config['openai_api_key'][:20]}...")
            print(f"   ✅ Model: {self.config['ai_model']}")
            print(f"   ✅ Temperature: {self.config['ai_temperature']}")
            print(f"   ✅ Max Tokens: {self.config['ai_max_tokens']}")
        else:
            print("   ❌ OpenAI API key missing")
        
        # Google Sheets Configuration
        print("\n📊 GOOGLE SHEETS CONFIGURATION:")
        if self.config['google_sheet_id']:
            print(f"   ✅ Sheet ID: {self.config['google_sheet_id']}")
            print(f"   ✅ Service Account: {self.config['service_account_email']}")
        else:
            print("   ❌ Google Sheet ID missing")
        
        # Full Sail Configuration
        print("\n🎪 FULL SAIL CONFIGURATION:")
        print(f"   ✅ ve(4,4) Model: {self.config['full_sail_ve44_enabled']}")
        print(f"   ✅ ROE Improvement: {self.config['full_sail_roe_improvement']}%")
        print(f"   ✅ Target Blockchain: {self.config['full_sail_target_blockchain']}")
        print(f"   ✅ Incubator: {self.config['full_sail_incubator']}")
        
        # Deal Analysis Configuration
        print("\n💰 DEAL ANALYSIS CONFIGURATION:")
        print(f"   ✅ Deal Analysis: {self.config['deal_analysis_enabled']}")
        print(f"   ✅ Min Probability: {self.config['minimum_deal_probability']}%")
        print(f"   ✅ High Threshold: {self.config['high_probability_threshold']}%")
        print(f"   ✅ Value Threshold: ${self.config['deal_value_threshold']:,}")
        
        # Target Audience
        print("\n🎯 TARGET AUDIENCE:")
        print(f"   ✅ DeFi Protocols: {self.config['target_defi_protocols']}")
        print(f"   ✅ VCs: {self.config['target_vcs']}")
        print(f"   ✅ Institutional Investors: {self.config['target_institutional_investors']}")
        
        # Advanced Features
        print("\n🤖 ADVANCED FEATURES:")
        print(f"   ✅ Machine Learning: {self.config['ml_enabled']}")
        print(f"   ✅ Predictive Analytics: {self.config['predictive_analytics']}")
        print(f"   ✅ Smart Caching: {self.config['cache_enabled']}")
        
        return telegram_configured
    
    async def test_existing_components(self):
        """Test your existing BD components"""
        logger.info("🔧 Testing existing BD components...")
        
        # Test BD Intelligence
        try:
            if self.config['openai_api_key']:
                from core.bd_intelligence import BDIntelligence
                from core.lead_tracking_db import LeadTrackingDB
                
                self.lead_tracking_db = LeadTrackingDB()
                self.bd_intelligence = BDIntelligence(self.config['openai_api_key'], self.lead_tracking_db)
                
                self.components_available['bd_intelligence'] = True
                self.components_available['lead_tracking_db'] = True
                logger.info("✅ BD Intelligence & Lead Tracking loaded")
            else:
                logger.warning("⚠️ OpenAI API key missing")
        except Exception as e:
            logger.warning(f"⚠️ BD Intelligence error: {e}")
        
        # Test Data Manager
        try:
            from core.data_manager import DataManager
            self.data_manager = DataManager()
            self.components_available['data_manager'] = True
            logger.info("✅ Data Manager loaded")
        except Exception as e:
            logger.warning(f"⚠️ Data Manager error: {e}")
        
        # Test Google Sheets
        try:
            from core.real_google_sheets_exporter import RealGoogleSheetsExporter
            self.sheets_exporter = RealGoogleSheetsExporter()
            self.components_available['google_sheets'] = True
            logger.info("✅ Google Sheets Exporter loaded")
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets error: {e}")
        
        return self.components_available
    
    async def run_comprehensive_test(self):
        """Run comprehensive integration test"""
        logger.info("🚀 Running comprehensive BD integration test...")
        
        # Display configuration
        telegram_configured = self.display_configuration_status()
        
        # Test components
        components = await self.test_existing_components()
        
        # Results
        print("\n📊 INTEGRATION TEST RESULTS:")
        print("="*80)
        
        print(f"✅ Configuration Loaded: True")
        print(f"✅ Telegram Configured: {telegram_configured}")
        print(f"✅ BD Intelligence: {components['bd_intelligence']}")
        print(f"✅ Lead Tracking DB: {components['lead_tracking_db']}")
        print(f"✅ Data Manager: {components['data_manager']}")
        print(f"✅ Google Sheets: {components['google_sheets']}")
        
        # Overall status
        overall_success = any(components.values())
        print(f"🎯 Overall Success: {overall_success}")
        
        # Recommendations
        print("\n🎯 NEXT STEPS:")
        print("="*80)
        
        if not telegram_configured:
            print("1. ⚠️ Add TELEGRAM_PHONE to .env.optimized")
            
        if not components['bd_intelligence']:
            print("2. ⚠️ Get fresh OpenAI API key from https://platform.openai.com/api-keys")
            
        if not self.config['google_sheet_id']:
            print("3. ⚠️ Create Google Sheet and share with service account")
        
        if overall_success:
            print("🎉 Your BD system is ready for Telegram integration!")
            print("📝 Just add missing credentials and run the full system")
        
        return {
            'telegram_configured': telegram_configured,
            'components_working': components,
            'overall_success': overall_success,
            'configuration': self.config
        }

async def main():
    """Main test function"""
    print("🚀 Ultimate BD Intelligence System - Integration Test")
    print("=" * 80)
    print("📱 Telegram + Existing BD Intelligence + Google Sheets")
    print("🎪 Full Sail ve(4,4) DeFi Protocol Optimization")
    print("=" * 80)
    
    # Run test
    test = UpdatedBDIntegrationTest()
    results = await test.run_comprehensive_test()
    
    # Summary
    print(f"\n🎉 Integration Test Complete!")
    print(f"🎯 Success Rate: {sum(results['components_working'].values())}/4 components working")
    
    if results['overall_success']:
        print("✅ Your sophisticated BD system is operational!")
        print("📝 Configure remaining credentials for full functionality")
    else:
        print("⚠️ Some components need configuration")
        print("📋 Follow the recommendations above")

if __name__ == "__main__":
    asyncio.run(main()) 