#!/usr/bin/env python3
"""
Telegram Manager Bot - Optimized Version
=======================================
A high-performance, consolidated Telegram bot with advanced data handling,
AI-powered analysis, and robust sync capabilities.
"""

import os
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Telegram Bot imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Core components
from core.data_manager import DataManager
from core.ai_analyzer import AIAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedTelegramBot:
    """Optimized Telegram bot with advanced features"""
    
    def __init__(self):
        # Load configuration
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.authorized_users = self._load_authorized_users()
        
        # Telegram API credentials for reading chats
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        
        # Initialize core components
        self.data_manager = DataManager()
        self.ai_analyzer = AIAnalyzer(self.data_manager)
        
        # Performance optimization
        self.message_queue = asyncio.Queue(maxsize=1000)
        self.processing_tasks = set()
        self.stats = {
            'messages_processed': 0,
            'notes_created': 0,
            'analyses_performed': 0,
            'chats_synced': 0,
            'contacts_updated': 0,
            'outreach_blurbs_created': 0,
            'start_time': datetime.now()
        }
        
        # Chat reading and CRM features
        self.telethon_client = None
        self.chat_reading_enabled = False
        self.auto_sync_enabled = True
        self.crm_features = {
            'contact_tracking': True,
            'lead_scoring': True,
            'conversation_analytics': True,
            'business_insights': True
        }
        
        # Initialize bot
        self.application = None
        self._init_bot()
        
        logger.info("✅ Optimized Telegram Bot initialized successfully")
    
    def _load_authorized_users(self) -> List[int]:
        """Load authorized users from environment or config"""
        # Check for AUTHORIZED_USERS first (new format)
        users_str = os.getenv('AUTHORIZED_USERS', '')
        if users_str:
            return [int(uid.strip()) for uid in users_str.split(',') if uid.strip().isdigit()]
        
        # Fallback to USER_ID (old format)
        user_id = os.getenv('USER_ID')
        if user_id and user_id.isdigit():
            return [int(user_id)]
        
        return []
    
    def _init_bot(self):
        """Initialize Telegram bot application"""
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.application = Application.builder().token(self.bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("note", self.note_command))
        self.application.add_handler(CommandHandler("notes", self.notes_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("dailybrief", self.dailybrief_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("sync", self.sync_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("sheets", self.sheets_command))
        
        # New CRM and chat reading commands
        self.application.add_handler(CommandHandler("read_chats", self.read_chats_command))
        self.application.add_handler(CommandHandler("contacts", self.contacts_command))
        self.application.add_handler(CommandHandler("leads", self.leads_command))
        self.application.add_handler(CommandHandler("crm", self.crm_command))
        self.application.add_handler(CommandHandler("auto_sync", self.auto_sync_command))
        self.application.add_handler(CommandHandler("insights", self.insights_command))
        
        # Outreach and follow-up commands
        self.application.add_handler(CommandHandler("outreach", self.outreach_command))
        self.application.add_handler(CommandHandler("blurbs", self.blurbs_command))
        self.application.add_handler(CommandHandler("followup", self.followup_command))
        
        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("✅ Bot handlers configured")
    
    def _is_authorized_user(self, update: Update) -> bool:
        """Check if user is authorized (TEMP: allow all users for debugging)"""
        # DEBUG: Allow all users for now
        return True  # <-- REMOVE THIS LINE AFTER DEBUGGING
        # Uncomment below for normal behavior
        # if not self.authorized_users:
        #     return True  # Allow all users if no restrictions set
        # user_id = update.effective_user.id
        # return user_id in self.authorized_users
    
    async def _safe_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
        """Safely reply to user with error handling"""
        try:
            if update.message:
                await update.message.reply_text(text, **kwargs)
            elif update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(text, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error sending reply: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /start command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /start command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        welcome_text = """
🤖 **Telegram Manager Bot - Optimized Version**

**Available Commands:**
• `/note <text>` - Create a note
• `/notes [category]` - View notes
• `/analyze [chat_id]` - Analyze chat data
• `/status` - Check system status
• `/sync` - Check sync status
• `/stats` - View bot statistics
• `/help` - Show this help

**Features:**
✅ Advanced data handling with duplicate prevention
✅ AI-powered sentiment analysis and insights
✅ Automatic Google Sheets synchronization
✅ Business intelligence and recommendations
✅ High-performance message processing

Bot is ready to process messages and provide insights!
        """
        
        await self._safe_reply(update, context, welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        print(f"[DEBUG] /help command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /help command from user {getattr(update.effective_user, 'id', None)}")
        
        help_text = """
🤖 **Telegram Manager Bot - Enhanced CRM Version**

**📚 Chat Management:**
• `/read_chats` - Read and sync all Telegram chats
• `/auto_sync` - Toggle automatic chat synchronization

**📇 Contact Management:**
• `/contacts` - View and manage contacts
• `/leads` - View business leads and opportunities
• `/crm` - CRM dashboard and statistics

**📊 Analysis & Insights:**
• `/analyze [chat_id]` - Analyze specific chat data
• `/insights` - Generate business insights from conversations
• `/dailybrief` - Daily summary and business brief
• `/stats` - View bot performance statistics

**🎯 Outreach & Follow-up:**
• `/outreach` - Generate outreach blurbs for all contacts
• `/blurbs` - View existing outreach blurbs
• `/followup` - Get follow-up recommendations

**📝 Note Management:**
• `/note <text>` - Create a note
• `/notes [category]` - View notes by category

**🔧 System Commands:**
• `/status` - Check system status
• `/sync` - Check Google Sheets sync status
• `/sheets` - Get Google Sheets link
• `/help` - Show this help message

**🚀 Features:**
✅ Advanced chat reading and synchronization
✅ AI-powered sentiment analysis and insights
✅ Contact management and lead scoring
✅ Business intelligence and recommendations
✅ Automatic Google Sheets integration
✅ High-performance message processing
✅ CRM dashboard and analytics

**💡 Quick Start:**
1. Use `/read_chats` to sync your Telegram chats
2. View contacts with `/contacts`
3. Check leads with `/leads`
4. Get insights with `/insights` or `/dailybrief`
5. Monitor with `/crm` dashboard

Bot is ready to transform your Telegram into a powerful CRM! 🎯
"""
        
        await self._safe_reply(update, context, help_text, parse_mode='Markdown')
    
    async def sheets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sheets command - Return Google Sheets link"""
        print(f"[DEBUG] /sheets command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /sheets command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        
        if not spreadsheet_id:
            await self._safe_reply(update, context, 
                "❌ Google Sheets not configured.\n"
                "Please set GOOGLE_SHEETS_SPREADSHEET_ID in your .env file.")
            return
        
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        response = "📊 **Google Sheets Integration**\n\n"
        response += f"🔗 **Spreadsheet Link:**\n{sheets_url}\n\n"
        response += "**Worksheets:**\n"
        response += "• **Messages** - All synced messages\n"
        response += "• **Contacts** - Contact information and lead scores\n"
        response += "• **Notes** - Your notes and reminders\n"
        response += "• **Analyses** - AI analysis results\n\n"
        response += "💡 **Tip:** Use `/sync` to check sync status"
        
        await self._safe_reply(update, context, response, parse_mode='Markdown')
    
    async def note_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /note command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /note command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        if not context.args:
            await self._safe_reply(update, context, "❌ Please provide note text. Usage: `/note <text>`", parse_mode='Markdown')
            return
        
        note_text = " ".join(context.args)
        
        # Extract category and tags
        category = "general"
        tags = []
        
        # Check for category prefix (e.g., #meeting, #task)
        if "#" in note_text:
            parts = note_text.split("#")
            note_text = parts[0].strip()
            tags = [tag.strip() for tag in parts[1:] if tag.strip()]
            if tags:
                category = tags[0]  # Use first tag as category
        
        # Add note
        success, message = await self.data_manager.add_note(note_text, category, "medium", tags)
        
        if success:
            self.stats['notes_created'] += 1
            await self._safe_reply(update, context, f"✅ {message}")
        else:
            await self._safe_reply(update, context, f"❌ Failed to create note: {message}")
    
    async def notes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /notes command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /notes command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        category = context.args[0] if context.args else None
        notes = await self.data_manager.get_notes(category, limit=10)
        
        if not notes:
            category_text = f" in category '{category}'" if category else ""
            await self._safe_reply(update, context, f"📝 No notes found{category_text}")
            return
        
        response = f"📝 **Recent Notes"
        if category:
            response += f" - {category}"
        response += ":**\n\n"
        
        for note in notes:
            timestamp = note.get('timestamp', 'Unknown')
            text = note.get('text', '')[:100] + "..." if len(note.get('text', '')) > 100 else note.get('text', '')
            tags = note.get('tags', [])
            tags_text = " ".join([f"#{tag}" for tag in tags]) if tags else ""
            
            response += f"• **{timestamp}**\n{text}\n{tags_text}\n\n"
        
        await self._safe_reply(update, context, response, parse_mode='Markdown')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /analyze command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /analyze command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        chat_id = context.args[0] if context.args else None
        
        # Get messages for analysis
        try:
            messages = await self.data_manager.get_messages(chat_id=int(chat_id) if chat_id else None, limit=500)
        except Exception as e:
            logger.error(f"❌ Error fetching messages for analysis: {e}")
            await self._safe_reply(update, context, f"❌ Error fetching messages: {str(e)}")
            return
        
        if not messages:
            await self._safe_reply(update, context, "📭 No messages found for analysis.")
            return
        
        # Perform analysis
        try:
            analysis = await self.ai_analyzer.analyze_chat(
                chat_id or "general",
                f"Chat {chat_id}" if chat_id else "General Chat",
                messages
            )
            if analysis:
                await self.ai_analyzer.store_analysis(analysis)
                self.stats['analyses_performed'] += 1
                response = f"""
📊 **Chat Analysis Results**

**Overview:**
• Messages analyzed: {analysis.message_count}
• Participants: {analysis.participants}

**Sentiment Analysis:**
• Overall sentiment: {analysis.sentiment_score:.2f}

**Key Topics:**
{', '.join(analysis.key_topics[:5])}

**Business Opportunities:**
{chr(10).join([f"• {opp}" for opp in analysis.business_opportunities[:3]])}

**Recommendations:**
{chr(10).join([f"• {rec}" for rec in analysis.recommendations[:3]])}
"""
                await self._safe_reply(update, context, response, parse_mode='Markdown')
            else:
                await self._safe_reply(update, context, "❌ Failed to perform analysis (AI unavailable or no data)")
        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /status command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /status command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Get system status
        sync_status = self.data_manager.get_sync_status()
        
        # Get message count
        messages = await self.data_manager.get_messages(limit=1)
        message_count = len(messages) if messages else 0
        
        # Calculate uptime
        uptime = datetime.now() - self.stats['start_time']
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        status_text = f"""
🔄 **System Status**

**Bot Status:**
• Status: ✅ Running
• Uptime: {uptime_str}
• Messages processed: {self.stats['messages_processed']}
• Notes created: {self.stats['notes_created']}
• Analyses performed: {self.stats['analyses_performed']}

**Data Management:**
• Local messages: {message_count}
• Google Sheets: {'✅ Connected' if sync_status.get('google_sheets_enabled') else '❌ Not available'}
• Sync status: {sync_status.get('synced', 0)} synced, {sync_status.get('pending', 0)} pending, {sync_status.get('failed', 0)} failed

**AI Analysis:**
• AI client: {'✅ Available' if self.ai_analyzer.ai_client else '⚠️ Fallback mode'}
• Cache entries: {len(self.ai_analyzer.cache)}
        """
        
        await self._safe_reply(update, context, status_text, parse_mode='Markdown')
    
    async def sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /sync command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /sync command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        sync_status = self.data_manager.get_sync_status()
        
        if not sync_status.get('google_sheets_enabled'):
            await self._safe_reply(update, context, "❌ Google Sheets integration not available")
            return
        
        sync_text = f"""
🔄 **Sync Status**

**Google Sheets Integration:**
• Status: ✅ Connected
• Total items: {sync_status.get('total_items', 0)}
• Synced: {sync_status.get('synced', 0)}
• Pending: {sync_status.get('pending', 0)}
• Failed: {sync_status.get('failed', 0)}

**Sync Queue:**
• Items in queue: {self.data_manager.sync_queue.qsize()}
• Worker status: {'🟢 Running' if self.data_manager.sync_worker_running else '🔴 Stopped'}
        """
        
        await self._safe_reply(update, context, sync_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] /stats command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /stats command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Calculate performance metrics
        uptime = datetime.now() - self.stats['start_time']
        uptime_seconds = uptime.total_seconds()
        
        messages_per_hour = (self.stats['messages_processed'] / uptime_seconds) * 3600 if uptime_seconds > 0 else 0
        notes_per_hour = (self.stats['notes_created'] / uptime_seconds) * 3600 if uptime_seconds > 0 else 0
        
        stats_text = f"""
📈 **Performance Statistics**

**Bot Performance:**
• Uptime: {str(uptime).split('.')[0]}
• Messages processed: {self.stats['messages_processed']}
• Notes created: {self.stats['notes_created']}
• Analyses performed: {self.stats['analyses_performed']}
• Chats synced: {self.stats['chats_synced']}
• Contacts updated: {self.stats['contacts_updated']}
• Outreach blurbs: {self.stats['outreach_blurbs_created']}

**Processing Rates:**
• Messages/hour: {messages_per_hour:.1f}
• Notes/hour: {notes_per_hour:.1f}
• Active tasks: {len(self.processing_tasks)}

**System Health:**
• Memory usage: Optimized
• Cache efficiency: {len(self.ai_analyzer.cache)} entries
• Queue status: {self.message_queue.qsize()} items
        """
        
        await self._safe_reply(update, context, stats_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] Received message: {getattr(update.message, 'text', None)} from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] Received message: {getattr(update.message, 'text', None)} from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            return
        
        try:
            # Extract message data
            message = update.message
            message_data = {
                'message_id': message.message_id,
                'chat_id': message.chat.id,
                'chat_title': message.chat.title or message.chat.username or f"Chat {message.chat.id}",
                'user_id': message.from_user.id,
                'username': message.from_user.username or '',
                'first_name': message.from_user.first_name or '',
                'last_name': message.from_user.last_name or '',
                'message_text': message.text or '',
                'message_type': 'text',
                'timestamp': message.date.isoformat()
            }
            
            # Add to processing queue
            await self.message_queue.put(message_data)
            
            # Update stats
            self.stats['messages_processed'] += 1
            
            # Process message asynchronously
            asyncio.create_task(self._process_message(message_data))
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    async def _process_message(self, message_data: Dict[str, Any]):
        """Process message asynchronously"""
        try:
            # Store message
            success, message = await self.data_manager.add_message(message_data)
            if not success:
                logger.error(f"❌ Failed to store message: {message}")
            
            # Clean up cache periodically
            self.ai_analyzer.cleanup_cache()
            self.data_manager.cleanup_cache()
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[DEBUG] Button callback from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] Button callback from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await update.callback_query.answer("❌ Not authorized")
            return
        
        query = update.callback_query
        await query.answer()
        
        # Handle different button actions
        if query.data == "status":
            await self.status_command(update, context)
        elif query.data == "sync":
            await self.sync_command(update, context)
        elif query.data == "stats":
            await self.stats_command(update, context)
        elif query.data == "sheets":
            await self.sheets_command(update, context)
        else:
            await self._safe_reply(update, context, "❌ Unknown button action")
    
    async def start_bot(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting Optimized Telegram Bot...")
            
            # Start sync worker
            await self.data_manager.start_sync_worker()
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Bot started successfully")
            
            # Keep running
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down bot...")
            finally:
                await self.stop_bot()
                
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the bot gracefully"""
        try:
            # Stop sync worker
            self.data_manager.sync_worker_running = False
            
            # Stop application
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            # Close components
            await self.data_manager.close()
            await self.ai_analyzer.close()
            
            logger.info("✅ Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")
    
    async def read_chats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /read_chats command - Read and sync all Telegram chats"""
        print(f"[DEBUG] /read_chats command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /read_chats command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Check if Telethon credentials are available
        if not all([self.api_id, self.api_hash, self.phone]):
            await self._safe_reply(update, context, 
                "❌ Telegram API credentials not configured.\n"
                "Please set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE in your .env file.")
            return
        
        await self._safe_reply(update, context, "🔄 Starting chat reading and sync process...")
        
        try:
            # Start chat reading in background
            asyncio.create_task(self._read_all_chats(update, context))
            
        except Exception as e:
            logger.error(f"❌ Error starting chat reading: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def contacts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /contacts command - View and manage contacts"""
        print(f"[DEBUG] /contacts command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /contacts command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Get contacts from database
        contacts = await self.data_manager.get_contacts(limit=10)
        
        if not contacts:
            await self._safe_reply(update, context, "📇 No contacts found. Use /read_chats to sync your chats first.")
            return
        
        response = "📇 **Recent Contacts:**\n\n"
        
        for contact in contacts[:5]:  # Show top 5
            response += f"👤 **{contact.get('name', 'Unknown')}**\n"
            response += f"   • Username: @{contact.get('username', 'N/A')}\n"
            response += f"   • Category: {contact.get('category', 'Unknown')}\n"
            response += f"   • Lead Score: {contact.get('lead_score', 0):.1f}\n"
            response += f"   • Messages: {contact.get('message_count', 0)}\n\n"
        
        if len(contacts) > 5:
            response += f"... and {len(contacts) - 5} more contacts"
        
        await self._safe_reply(update, context, response, parse_mode='Markdown')
    
    async def leads_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leads command - View business leads"""
        print(f"[DEBUG] /leads command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /leads command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Get high-scoring contacts as leads
        contacts = await self.data_manager.get_contacts(limit=20)
        leads = [c for c in contacts if c.get('lead_score', 0) > 0.5]
        
        if not leads:
            await self._safe_reply(update, context, "🎯 No high-scoring leads found. Use /read_chats to analyze your conversations.")
            return
        
        response = "🎯 **Top Business Leads:**\n\n"
        
        for lead in sorted(leads, key=lambda x: x.get('lead_score', 0), reverse=True)[:5]:
            response += f"🔥 **{lead.get('name', 'Unknown')}** (Score: {lead.get('lead_score', 0):.1f})\n"
            response += f"   • Company: {lead.get('company', 'N/A')}\n"
            response += f"   • Role: {lead.get('role', 'N/A')}\n"
            response += f"   • Industry: {lead.get('industry', 'N/A')}\n"
            response += f"   • Last Contact: {lead.get('last_message_date', 'N/A')}\n\n"
        
        await self._safe_reply(update, context, response, parse_mode='Markdown')
    
    async def crm_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /crm command - CRM dashboard"""
        print(f"[DEBUG] /crm command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /crm command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Get CRM statistics
        contacts = await self.data_manager.get_contacts()
        messages = await self.data_manager.get_messages(limit=1)
        message_count = len(messages) if messages else 0
        
        # Calculate CRM metrics
        total_contacts = len(contacts)
        high_value_leads = len([c for c in contacts if c.get('lead_score', 0) > 0.7])
        recent_contacts = len([c for c in contacts if c.get('last_message_date')])
        
        response = "📊 **CRM Dashboard**\n\n"
        response += f"👥 **Contacts:** {total_contacts}\n"
        response += f"🎯 **High-Value Leads:** {high_value_leads}\n"
        response += f"💬 **Total Messages:** {message_count}\n"
        response += f"📅 **Recent Activity:** {recent_contacts} contacts\n\n"
        
        response += "**Quick Actions:**\n"
        response += "• `/read_chats` - Sync all chats\n"
        response += "• `/contacts` - View contacts\n"
        response += "• `/leads` - View leads\n"
        response += "• `/insights` - Business insights\n"
        response += "• `/auto_sync` - Toggle auto-sync\n"
        
        await self._safe_reply(update, context, response, parse_mode='Markdown')
    
    async def auto_sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /auto_sync command - Toggle automatic sync"""
        print(f"[DEBUG] /auto_sync command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /auto_sync command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Toggle auto sync
        self.auto_sync_enabled = not self.auto_sync_enabled
        
        status = "🟢 Enabled" if self.auto_sync_enabled else "🔴 Disabled"
        await self._safe_reply(update, context, f"🔄 Auto-sync {status}")
    
    async def insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /insights command - Business insights"""
        print(f"[DEBUG] /insights command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /insights command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Get recent messages for analysis
        messages = await self.data_manager.get_messages(limit=100)
        
        if not messages:
            await self._safe_reply(update, context, "📊 No messages to analyze. Use /read_chats to sync your chats first.")
            return
        
        await self._safe_reply(update, context, "🧠 Analyzing conversations for business insights...")
        
        try:
            # Perform analysis
            analysis = await self.ai_analyzer.analyze_chat(
                "general",
                "All Chats",
                messages
            )
            
            if analysis:
                await self.ai_analyzer.store_analysis(analysis)
                self.stats['analyses_performed'] += 1
                
                response = "🧠 **Business Insights**\n\n"
                response += f"📈 **Sentiment:** {analysis.sentiment_score:.2f}\n"
                response += f"🎯 **Key Topics:** {', '.join(analysis.key_topics[:3])}\n\n"
                
                if analysis.business_opportunities:
                    response += "💼 **Opportunities:**\n"
                    for opp in analysis.business_opportunities[:2]:
                        response += f"• {opp}\n"
                    response += "\n"
                
                if analysis.recommendations:
                    response += "💡 **Recommendations:**\n"
                    for rec in analysis.recommendations[:2]:
                        response += f"• {rec}\n"
                
                await self._safe_reply(update, context, response, parse_mode='Markdown')
            else:
                await self._safe_reply(update, context, "❌ Failed to generate insights")
                
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def dailybrief_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dailybrief command - Generate a daily summary and insights"""
        print(f"[DEBUG] /dailybrief command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /dailybrief command from user {getattr(update.effective_user, 'id', None)}")
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        # Get messages from the last 24 hours
        from datetime import datetime, timedelta
        now = datetime.now()
        since = now - timedelta(days=1)
        all_messages = await self.data_manager.get_messages(limit=1000)
        messages = [m for m in all_messages if 'timestamp' in m and m['timestamp'] and datetime.fromisoformat(str(m['timestamp'])) >= since]
        
        if not messages:
            await self._safe_reply(update, context, "📭 No messages found in the last 24 hours.")
            return
        
        await self._safe_reply(update, context, "🧠 Generating daily brief... This may take a moment.")
        
        try:
            analysis = await self.ai_analyzer.analyze_chat(
                "daily_brief",
                "Daily Brief",
                messages
            )
            if analysis:
                await self.ai_analyzer.store_analysis(analysis)
                self.stats['analyses_performed'] += 1
                
                response = """
📅 **Daily Brief**

**Messages analyzed:** {message_count}
**Participants:** {participants}
**Sentiment:** {sentiment_score:.2f}
**Key Topics:** {topics}

**Opportunities:**
{opps}

**Recommendations:**
{recs}
""".format(
    message_count=analysis.message_count,
    participants=analysis.participants,
    sentiment_score=analysis.sentiment_score,
    topics=', '.join(analysis.key_topics[:5]),
    opps='\n'.join([f"• {o}" for o in analysis.business_opportunities[:3]]) or 'None',
    recs='\n'.join([f"• {r}" for r in analysis.recommendations[:3]]) or 'None'
)
                await self._safe_reply(update, context, response, parse_mode='Markdown')
            else:
                await self._safe_reply(update, context, "❌ Failed to generate daily brief (AI unavailable or no data)")
        except Exception as e:
            logger.error(f"❌ Error generating daily brief: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def _read_all_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Read all Telegram chats and sync to database"""
        try:
            # Initialize Telethon client
            from telethon import TelegramClient
            
            self.telethon_client = TelegramClient('session_name', self.api_id, self.api_hash)
            await self.telethon_client.start(phone=self.phone)
            
            # Get all dialogs (chats)
            dialogs = await self.telethon_client.get_dialogs()
            
            total_messages = 0
            total_chats = len(dialogs)
            
            await self._safe_reply(update, context, f"📚 Found {total_chats} chats. Starting sync...")
            
            for i, dialog in enumerate(dialogs[:20]):  # Limit to 20 chats for performance
                try:
                    # Get recent messages from this chat
                    messages = await self.telethon_client.get_messages(dialog.entity, limit=50)
                    
                    chat_messages = 0
                    for message in messages:
                        if message.text:  # Only process text messages
                            message_data = {
                                'message_id': message.id,
                                'chat_id': dialog.id,
                                'chat_title': dialog.title or dialog.name or f"Chat {dialog.id}",
                                'user_id': message.sender_id if message.sender_id else 0,
                                'username': getattr(message.sender, 'username', '') if message.sender else '',
                                'first_name': getattr(message.sender, 'first_name', '') if message.sender else '',
                                'last_name': getattr(message.sender, 'last_name', '') if message.sender else '',
                                'message_text': message.text,
                                'message_type': 'text',
                                'timestamp': message.date.isoformat()
                            }
                            
                            success, _ = await self.data_manager.add_message(message_data)
                            if success:
                                chat_messages += 1
                                total_messages += 1
                    
                    # Update progress every 5 chats
                    if (i + 1) % 5 == 0:
                        await self._safe_reply(update, context, 
                            f"📚 Progress: {i + 1}/{total_chats} chats processed, {total_messages} messages synced")
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing chat {dialog.title}: {e}")
                    continue
            
            self.stats['chats_synced'] = total_chats
            
            await self._safe_reply(update, context, 
                f"✅ Sync complete!\n"
                f"📚 Chats processed: {total_chats}\n"
                f"💬 Messages synced: {total_messages}\n"
                f"🔄 Use /contacts, /leads, or /insights to view results")
            
            # Disconnect Telethon client
            await self.telethon_client.disconnect()
            
        except Exception as e:
            logger.error(f"❌ Error in chat reading: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def outreach_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /outreach command - Generate outreach blurbs for all contacts"""
        print(f"[DEBUG] /outreach command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /outreach command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        await self._safe_reply(update, context, "🎯 Generating outreach blurbs for all contacts...")
        
        try:
            # Get all contacts
            contacts = await self.data_manager.get_contacts()
            
            if not contacts:
                await self._safe_reply(update, context, 
                    "📇 No contacts found. Use `/read_chats` to sync your chats first.",
                    parse_mode='Markdown')
                return
            
            blurbs_created = 0
            
            for contact in contacts:
                # Generate personalized outreach blurb
                blurb = await self._generate_outreach_blurb(contact)
                
                # Store the blurb in database
                await self._store_outreach_blurb(contact['user_id'], blurb)
                blurbs_created += 1
            
            self.stats['outreach_blurbs_created'] = blurbs_created
            
            result_text = f"""
✅ **Outreach Blurbs Generated!**

🎯 **Blurbs Created:** {blurbs_created}
👥 **Contacts Processed:** {len(contacts)}

**Next Steps:**
• Use `/blurbs` to view all outreach blurbs
• Use `/followup` to get follow-up recommendations
• Use `/leads` to prioritize high-value contacts
            """
            
            await self._safe_reply(update, context, result_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error generating outreach blurbs: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def blurbs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /blurbs command - View existing outreach blurbs"""
        print(f"[DEBUG] /blurbs command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /blurbs command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        try:
            blurbs = await self._get_outreach_blurbs(limit=5)
            
            if not blurbs:
                await self._safe_reply(update, context, 
                    "📝 No outreach blurbs found. Use `/outreach` to generate them first.",
                    parse_mode='Markdown')
                return
            
            response = "📝 **Recent Outreach Blurbs:**\n\n"
            
            for i, blurb in enumerate(blurbs, 1):
                response += f"{i}. **{blurb['contact_name']}**\n"
                response += f"   • Type: {blurb['blurb_type']}\n"
                response += f"   • Generated: {blurb['created_at']}\n"
                response += f"   • Message:\n"
                response += f"   _{blurb['message'][:100]}..._\n\n"
            
            await self._safe_reply(update, context, response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error getting blurbs: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def followup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /followup command - Get follow-up recommendations"""
        print(f"[DEBUG] /followup command from user {getattr(update.effective_user, 'id', None)}")
        logger.info(f"[DEBUG] /followup command from user {getattr(update.effective_user, 'id', None)}")
        
        if not self._is_authorized_user(update):
            await self._safe_reply(update, context, "❌ You are not authorized to use this bot.")
            return
        
        try:
            # Get contacts that need follow-up
            contacts = await self.data_manager.get_contacts()
            
            if not contacts:
                await self._safe_reply(update, context, 
                    "📇 No contacts found. Use `/read_chats` to sync your chats first.",
                    parse_mode='Markdown')
                return
            
            # Filter contacts that need follow-up (high lead score, recent activity)
            followup_contacts = []
            for contact in contacts:
                if contact.get('lead_score', 0) > 0.5:
                    followup_contacts.append(contact)
            
            if not followup_contacts:
                await self._safe_reply(update, context, 
                    "📅 No contacts currently need follow-up. Use `/outreach` to generate new outreach blurbs.",
                    parse_mode='Markdown')
                return
            
            response = "📅 **Follow-up Recommendations:**\n\n"
            
            for i, contact in enumerate(followup_contacts[:5], 1):
                response += f"{i}. **{contact['name']}** (@{contact['username']})\n"
                response += f"   • Lead Score: {contact['lead_score']:.1f}\n"
                response += f"   • Last Contact: {contact['last_message_date']}\n"
                response += f"   • Recommended Action: {self._get_followup_action(contact)}\n\n"
            
            await self._safe_reply(update, context, response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error getting follow-up recommendations: {e}")
            await self._safe_reply(update, context, f"❌ Error: {str(e)}")
    
    async def _generate_outreach_blurb(self, contact: Dict[str, Any]) -> str:
        """Generate personalized outreach blurb for a contact"""
        try:
            name = contact.get('name', 'there')
            lead_score = contact.get('lead_score', 0)
            category = contact.get('category', 'Contact')
            company = contact.get('company', '')
            
            # Generate different types of blurbs based on lead score and category
            if lead_score > 0.8:
                blurb_type = "high_value"
                message = f"Hi {name}! 👋 I noticed our recent conversations have been really productive. I'd love to explore potential collaboration opportunities. Are you free for a quick call this week?"
            elif lead_score > 0.6:
                blurb_type = "medium_value"
                message = f"Hey {name}! Hope you're doing well. I enjoyed our recent chat and wanted to follow up on the topics we discussed. Would you be interested in continuing the conversation?"
            elif category == "High-Value Lead":
                blurb_type = "lead_nurture"
                message = f"Hi {name}! Thanks for the engaging conversation. I think there's great potential for collaboration here. Would you be open to a brief discussion about how we might work together?"
            else:
                blurb_type = "general"
                message = f"Hi {name}! Just wanted to check in and see how things are going. I enjoyed our recent conversation and would love to stay connected."
            
            return {
                'type': blurb_type,
                'message': message,
                'contact_name': name,
                'lead_score': lead_score,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating outreach blurb: {e}")
            return {
                'type': 'general',
                'message': f"Hi there! Just wanted to check in and see how things are going.",
                'contact_name': contact.get('name', 'Unknown'),
                'lead_score': 0,
                'category': 'Contact'
            }
    
    async def _store_outreach_blurb(self, user_id: int, blurb: Dict[str, Any]):
        """Store outreach blurb in database"""
        try:
            # Add to database (you can extend this to store in a separate table)
            blurb_data = {
                'user_id': user_id,
                'blurb_type': blurb['type'],
                'message': blurb['message'],
                'contact_name': blurb['contact_name'],
                'lead_score': blurb['lead_score'],
                'category': blurb['category'],
                'created_at': datetime.now().isoformat()
            }
            
            # For now, store as a note with special category
            await self.data_manager.add_note(
                text=f"OUTREACH BLURB: {blurb['message']}",
                category="outreach",
                priority="high" if blurb['lead_score'] > 0.7 else "medium"
            )
            
            logger.info(f"✅ Stored outreach blurb for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing outreach blurb: {e}")
    
    async def _get_outreach_blurbs(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get outreach blurbs from database"""
        try:
            # Get notes with outreach category
            notes = await self.data_manager.get_notes(category="outreach", limit=limit)
            
            blurbs = []
            for note in notes:
                if note['text'].startswith('OUTREACH BLURB:'):
                    message = note['text'].replace('OUTREACH BLURB: ', '')
                    blurbs.append({
                        'contact_name': 'Contact',  # Could be enhanced to extract from note
                        'blurb_type': 'general',
                        'message': message,
                        'created_at': note['timestamp']
                    })
            
            return blurbs
            
        except Exception as e:
            logger.error(f"❌ Error getting outreach blurbs: {e}")
            return []
    
    def _get_followup_action(self, contact: Dict[str, Any]) -> str:
        """Get recommended follow-up action for a contact"""
        lead_score = contact.get('lead_score', 0)
        category = contact.get('category', '')
        
        if lead_score > 0.8:
            return "Schedule high-priority meeting"
        elif lead_score > 0.6:
            return "Send detailed proposal"
        elif category == "High-Value Lead":
            return "Follow up with case study"
        else:
            return "Send general check-in message"

async def main():
    """Main entry point"""
    try:
        bot = OptimizedTelegramBot()
        await bot.start_bot()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 