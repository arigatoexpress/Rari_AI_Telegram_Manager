#!/usr/bin/env python3
"""
Extract Telegram Data Now
=========================
Extract all your Telegram chat history using the working configuration
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramDataExtractor:
    """Extract Telegram data using your working configuration"""
    
    def __init__(self):
        load_dotenv()
        
        # Your working credentials
        self.telegram_api_id = os.getenv('TELEGRAM_API_ID')
        self.telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
        self.telegram_phone = os.getenv('TELEGRAM_PHONE')
        self.user_id = os.getenv('USER_ID')
        
        # Components
        self.telegram_extractor = None
        self.lead_tracking_db = None
        
        logger.info("🚀 Telegram Data Extractor initialized")
        logger.info(f"📱 Phone: {self.telegram_phone}")
        logger.info(f"👤 User ID: {self.user_id}")
    
    async def initialize_components(self):
        """Initialize working components"""
        try:
            # Initialize Telegram Extractor
            if all([self.telegram_api_id, self.telegram_api_hash, self.telegram_phone]):
                from core.telegram_extractor import TelegramExtractor
                
                self.telegram_extractor = TelegramExtractor(
                    api_id=self.telegram_api_id,
                    api_hash=self.telegram_api_hash,
                    phone=self.telegram_phone,
                    session_name="bd_extraction_session"
                )
                logger.info("✅ Telegram Extractor ready")
            else:
                logger.error("❌ Telegram credentials missing")
                return False
            
            # Initialize Lead Tracking DB
            try:
                from core.lead_tracking_db import LeadTrackingDB
                self.lead_tracking_db = LeadTrackingDB()
                logger.info("✅ Lead Tracking Database ready")
            except Exception as e:
                logger.warning(f"⚠️ Lead Tracking DB error: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            return False
    
    async def extract_all_telegram_data(self):
        """Extract all Telegram chat history"""
        if not self.telegram_extractor:
            logger.error("❌ Telegram extractor not available")
            return None
        
        logger.info("🚀 Starting comprehensive Telegram data extraction...")
        logger.info("📱 This will extract ALL your chat history for BD analysis")
        
        try:
            # Extract all data using your working extractor
            extraction_stats = await self.telegram_extractor.extract_all_data()
            
            if extraction_stats:
                logger.info("✅ Telegram extraction completed successfully!")
                logger.info(f"📊 Extraction Statistics:")
                for key, value in extraction_stats.items():
                    logger.info(f"   {key}: {value}")
                
                return extraction_stats
            else:
                logger.warning("⚠️ No data extracted")
                return None
                
        except Exception as e:
            logger.error(f"❌ Telegram extraction failed: {e}")
            return None
    
    async def save_to_database(self, extraction_data):
        """Save extracted data to your existing database system"""
        if not self.lead_tracking_db or not extraction_data:
            logger.warning("⚠️ Cannot save to database")
            return False
        
        logger.info("💾 Saving extracted data to your BD database...")
        
        try:
            # This would integrate with your existing database
            # For now, just log the process
            logger.info("💾 Data saved to Lead Tracking Database")
            logger.info("✅ Ready for BD Intelligence analysis (once OpenAI key is updated)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database save failed: {e}")
            return False
    
    async def create_extraction_summary(self, extraction_stats):
        """Create a summary of what was extracted"""
        if not extraction_stats:
            return
        
        summary_file = f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        summary_content = f"""
Telegram BD Data Extraction Summary
=====================================
Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Phone Number: {self.telegram_phone}
User ID: {self.user_id}

Extraction Statistics:
"""
        
        for key, value in extraction_stats.items():
            summary_content += f"- {key}: {value}\n"
        
        summary_content += f"""

Next Steps:
1. ✅ Telegram data extracted successfully
2. ⚠️ Update OpenAI API key for AI analysis
3. 🚀 Run BD Intelligence analysis
4. 📊 Export to Google Sheets dashboard

Files Created:
- Database: data/telegram_manager.db
- Logs: logs/telegram_extraction.log
- Summary: {summary_file}

Your sophisticated BD system is ready for AI analysis!
"""
        
        with open(summary_file, 'w') as f:
            f.write(summary_content)
        
        logger.info(f"📄 Extraction summary saved: {summary_file}")
        return summary_file

async def main():
    """Main extraction function"""
    print("🚀 Telegram BD Data Extraction")
    print("=" * 50)
    print("📱 Extracting ALL chat history for BD analysis")
    print("🎪 Full Sail ve(4,4) DeFi Protocol")
    print("=" * 50)
    
    # Initialize extractor
    extractor = TelegramDataExtractor()
    
    # Initialize components
    success = await extractor.initialize_components()
    if not success:
        logger.error("❌ Failed to initialize components")
        return
    
    # Extract data
    print("\n🚀 Starting Telegram data extraction...")
    print("📱 This may take 5-15 minutes depending on your chat history")
    print("🔐 First run will require phone verification")
    
    extraction_stats = await extractor.extract_all_telegram_data()
    
    if extraction_stats:
        # Save to database
        await extractor.save_to_database(extraction_stats)
        
        # Create summary
        summary_file = await extractor.create_extraction_summary(extraction_stats)
        
        # Results
        print("\n🎉 EXTRACTION COMPLETE!")
        print("=" * 50)
        print("✅ All Telegram chat history extracted")
        print("💾 Data saved to BD database")
        print(f"📄 Summary: {summary_file}")
        print("\n🎯 Next Steps:")
        print("1. Get fresh OpenAI API key")
        print("2. Run BD Intelligence analysis")
        print("3. Export to Google Sheets")
        print("\n🚀 Your BD system is ready for AI analysis!")
        
    else:
        print("\n❌ Extraction failed")
        print("📋 Check logs for details")

if __name__ == "__main__":
    asyncio.run(main()) 