#!/usr/bin/env python3
"""
Unified Telegram Business Development Bot
Combines message syncing, AI analysis, and business development features
"""

import os
import sys
import asyncio
import logging
import signal
import fcntl
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Core libraries
import nest_asyncio
from dotenv import load_dotenv

# Telegram libraries
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telethon for message syncing
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import our core modules
from core.data_manager import DataManager
from core.bd_analyzer import BusinessDevelopmentAnalyzer

# Apply nest_asyncio for Jupyter/async compatibility
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """Bot configuration from environment variables"""
    bot_token: str
    api_id: int
    api_hash: str
    phone: str
    user_id: int
    authorized_users: List[int]
    openai_api_key: str
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Load configuration from environment variables"""
        authorized_users_str = os.getenv('AUTHORIZED_USERS', str(os.getenv('USER_ID', '')))
        authorized_users = [int(uid.strip()) for uid in authorized_users_str.split(',') if uid.strip().isdigit()]
        
        return cls(
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            api_id=int(os.getenv('TELEGRAM_API_ID', '0')),
            api_hash=os.getenv('TELEGRAM_API_HASH', ''),
            phone=os.getenv('TELEGRAM_PHONE', ''),
            user_id=int(os.getenv('USER_ID', '0')),
            authorized_users=authorized_users,
            openai_api_key=os.getenv('OPENAI_API_KEY', '')
        )

class BotInstanceManager:
    """Manages bot instance locking to prevent multiple instances"""
    
    def __init__(self, lock_file: str = 'bot.lock'):
        self.lock_file = lock_file
        self.lock_fd = None
        self.pid = os.getpid()
    
    def acquire_lock(self) -> bool:
        """Acquire exclusive lock"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(self.pid))
            self.lock_fd.flush()
            logger.info(f"🔒 Bot instance lock acquired (PID: {self.pid})")
            return True
        except (IOError, OSError) as e:
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            logger.error(f"❌ Could not acquire lock: {e}")
            return False
    
    def release_lock(self):
        """Release the lock"""
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
                os.remove(self.lock_file)
                logger.info("🔓 Bot instance lock released")
            except Exception as e:
                logger.error(f"❌ Error releasing lock: {e}")
            finally:
                self.lock_fd = None

class UnifiedTelegramBot:
    """Unified Telegram Bot with all functionalities"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.application = None
        self.telethon_client = None
        self.data_manager = None
        self.bd_analyzer = None
        self.scheduler = None
        self.instance_manager = BotInstanceManager()
        self.is_running = False
        self.last_sync_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}")
        logger.info("🛑 Stopping Unified Telegram Bot...")
        self.instance_manager.release_lock()
        asyncio.create_task(self.stop_bot())
    
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize data manager
            self.data_manager = DataManager()
            logger.info("✅ Data Manager initialized")
            
            # Initialize BD analyzer
            self.bd_analyzer = BusinessDevelopmentAnalyzer(self.config.openai_api_key)
            logger.info("✅ Business Development Analyzer initialized")
            
            # Initialize Telethon client
            self.telethon_client = TelegramClient(
                'sync_session',
                self.config.api_id,
                self.config.api_hash
            )
            await self.telethon_client.start(phone=self.config.phone)
            logger.info("✅ Telethon client initialized")
            
            # Initialize Telegram bot
            self.application = Application.builder().token(self.config.bot_token).build()
            
            # Add command handlers
            self._setup_handlers()
            logger.info("✅ Command handlers set up")
            
            # Initialize scheduler
            self.scheduler = AsyncIOScheduler()
            self.scheduler.add_job(
                self._auto_sync,
                IntervalTrigger(minutes=30),
                id='auto_sync',
                name='Auto Sync Messages'
            )
            logger.info("✅ Scheduler initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing bot: {e}")
            return False
    
    def _setup_handlers(self):
        """Setup all command handlers"""
        handlers = [
            # Basic commands
            CommandHandler("start", self._start_command),
            CommandHandler("help", self._help_command),
            CommandHandler("status", self._status_command),
            
            # Sync commands
            CommandHandler("sync", self._sync_command),
            CommandHandler("chats", self._chats_command),
            
            # Analysis commands
            CommandHandler("analyze", self._analyze_command),
            CommandHandler("analyze_all", self._analyze_all_command),
            CommandHandler("briefing", self._briefing_command),
            CommandHandler("contacts", self._contacts_command),
            CommandHandler("followups", self._followups_command),
            CommandHandler("opportunities", self._opportunities_command),
            CommandHandler("rate", self._rate_command),
            
            # Message handler for logging
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler)
        ]
        
        for handler in handlers:
            self.application.add_handler(handler)
    
    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id in self.config.authorized_users
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        welcome_msg = """
🚀 **Unified Telegram Business Development Bot**

