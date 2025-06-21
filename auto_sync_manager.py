#!/usr/bin/env python3
"""
Automated Sync Manager for Telegram Manager Bot
===============================================
Handles automatic background sync and real-time data integration.
"""

import os
import time
import threading
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from chat_history_manager import ChatHistoryManager
from google_sheets_database import initialize_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoSyncManager:
    """Manages automatic sync and data integration"""
    
    def __init__(self):
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.user_id = os.getenv('USER_ID')
        self.chat_manager = ChatHistoryManager()
        self.db = initialize_database()
        self.sync_interval = 3600  # 1 hour
        self.last_sync = None
        self.sync_thread = None
        self.running = False
        
    def start_background_sync(self):
        """Start background sync thread"""
        if self.sync_thread and self.sync_thread.is_alive():
            logger.info("Background sync already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._background_sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("✅ Background sync started")
    
    def stop_background_sync(self):
        """Stop background sync"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("🛑 Background sync stopped")
    
    def _background_sync_loop(self):
        """Background sync loop"""
        while self.running:
            try:
                self._perform_sync()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Error in background sync: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _perform_sync(self):
        """Perform a sync operation"""
        try:
            logger.info("🔄 Starting background sync...")
            
            # Check if we have credentials
            if not all([self.api_id, self.api_hash, self.user_id]):
                logger.warning("Missing Telegram credentials for sync")
                return
            
            # Fetch recent messages (simplified approach)
            result = self.chat_manager.fetch_full_chat_history(
                api_id=str(self.api_id),
                api_hash=str(self.api_hash),
                phone=str(self.user_id),
                limit=100  # Smaller limit for background sync
            )
            
            if result.get('messages'):
                # Store in database
                success = self.chat_manager.store_encrypted_history(result)
                if success:
                    self.last_sync = datetime.now()
                    logger.info(f"✅ Background sync completed: {len(result['messages'])} messages")
                else:
                    logger.error("❌ Failed to store messages in background sync")
            else:
                logger.info("📝 No new messages to sync")
                
        except Exception as e:
            logger.error(f"❌ Background sync error: {e}")
    
    def get_recent_messages(self, limit=50):
        """Get recent messages from database"""
        try:
            return self.chat_manager.get_encrypted_history(limit=limit)
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    def get_sync_status(self):
        """Get sync status information"""
        return {
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'running': self.running,
            'sync_interval': self.sync_interval,
            'total_messages': len(self.get_recent_messages(limit=10000))
        }
    
    def force_sync(self):
        """Force an immediate sync"""
        logger.info("🔄 Force sync requested...")
        self._perform_sync()
        return self.get_sync_status()

# Global sync manager instance
sync_manager = None

def get_sync_manager():
    """Get the global sync manager instance"""
    global sync_manager
    if sync_manager is None:
        sync_manager = AutoSyncManager()
    return sync_manager

def start_auto_sync():
    """Start automatic sync"""
    manager = get_sync_manager()
    manager.start_background_sync()
    return manager

def stop_auto_sync():
    """Stop automatic sync"""
    global sync_manager
    if sync_manager:
        sync_manager.stop_background_sync()

def get_recent_messages(limit=50):
    """Get recent messages (wrapper for bot)"""
    manager = get_sync_manager()
    return manager.get_recent_messages(limit)

def get_sync_status():
    """Get sync status (wrapper for bot)"""
    manager = get_sync_manager()
    return manager.get_sync_status()

def force_sync():
    """Force sync (wrapper for bot)"""
    manager = get_sync_manager()
    return manager.force_sync()

if __name__ == "__main__":
    """Test the auto sync manager"""
    print("🔄 Testing Auto Sync Manager...")
    
    manager = AutoSyncManager()
    
    # Test sync status
    status = manager.get_sync_status()
    print(f"📊 Sync Status: {status}")
    
    # Test getting messages
    messages = manager.get_recent_messages(limit=10)
    print(f"📝 Found {len(messages)} messages in database")
    
    # Test force sync
    print("🔄 Testing force sync...")
    result = manager.force_sync()
    print(f"✅ Force sync result: {result}")
    
    print("🎉 Auto Sync Manager test complete!") 