This bot combines message syncing, AI analysis, and business development features.

**Available Commands:**
• `/help` - Show all commands
• `/status` - Bot status and statistics
• `/sync` - Sync messages from all chats
• `/analyze` - Analyze recent messages
• `/briefing` - Get daily BD briefing
• `/contacts` - View contact ratings
• `/opportunities` - Show hot leads

Type `/help` for detailed command descriptions.
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        help_msg = """
📚 **Command Reference**

**📊 Status & Info:**
• `/status` - Bot status, sync info, and statistics
• `/chats` - List all synced chats with message counts

**🔄 Message Syncing:**
• `/sync` - Manually sync messages from all chats
• Auto-sync runs every 30 minutes

**🤖 AI Analysis:**
• `/analyze [days]` - Analyze recent messages (default: 7 days)
• `/analyze_all` - Comprehensive analysis of all chats

**💼 Business Development:**
• `/briefing` - Daily BD briefing with key insights
• `/contacts` - Contact ratings and engagement analysis
• `/followups` - Personalized follow-up recommendations
• `/opportunities` - Hot leads and investment opportunities
• `/rate` - Top-rated contacts and potential

**🎯 Features:**
✅ Automatic message syncing from all your Telegram chats
✅ AI-powered business development analysis
✅ Contact rating and engagement tracking
✅ Investment opportunity identification
✅ Personalized follow-up recommendations
✅ Daily briefings with actionable insights
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            # Get database stats
            stats = self.data_manager.get_stats()
            
            # Get sync info
            sync_status = "🟢 Ready" if self.telethon_client.is_connected() else "🔴 Disconnected"
            last_sync = self.last_sync_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_sync_time else "Never"
            
            status_msg = f"""
📊 **Bot Status**

**🔄 Sync Status:** {sync_status}
**⏰ Last Sync:** {last_sync}
**🤖 Scheduler:** {'🟢 Running' if self.scheduler.running else '🔴 Stopped'}

**📈 Database Statistics:**
• **Messages:** {stats.get('total_messages', 0):,}
• **Chats:** {stats.get('total_chats', 0):,}
• **Contacts:** {stats.get('total_contacts', 0):,}
• **Notes:** {stats.get('total_notes', 0):,}

**💾 Storage:**
• **Database Size:** {stats.get('db_size_mb', 0):.1f} MB
• **Uptime:** {self._get_uptime()}
            """
            
            await update.message.reply_text(status_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(f"❌ Error getting status: {str(e)}")
    
    async def _sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sync command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        await update.message.reply_text("🔄 Starting message sync...")
        
        try:
            result = await self._sync_messages()
            await update.message.reply_text(f"✅ Sync complete!\n{result}")
        except Exception as e:
            logger.error(f"Error in sync command: {e}")
            await update.message.reply_text(f"❌ Sync failed: {str(e)}")
    
    async def _chats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chats command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            chats = self.data_manager.get_chat_list()
            
            if not chats:
                await update.message.reply_text("📭 No chats synced yet. Use /sync to sync messages.")
                return
            
            chat_list = "📱 **Synced Chats:**\n\n"
            for chat in chats[:20]:  # Show top 20 chats
                chat_list += f"• **{chat['title']}** ({chat['message_count']} messages)\n"
            
            if len(chats) > 20:
                chat_list += f"\n... and {len(chats) - 20} more chats"
            
            await update.message.reply_text(chat_list, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in chats command: {e}")
            await update.message.reply_text(f"❌ Error getting chats: {str(e)}")
    
    async def _analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            # Get days parameter
            days = 7
            if context.args and context.args[0].isdigit():
                days = int(context.args[0])
            
            await update.message.reply_text(f"🤖 Analyzing messages from the last {days} days...")
            
            # Get recent messages
            messages = self.data_manager.get_recent_messages(days=days)
            
            if not messages:
                await update.message.reply_text("📭 No messages found for analysis.")
                return
            
            # Analyze with BD analyzer
            analysis = await self.bd_analyzer.analyze_messages(messages)
            
            # Format response
            response = f"""
🤖 **Message Analysis ({days} days)**

**📊 Summary:**
• **Messages Analyzed:** {len(messages)}
• **Key Insights:** {analysis.get('key_insights', 'None')}
• **Sentiment:** {analysis.get('overall_sentiment', 'Neutral')}

**🎯 Recommendations:**
{analysis.get('recommendations', 'No specific recommendations')}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await update.message.reply_text(f"❌ Analysis failed: {str(e)}")
    
    async def _analyze_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze_all command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        await update.message.reply_text("🤖 Performing comprehensive analysis of all chats...")
        
        try:
            analysis = await self.bd_analyzer.analyze_all_chats(self.data_manager)
            
            response = f"""
🤖 **Comprehensive Chat Analysis**

**📊 Overview:**
• **Total Chats:** {analysis.get('total_chats', 0)}
• **Hot Leads:** {analysis.get('hot_leads', 0)}
• **Investment Potential:** {analysis.get('avg_investment_score', 0):.1f}/10

**🔥 Top Opportunities:**
{analysis.get('top_opportunities', 'None identified')}

**📈 Key Insights:**
{analysis.get('key_insights', 'No specific insights')}

**🎯 Next Actions:**
{analysis.get('recommendations', 'No specific recommendations')}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analyze_all command: {e}")
            await update.message.reply_text(f"❌ Comprehensive analysis failed: {str(e)}")
    
    async def _briefing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /briefing command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        await update.message.reply_text("📋 Generating daily business development briefing...")
        
        try:
            briefing = await self.bd_analyzer.generate_daily_briefing(self.data_manager)
            
            response = f"""
📋 **Daily BD Briefing - {datetime.now().strftime('%Y-%m-%d')}**

**🎯 Priority Actions:**
{briefing.get('priority_actions', 'No priority actions identified')}

**🔥 Hot Leads:**
{briefing.get('hot_leads', 'No hot leads identified')}

**📊 Key Metrics:**
{briefing.get('key_metrics', 'No metrics available')}

**💡 Opportunities:**
{briefing.get('opportunities', 'No opportunities identified')}

**⚠️ Action Items:**
{briefing.get('action_items', 'No action items')}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in briefing command: {e}")
            await update.message.reply_text(f"❌ Briefing generation failed: {str(e)}")
    
    async def _contacts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /contacts command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            contacts = await self.bd_analyzer.get_contact_ratings(self.data_manager)
            
            if not contacts:
                await update.message.reply_text("📭 No contacts found for rating.")
                return
            
            response = "👥 **Contact Ratings:**\n\n"
            for contact in contacts[:10]:  # Show top 10
                rating = contact.get('rating', 'N/A')
                engagement = contact.get('engagement_level', 'Unknown')
                response += f"• **{contact['name']}** - {rating}/10 ({engagement})\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in contacts command: {e}")
            await update.message.reply_text(f"❌ Error getting contacts: {str(e)}")
    
    async def _followups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /followups command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        await update.message.reply_text("📝 Generating personalized follow-up recommendations...")
        
        try:
            followups = await self.bd_analyzer.generate_followup_recommendations(self.data_manager)
            
            response = f"""
📝 **Follow-up Recommendations**

**🎯 High Priority:**
{followups.get('high_priority', 'No high priority follow-ups')}

**📋 Standard Follow-ups:**
{followups.get('standard', 'No standard follow-ups')}

**💡 Suggested Messages:**
{followups.get('suggested_messages', 'No message suggestions')}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in followups command: {e}")
            await update.message.reply_text(f"❌ Follow-up generation failed: {str(e)}")
    
    async def _opportunities_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /opportunities command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            opportunities = await self.bd_analyzer.identify_opportunities(self.data_manager)
            
            response = f"""
🔥 **Hot Opportunities**

**💰 Investment Leads:**
{opportunities.get('investment_leads', 'No investment leads identified')}

**🤝 Partnership Opportunities:**
{opportunities.get('partnerships', 'No partnership opportunities')}

**👥 Community Leads:**
{opportunities.get('community_leads', 'No community leads')}

**📊 Scoring:**
{opportunities.get('scoring_summary', 'No scoring available')}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in opportunities command: {e}")
            await update.message.reply_text(f"❌ Opportunities analysis failed: {str(e)}")
    
    async def _rate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rate command"""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return
        
        try:
            ratings = await self.bd_analyzer.get_top_rated_contacts(self.data_manager)
            
            response = f"""
⭐ **Top Rated Contacts**

**🥇 Gold Tier (9-10/10):**
{ratings.get('gold_tier', 'None')}

**🥈 Silver Tier (7-8/10):**
{ratings.get('silver_tier', 'None')}

**🥉 Bronze Tier (5-6/10):**
{ratings.get('bronze_tier', 'None')}

**📊 Rating Criteria:**
• Investment potential
• Engagement level
• Response rate
• Network value
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in rate command: {e}")
            await update.message.reply_text(f"❌ Rating analysis failed: {str(e)}")
    
    async def _message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages for logging"""
        try:
            # Store message in database
            message_data = {
                'chat_id': update.effective_chat.id,
                'message_id': update.message.message_id,
                'user_id': update.effective_user.id,
                'text': update.message.text,
                'timestamp': update.message.date,
                'chat_title': update.effective_chat.title or f"Chat {update.effective_chat.id}",
                'username': update.effective_user.username or update.effective_user.first_name
            }
            
            self.data_manager.store_message(message_data)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _sync_messages(self) -> str:
        """Sync messages from all chats"""
        try:
            if not self.telethon_client.is_connected():
                await self.telethon_client.connect()
            
            synced_count = 0
            chat_count = 0
            
            # Get all dialogs (chats)
            async for dialog in self.telethon_client.iter_dialogs():
                chat_count += 1
                
                # Get last message timestamp from database
                last_timestamp = self.data_manager.get_last_message_timestamp(dialog.id)
                
                # Sync messages newer than last timestamp
                async for message in self.telethon_client.iter_messages(dialog, reverse=True):
                    if last_timestamp and message.date <= last_timestamp:
                        break
                    
                    if message.text:
                        message_data = {
                            'chat_id': dialog.id,
                            'message_id': message.id,
                            'user_id': message.sender_id or 0,
                            'text': message.text,
                            'timestamp': message.date,
                            'chat_title': dialog.title or f"Chat {dialog.id}",
                            'username': getattr(message.sender, 'username', '') or getattr(message.sender, 'first_name', '') or 'Unknown'
                        }
                        
                        self.data_manager.store_message(message_data)
                        synced_count += 1
                
                # Limit to prevent timeout
                if chat_count >= 50:
                    break
            
            self.last_sync_time = datetime.now()
            return f"📊 Synced {synced_count} messages from {chat_count} chats"
            
        except Exception as e:
            logger.error(f"Error syncing messages: {e}")
            raise
    
    async def _auto_sync(self):
        """Automatic sync job"""
        try:
            logger.info("🔄 Starting automatic sync...")
            result = await self._sync_messages()
            logger.info(f"✅ Auto sync complete: {result}")
        except Exception as e:
            logger.error(f"❌ Auto sync failed: {e}")
    
    def _get_uptime(self) -> str:
        """Get bot uptime"""
        if hasattr(self, 'start_time'):
            uptime = datetime.now() - self.start_time
            return str(uptime).split('.')[0]
        return "Unknown"
    
    async def start_bot(self) -> bool:
        """Start the unified bot"""
        try:
            # Acquire instance lock
            if not self.instance_manager.acquire_lock():
                logger.error("❌ Another bot instance is already running")
                return False
            
            # Initialize components
            if not await self.initialize():
                self.instance_manager.release_lock()
                return False
            
            # Start application
            await self.application.initialize()
            await self.application.start()
            
            # Start scheduler
            self.scheduler.start()
            
            # Start polling
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("🚀 Unified Telegram Bot started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            self.instance_manager.release_lock()
            return False
    
    async def stop_bot(self):
        """Stop the unified bot"""
        try:
            if self.is_running:
                # Stop scheduler
                if self.scheduler and self.scheduler.running:
                    self.scheduler.shutdown()
                
                # Stop application
                if self.application:
                    await self.application.updater.stop()
                    await self.application.stop()
                    await self.application.shutdown()
                
                # Disconnect Telethon
                if self.telethon_client:
                    await self.telethon_client.disconnect()
                
                self.is_running = False
                logger.info("✅ Unified Telegram Bot stopped")
            
            # Release lock
            self.instance_manager.release_lock()
            
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")

async def main():
    """Main function"""
    try:
        # Load configuration
        config = BotConfig.from_env()
        
        # Validate configuration
        if not all([config.bot_token, config.api_id, config.api_hash, config.openai_api_key]):
            logger.error("❌ Missing required environment variables")
            sys.exit(1)
        
        # Create and start bot
        bot = UnifiedTelegramBot(config)
        logger.info("🚀 Unified Telegram Bot initialized")
        
        if await bot.start_bot():
            try:
                # Keep running
                while bot.is_running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Received keyboard interrupt")
        
        await bot.stop_bot()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 