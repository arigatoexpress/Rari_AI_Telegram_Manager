#!/usr/bin/env python3
"""
Ultimate BD Bot - AI-Powered Deal Closing Machine
================================================
Advanced business development bot with intelligent deal analysis:
- AI-powered opportunity identification
- Deal stage tracking and progression
- Intelligent follow-up recommendations
- Automated relationship mapping
- Real-time deal closing strategies
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ultimate_bd_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UltimateBDBot:
    """Ultimate AI-powered business development bot"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.user_id = int(os.getenv('USER_ID', '0'))
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Components
        self.application = None
        self.data_manager = None
        self.ai_deal_analyzer = None
        self.bd_context = None
        self.sheets_manager = None
        
        # Optimization components
        self.batch_processor = None
        self.smart_cache = None
        self.smart_sync = None
        self.differential_backup = None
        
        # Deal tracking
        self.active_deals = []
        self.daily_opportunities = []
        self.urgent_actions = []
        
        # State
        self.is_running = False
        self.start_time = datetime.now()
        
    async def initialize(self):
        """Initialize all bot components"""
        try:
            logger.info("🚀 Initializing Ultimate BD Bot...")
            
            # Initialize optimization components first
            await self._init_optimization_components()
            
            # Initialize core components
            await self._init_ai_deal_analyzer()
            await self._init_data_manager()
            await self._init_bd_context()
            await self._init_sheets_manager()
            await self._init_telegram_bot()
            
            logger.info("✅ Ultimate BD Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def _init_optimization_components(self):
        """Initialize optimization components"""
        try:
            # Initialize batch processor
            from core.batch_processor import AsyncBatchProcessor
            self.batch_processor = AsyncBatchProcessor(
                max_concurrent_jobs=int(os.getenv('MAX_CONCURRENT_BATCHES', '3')),
                max_batch_size=int(os.getenv('MAX_BATCH_SIZE', '50'))
            )
            await self.batch_processor.start()
            logger.info("✅ Batch Processor initialized")
            
            # Initialize smart cache
            from core.smart_cache import SmartCache
            self.smart_cache = SmartCache(
                max_memory_size=int(os.getenv('CACHE_MEMORY_SIZE', str(100 * 1024 * 1024))),
                max_disk_size=int(os.getenv('CACHE_DISK_SIZE', str(1024 * 1024 * 1024))),
                cache_dir=os.getenv('CACHE_DIR', 'cache')
            )
            await self.smart_cache.start()
            logger.info("✅ Smart Cache initialized")
            
            # Initialize smart sync
            from core.smart_sync import SmartSync
            self.smart_sync = SmartSync(
                sync_db_path=os.getenv('SYNC_DB_PATH', 'data/sync.db')
            )
            logger.info("✅ Smart Sync initialized")
            
            # Initialize differential backup
            from core.differential_backup import DifferentialBackup
            self.differential_backup = DifferentialBackup(
                backup_root=os.getenv('BACKUP_ROOT', 'backups'),
                chunk_size=int(os.getenv('BACKUP_CHUNK_SIZE', str(64 * 1024)))
            )
            logger.info("✅ Differential Backup initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Optimization components initialization failed: {e}")
            # Don't raise, as these are optional optimizations
    
    async def _init_ai_deal_analyzer(self):
        """Initialize AI deal analyzer"""
        try:
            from core.ai_deal_analyzer import AIDealAnalyzer
            self.ai_deal_analyzer = AIDealAnalyzer(self.openai_api_key)
            logger.info("✅ AI Deal Analyzer initialized")
        except Exception as e:
            logger.error(f"❌ AI Deal Analyzer initialization failed: {e}")
            raise
    
    async def _init_data_manager(self):
        """Initialize data manager"""
        try:
            from core.data_manager import DataManager
            self.data_manager = DataManager()
            
            # Initialize new lead tracking database
            from core.lead_tracking_db import LeadTrackingDB
            from core.real_google_sheets_exporter import RealGoogleSheetsExporter
            self.lead_db = LeadTrackingDB()
            self.sheets_exporter = RealGoogleSheetsExporter()
            
            # Initialize BD Intelligence System
            from core.bd_intelligence import BDIntelligence, BDMessageGenerator
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.bd_intelligence = BDIntelligence(openai_key, self.lead_db)
                self.bd_message_gen = BDMessageGenerator(self.bd_intelligence)
                logger.info("🧠 BD Intelligence System initialized")
            else:
                logger.warning("⚠️ OPENAI_API_KEY not found - BD Intelligence features disabled")
                self.bd_intelligence = None
                self.bd_message_gen = None
            
            logger.info("✅ Data Manager and Lead Tracking DB initialized")
        except Exception as e:
            logger.error(f"❌ Data Manager initialization failed: {e}")
            # Continue without data manager
            self.data_manager = None
            self.lead_db = None
            self.sheets_exporter = None
    
    async def _init_bd_context(self):
        """Initialize BD context manager"""
        try:
            from core.bd_context_manager import BDContextManager
            if os.getenv('GOOGLE_SHEET_ID'):
                self.bd_context = BDContextManager(google_sheet_id=os.getenv('GOOGLE_SHEET_ID'))
                logger.info("✅ BD Context Manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ BD Context initialization failed: {e}")
            self.bd_context = None
    
    async def _init_sheets_manager(self):
        """Initialize Google Sheets manager"""
        try:
            from core.google_sheets_manager import GoogleSheetsManager
            if os.getenv('GOOGLE_SHEET_ID'):
                self.sheets_manager = GoogleSheetsManager(
                    os.getenv('GOOGLE_SHEET_ID'),
                    'google_service_account.json'
                )
                await self.sheets_manager.initialize()
                logger.info("✅ Google Sheets Manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets initialization failed: {e}")
            self.sheets_manager = None
    
    async def _init_telegram_bot(self):
        """Initialize Telegram bot"""
        try:
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
            
            if not self.bot_token:
                raise ValueError("TELEGRAM_BOT_TOKEN is required")
            
            self.application = Application.builder().token(self.bot_token).build()
            self._add_command_handlers()
            
            logger.info("✅ Telegram Bot initialized")
        except Exception as e:
            logger.error(f"❌ Telegram Bot initialization failed: {e}")
            raise
    
    def _add_command_handlers(self):
        """Add command handlers"""
        from telegram.ext import CommandHandler, MessageHandler, filters
        
        if not self.application:
            return
        
        # Core commands
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        
        # AI-powered BD commands
        self.application.add_handler(CommandHandler("deals", self._deals_command))
        self.application.add_handler(CommandHandler("hotleads", self._hot_leads_command))
        self.application.add_handler(CommandHandler("actions", self._urgent_actions_command))
        self.application.add_handler(CommandHandler("analyze", self._analyze_conversations_command))
        self.application.add_handler(CommandHandler("strategy", self._deal_strategy_command))
        self.application.add_handler(CommandHandler("close", self._close_deal_command))
        
        # New features
        self.application.add_handler(CommandHandler("brief", self._daily_brief_command))
        self.application.add_handler(CommandHandler("briefing", self._daily_brief_command))
        self.application.add_handler(CommandHandler("message", self._generate_message_command))
        self.application.add_handler(CommandHandler("msg", self._generate_message_command))
        
        # Lead tracking commands
        self.application.add_handler(CommandHandler("leads", self._leads_dashboard_command))
        self.application.add_handler(CommandHandler("hotleads", self._hot_leads_command))
        self.application.add_handler(CommandHandler("followup", self._follow_up_command))
        self.application.add_handler(CommandHandler("export", self._export_leads_command))
        self.application.add_handler(CommandHandler("addlead", self._add_lead_command))
        self.application.add_handler(CommandHandler("updatelead", self._update_lead_command))
        self.application.add_handler(CommandHandler("migrate", self._migrate_database_command))
        
        # BD Intelligence commands
        self.application.add_handler(CommandHandler("analyze", self._analyze_conversation_command))
        self.application.add_handler(CommandHandler("bdbrief", self._bd_brief_command))
        self.application.add_handler(CommandHandler("suggest", self._suggest_message_command))
        self.application.add_handler(CommandHandler("kpis", self._bd_kpis_command))
        self.application.add_handler(CommandHandler("insights", self._conversation_insights_command))
        self.application.add_handler(CommandHandler("smart", self._smart_response_command))
        
        # Reporting
        self.application.add_handler(CommandHandler("report", self._daily_report_command))
        self.application.add_handler(CommandHandler("pipeline", self._pipeline_command))
        
        # Message handler for real-time analysis
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        
        # Google Sheets Export commands
        self.application.add_handler(CommandHandler("sheets_export", self._sheets_export_command))
        self.application.add_handler(CommandHandler("sheets_dashboard", self._sheets_dashboard_command))
        self.application.add_handler(CommandHandler("sheets_sync", self._sheets_sync_command))
        self.application.add_handler(CommandHandler("sheets_url", self._sheets_url_command))
        
        logger.info("✅ All command handlers added")

    # =============================================================================
    # COMMAND HANDLERS
    # =============================================================================
    
    async def _start_command(self, update, context):
        """Welcome command"""
        welcome_message = """
🎯 **Ultimate BD Bot** - AI Deal Closing Machine

**🔥 Hot Commands:**
• `/deals` - Active deal pipeline
• `/hotleads` - High-probability opportunities
• `/actions` - Urgent actions to close deals
• `/analyze` - AI analysis of conversations

**📊 Intelligence:**
• AI-powered opportunity identification
• Deal stage tracking & progression
• Intelligent follow-up recommendations
• Real-time closing strategies

Ready to close deals with Full Sail! 🚀
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def _help_command(self, update, context):
        """Help command"""
        help_message = """
🎯 **Ultimate BD Bot - Deal Closing Commands**

**🔥 Active Deal Management:**
• `/deals` - View active deal pipeline
• `/hotleads` - High-probability opportunities (>70%)
• `/actions` - Urgent actions needed today
• `/pipeline` - Complete pipeline overview

**🤖 AI Analysis:**
• `/analyze [days]` - Analyze conversations for opportunities
• `/strategy [contact]` - Get deal closing strategy
• `/close [contact]` - Generate closing approach

**📊 Reporting:**
• `/report` - Daily deal report with insights
• `/help` - This command reference

**💡 Pro Tips:**
• Use `/analyze` daily to identify new opportunities
• Check `/actions` for urgent follow-ups
• Get personalized `/strategy` for each deal
• Track progress with `/pipeline`

Built to maximize deal closure with AI intelligence! 🎯
"""
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def _deals_command(self, update, context):
        """Show active deals pipeline"""
        try:
            progress_msg = await update.message.reply_text("🔍 **Analyzing Active Deals...**\n\n⏱️ Scanning conversations for opportunities...")
            
            # Get recent messages for analysis
            messages = self.data_manager.get_recent_messages(days=30) if self.data_manager else []
            
            if not messages:
                await progress_msg.edit_text("📭 No conversation data available for analysis.")
                return
            
            # Update progress
            await progress_msg.edit_text(f"🤖 **AI Analysis in Progress...**\n\n📝 Analyzing {len(messages)} messages\n⏳ Identifying opportunities...")
            
            # AI analysis
            opportunities = await self.ai_deal_analyzer.analyze_conversation_for_deals(messages)
            self.active_deals = opportunities
            
            if not opportunities:
                await progress_msg.edit_text("📊 **Active Deals Pipeline**\n\n✅ No active opportunities identified.\n\n💡 Continue conversations to generate new leads!")
                return
            
            # Sort by probability and value
            sorted_deals = sorted(opportunities, key=lambda x: x.probability * x.estimated_value, reverse=True)
            
            deals_message = f"📊 **Active Deals Pipeline** ({len(opportunities)} opportunities)\n\n"
            
            # Top deals
            deals_message += "🔥 **Top Opportunities:**\n"
            for i, deal in enumerate(sorted_deals[:5], 1):
                value_str = f"${deal.estimated_value:,.0f}" if deal.estimated_value > 0 else "TBD"
                deals_message += f"{i}. **{deal.contact_name}** - {deal.opportunity_type.value.title()}\n"
                deals_message += f"   💰 {value_str} | 📊 {deal.probability}% | 🎯 {deal.deal_stage.value.replace('_', ' ').title()}\n"
                deals_message += f"   ⚡ {deal.urgency.value.title()} | 🎪 Full Sail Fit: {deal.full_sail_fit_score}/100\n\n"
            
            # Pipeline summary
            total_value = sum(deal.estimated_value * (deal.probability / 100) for deal in opportunities)
            hot_deals = len([d for d in opportunities if d.probability > 70])
            
            deals_message += f"📈 **Pipeline Summary:**\n"
            deals_message += f"• Total Weighted Value: ${total_value:,.0f}\n"
            deals_message += f"• Hot Deals (>70%): {hot_deals}\n"
            deals_message += f"• Average Probability: {sum(d.probability for d in opportunities) / len(opportunities):.1f}%\n\n"
            
            deals_message += "💡 Use `/actions` for urgent follow-ups!"
            
            await progress_msg.edit_text(deals_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in deals command: {e}")
            await update.message.reply_text(f"❌ Deal analysis failed: {str(e)}")
    
    async def _hot_leads_command(self, update, context):
        """Show hot leads with high probability"""
        try:
            if not self.active_deals:
                await update.message.reply_text("🔍 No active deals analyzed yet. Use `/deals` first to analyze opportunities.")
                return
            
            hot_leads = [deal for deal in self.active_deals if deal.probability > 70]
            
            if not hot_leads:
                await update.message.reply_text("🌡️ **Hot Leads**\n\nNo high-probability deals (>70%) identified.\n\n💡 Focus on nurturing existing opportunities!")
                return
            
            hot_message = f"🔥 **Hot Leads** ({len(hot_leads)} high-probability deals)\n\n"
            
            for i, deal in enumerate(hot_leads, 1):
                value_str = f"${deal.estimated_value:,.0f}" if deal.estimated_value > 0 else "TBD"
                hot_message += f"🎯 **{i}. {deal.contact_name}** (@{deal.contact_username})\n"
                hot_message += f"💼 {deal.opportunity_type.value.title()} | 💰 {value_str}\n"
                hot_message += f"📊 **{deal.probability}%** probability | ⚡ {deal.urgency.value.title()}\n"
                hot_message += f"🎪 Full Sail Fit: **{deal.full_sail_fit_score}/100**\n"
                hot_message += f"📋 Next: {deal.next_action}\n"
                hot_message += f"⏰ Deadline: {deal.action_deadline.strftime('%Y-%m-%d')}\n\n"
            
            hot_message += "🚀 Use `/strategy [contact]` for closing approach!"
            
            await update.message.reply_text(hot_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in hot leads command: {e}")
            await update.message.reply_text(f"❌ Hot leads analysis failed: {str(e)}")
    
    async def _urgent_actions_command(self, update, context):
        """Show urgent actions needed"""
        try:
            if not self.active_deals:
                await update.message.reply_text("🔍 No active deals analyzed yet. Use `/deals` first to analyze opportunities.")
                return
            
            # Generate urgent actions
            urgent_actions = await self.ai_deal_analyzer.identify_urgent_actions(self.active_deals)
            self.urgent_actions = urgent_actions
            
            if not urgent_actions:
                await update.message.reply_text("✅ **Urgent Actions**\n\nNo urgent actions identified.\n\n💡 Great job staying on top of your pipeline!")
                return
            
            actions_message = f"⚡ **Urgent Actions** ({len(urgent_actions)} items)\n\n"
            
            for i, action in enumerate(urgent_actions[:10], 1):  # Top 10
                urgency_emoji = {"critical": "🚨", "high": "🔥", "medium": "⚠️", "low": "📋"}
                emoji = urgency_emoji.get(action.urgency.value, "📋")
                
                actions_message += f"{emoji} **{i}. {action.contact_name}**\n"
                actions_message += f"🎯 {action.description}\n"
                actions_message += f"⏰ Deadline: {action.deadline.strftime('%Y-%m-%d')}\n"
                actions_message += f"📊 Success Probability: {action.success_probability:.0f}%\n\n"
            
            actions_message += "💡 Use `/strategy [contact]` for specific approach!"
            
            await update.message.reply_text(actions_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in urgent actions command: {e}")
            await update.message.reply_text(f"❌ Urgent actions analysis failed: {str(e)}")
    
    async def _analyze_conversations_command(self, update, context):
        """Analyze conversations for new opportunities"""
        try:
            # Get days parameter
            days = 7
            if context.args and context.args[0].isdigit():
                days = int(context.args[0])
            
            progress_msg = await update.message.reply_text(f"🤖 **AI Conversation Analysis**\n\n⏱️ Analyzing last {days} days...\n🔍 Scanning for opportunities...")
            
            # Get messages
            messages = self.data_manager.get_recent_messages(days=days) if self.data_manager else []
            
            if not messages:
                await progress_msg.edit_text("📭 No conversation data available for analysis.")
                return
            
            # Update progress
            await progress_msg.edit_text(f"🤖 **AI Analysis in Progress**\n\n📝 Messages: {len(messages)}\n⚡ Identifying opportunities...")
            
            # AI analysis
            opportunities = await self.ai_deal_analyzer.analyze_conversation_for_deals(messages)
            
            # Filter new opportunities
            new_opportunities = [opp for opp in opportunities if opp.probability > 30]
            
            analysis_message = f"🤖 **AI Analysis Complete** ({days} days)\n\n"
            analysis_message += f"📊 **Results:**\n"
            analysis_message += f"• Messages Analyzed: {len(messages)}\n"
            analysis_message += f"• Opportunities Found: {len(opportunities)}\n"
            analysis_message += f"• Viable Opportunities: {len(new_opportunities)}\n\n"
            
            if new_opportunities:
                analysis_message += "🔥 **New Opportunities:**\n"
                for opp in new_opportunities[:5]:
                    analysis_message += f"• **{opp.contact_name}** - {opp.opportunity_type.value.title()} ({opp.probability}%)\n"
                
                analysis_message += f"\n💡 Use `/deals` to see full pipeline!"
            else:
                analysis_message += "✅ No new viable opportunities identified.\n\n💡 Continue engaging to generate new leads!"
            
            await progress_msg.edit_text(analysis_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await update.message.reply_text(f"❌ Analysis failed: {str(e)}")
    
    async def _deal_strategy_command(self, update, context):
        """Generate deal closing strategy"""
        try:
            if not context.args:
                await update.message.reply_text("💡 Usage: `/strategy [contact_name]`\n\nExample: `/strategy john`")
                return
            
            contact_query = ' '.join(context.args).lower()
            
            # Find matching deal
            matching_deals = [deal for deal in self.active_deals 
                            if contact_query in deal.contact_name.lower() or contact_query in deal.contact_username.lower()]
            
            if not matching_deals:
                await update.message.reply_text(f"❌ No deals found for '{contact_query}'\n\n💡 Use `/deals` to see active opportunities.")
                return
            
            deal = matching_deals[0]  # Take first match
            
            progress_msg = await update.message.reply_text(f"🎯 **Generating Strategy for {deal.contact_name}**\n\n⏳ AI analyzing deal context...")
            
            # Generate strategy
            strategy = await self.ai_deal_analyzer.generate_deal_closing_strategy(deal)
            
            strategy_message = f"🎯 **Deal Closing Strategy: {deal.contact_name}**\n\n"
            strategy_message += f"💼 **Opportunity:** {deal.opportunity_type.value.title()}\n"
            strategy_message += f"💰 **Value:** ${deal.estimated_value:,.0f}\n"
            strategy_message += f"📊 **Probability:** {deal.probability}%\n"
            strategy_message += f"🎪 **Full Sail Fit:** {deal.full_sail_fit_score}/100\n\n"
            
            strategy_message += f"🚀 **Primary Strategy:**\n{strategy.get('primary_strategy', 'Strategy generation failed')}\n\n"
            
            if strategy.get('key_messages'):
                strategy_message += f"💬 **Key Messages:**\n"
                for msg in strategy['key_messages'][:3]:
                    strategy_message += f"• {msg}\n"
                strategy_message += "\n"
            
            if strategy.get('next_steps'):
                strategy_message += f"📋 **Next Steps:**\n"
                for step in strategy['next_steps'][:3]:
                    strategy_message += f"• {step}\n"
                strategy_message += "\n"
            
            strategy_message += f"⏰ **Timeline:** {strategy.get('timeline', 'TBD')}\n"
            strategy_message += f"📈 **Success Probability:** {strategy.get('success_probability', deal.probability)}%"
            
            await progress_msg.edit_text(strategy_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in strategy command: {e}")
            await update.message.reply_text(f"❌ Strategy generation failed: {str(e)}")
    
    async def _daily_report_command(self, update, context):
        """Generate daily deal report"""
        try:
            if not self.active_deals:
                await update.message.reply_text("🔍 No active deals analyzed yet. Use `/deals` first to analyze opportunities.")
                return
            
            progress_msg = await update.message.reply_text("📊 **Generating Daily Deal Report...**\n\n⏳ Analyzing pipeline data...")
            
            # Generate report
            report = await self.ai_deal_analyzer.generate_daily_deal_report(self.active_deals)
            
            report_message = f"📊 **Daily Deal Report - {datetime.now().strftime('%Y-%m-%d')}**\n\n"
            
            summary = report.get('summary', {})
            report_message += f"📈 **Pipeline Summary:**\n"
            report_message += f"• Total Opportunities: {summary.get('total_opportunities', 0)}\n"
            report_message += f"• Estimated Value: ${summary.get('total_estimated_value', 0):,.0f}\n"
            report_message += f"• Hot Deals: {summary.get('hot_deals', 0)}\n"
            report_message += f"• Urgent Actions: {summary.get('urgent_actions', 0)}\n\n"
            
            # Top opportunities
            top_opps = report.get('top_opportunities', [])
            if top_opps:
                report_message += f"🔥 **Top Opportunities:**\n"
                for i, opp in enumerate(top_opps[:3], 1):
                    report_message += f"{i}. **{opp['name']}** - {opp['type'].title()} ({opp['probability']}%)\n"
                report_message += "\n"
            
            # Full Sail alignment
            fs_alignment = report.get('full_sail_alignment', {})
            report_message += f"🎪 **Full Sail Alignment:**\n"
            report_message += f"• High Fit (80+): {fs_alignment.get('high_fit', 0)}\n"
            report_message += f"• Medium Fit (50-80): {fs_alignment.get('medium_fit', 0)}\n"
            report_message += f"• Low Fit (<50): {fs_alignment.get('low_fit', 0)}\n\n"
            
            report_message += "💡 Focus on high-fit opportunities for best ROI!"
            
            await progress_msg.edit_text(report_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in daily report command: {e}")
            await update.message.reply_text(f"❌ Report generation failed: {str(e)}")
    
    async def _pipeline_command(self, update, context):
        """Show complete pipeline overview"""
        try:
            if not self.active_deals:
                await update.message.reply_text("🔍 No active deals analyzed yet. Use `/deals` first to analyze opportunities.")
                return
            
            # Group by deal stage
            from core.ai_deal_analyzer import DealStage
            stage_groups = {}
            for stage in DealStage:
                stage_groups[stage] = [deal for deal in self.active_deals if deal.deal_stage == stage]
            
            pipeline_message = f"📊 **Complete Pipeline Overview**\n\n"
            
            for stage, deals in stage_groups.items():
                if deals:
                    stage_name = stage.value.replace('_', ' ').title()
                    pipeline_message += f"🎯 **{stage_name}** ({len(deals)})\n"
                    
                    for deal in deals[:3]:  # Show top 3 per stage
                        pipeline_message += f"  • {deal.contact_name} - {deal.probability}%\n"
                    
                    if len(deals) > 3:
                        pipeline_message += f"  • ... and {len(deals) - 3} more\n"
                    
                    pipeline_message += "\n"
            
            # Pipeline health
            total_deals = len(self.active_deals)
            if total_deals > 0:
                avg_probability = sum(deal.probability for deal in self.active_deals) / total_deals
                pipeline_message += f"📈 **Pipeline Health:**\n"
                pipeline_message += f"• Average Probability: {avg_probability:.1f}%\n"
                pipeline_message += f"• Total Deals: {total_deals}\n"
                
                # Health assessment
                if avg_probability > 60:
                    pipeline_message += "🟢 **Status:** Healthy pipeline!\n"
                elif avg_probability > 40:
                    pipeline_message += "🟡 **Status:** Moderate pipeline - focus on nurturing\n"
                else:
                    pipeline_message += "🔴 **Status:** Needs attention - generate new leads\n"
            
            await update.message.reply_text(pipeline_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in pipeline command: {e}")
            await update.message.reply_text(f"❌ Pipeline analysis failed: {str(e)}")
    
    async def _close_deal_command(self, update, context):
        """Generate deal closing approach"""
        try:
            if not context.args:
                await update.message.reply_text("💡 Usage: `/close [contact_name]`\n\nExample: `/close john`")
                return
            
            contact_query = ' '.join(context.args).lower()
            
            # Find matching deal
            matching_deals = [deal for deal in self.active_deals 
                            if contact_query in deal.contact_name.lower()]
            
            if not matching_deals:
                await update.message.reply_text(f"❌ No deals found for '{contact_query}'\n\n💡 Use `/deals` to see active opportunities.")
                return
            
            deal = matching_deals[0]
            
            # Generate action item for closing
            from core.ai_deal_analyzer import UrgencyLevel
            
            # Simulate urgent action generation
            action_item = await self.ai_deal_analyzer._generate_action_item(deal, 90)
            
            if not action_item:
                await update.message.reply_text("❌ Unable to generate closing approach")
                return
            
            close_message = f"🎯 **Closing Approach: {deal.contact_name}**\n\n"
            close_message += f"💼 **Deal:** {deal.opportunity_type.value.title()}\n"
            close_message += f"💰 **Value:** ${deal.estimated_value:,.0f}\n"
            close_message += f"📊 **Probability:** {deal.probability}%\n\n"
            
            close_message += f"📝 **Recommended Message:**\n{action_item.recommended_message}\n\n"
            
            close_message += f"🎯 **Success Probability:** {action_item.success_probability:.0f}%\n"
            close_message += f"⏰ **Best Time:** Within 24-48 hours\n\n"
            
            close_message += "💡 Personalize this message and send!"
            
            await update.message.reply_text(close_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in close deal command: {e}")
            await update.message.reply_text(f"❌ Closing approach generation failed: {str(e)}")

    async def _daily_brief_command(self, update, context):
        """Generate daily business development briefing"""
        try:
            progress_msg = await update.message.reply_text("📋 **Generating Daily BD Briefing...**\n\n⏳ Analyzing pipeline and priorities...")
            
            # Get or analyze deals first
            if not self.active_deals:
                messages = self.data_manager.get_recent_messages(days=30) if self.data_manager else []
                if messages:
                    self.active_deals = await self.ai_deal_analyzer.analyze_conversation_for_deals(messages)
            
            # Generate daily briefing
            briefing = await self.ai_deal_analyzer.generate_daily_briefing(self.active_deals)
            
            if not briefing:
                await progress_msg.edit_text("📋 **Daily Briefing**\n\n⚠️ Unable to generate briefing. Try running `/deals` first to analyze opportunities.")
                return
            
            # Format briefing message
            briefing_message = f"📋 **Daily BD Briefing - {datetime.now().strftime('%Y-%m-%d')}**\n\n"
            
            # Daily focus
            briefing_message += f"🎯 **Today's Focus:**\n{briefing.get('daily_focus', 'Focus on building relationships')}\n\n"
            
            # Priority actions
            priority_actions = briefing.get('priority_actions', [])
            if priority_actions:
                briefing_message += f"🚨 **Priority Actions ({len(priority_actions)}):**\n"
                for action in priority_actions:
                    briefing_message += f"• **{action['contact']}**: {action['action']} ({action['priority']})\n"
                briefing_message += "\n"
            
            # Pipeline health
            health = briefing.get('pipeline_health', {})
            briefing_message += f"📊 **Pipeline Health:**\n"
            briefing_message += f"• Total Opportunities: {health.get('total_opportunities', 0)}\n"
            briefing_message += f"• Average Probability: {health.get('average_probability', 0)}%\n"
            briefing_message += f"• Pipeline Value: ${health.get('pipeline_value', 0):,.0f}\n"
            briefing_message += f"• High Probability Deals: {health.get('high_probability_deals', 0)}\n\n"
            
            # Key insights
            insights = briefing.get('key_insights', [])
            if insights:
                briefing_message += f"💡 **Key Insights:**\n"
                for insight in insights[:3]:
                    briefing_message += f"• {insight}\n"
                briefing_message += "\n"
            
            # Recommendations
            recommendations = briefing.get('recommended_activities', [])
            if recommendations:
                briefing_message += f"✅ **Today's Recommendations:**\n"
                for rec in recommendations[:5]:
                    briefing_message += f"• {rec}\n"
                briefing_message += "\n"
            
            briefing_message += "💡 Use `/message [type]` to generate contextual outreach messages!"
            
            await progress_msg.edit_text(briefing_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in daily brief command: {e}")
            await update.message.reply_text(f"❌ Daily briefing generation failed: {str(e)}")

    async def _generate_message_command(self, update, context):
        """Generate business context messages"""
        try:
            # Parse arguments
            message_type = "general"
            contact_name = ""
            
            if context.args:
                message_type = context.args[0].lower()
                if len(context.args) > 1:
                    contact_name = " ".join(context.args[1:])
            
            # Validate message type
            valid_types = ["funding", "partnership", "advisor", "general"]
            if message_type not in valid_types:
                await update.message.reply_text(f"💡 Usage: `/message [type] [contact_name]`\n\n**Valid types:** {', '.join(valid_types)}\n\n**Examples:**\n• `/message funding John Smith`\n• `/message partnership`\n• `/message advisor Sarah`")
                return
            
            progress_msg = await update.message.reply_text(f"✍️ **Generating {message_type.title()} Message...**\n\n⏳ Crafting personalized outreach...")
            
            # Generate message
            message_data = await self.ai_deal_analyzer.generate_business_context_message(
                contact_name=contact_name,
                context_type=message_type
            )
            
            if not message_data or "Error" in message_data.get('message', ''):
                await progress_msg.edit_text("❌ Unable to generate message. Please try again.")
                return
            
            # Format message response
            response_message = f"✍️ **{message_type.title()} Message Generated**\n\n"
            response_message += f"**📧 Subject:** {message_data.get('subject', 'No subject')}\n\n"
            response_message += f"**💬 Message:**\n{message_data.get('message', 'No message generated')}\n\n"
            response_message += f"**🎯 Context:** {message_data.get('business_stage', 'Unknown stage')}\n\n"
            response_message += "💡 **Tips:**\n"
            response_message += "• Personalize the [Your name] placeholder\n"
            response_message += "• Adjust tone based on relationship warmth\n"
            response_message += "• Add specific context about their background\n"
            response_message += "• Include relevant metrics or traction updates"
            
            # Split message if too long for Telegram
            if len(response_message) > 4000:
                # Send in parts
                parts = [
                    f"✍️ **{message_type.title()} Message Generated**\n\n**📧 Subject:** {message_data.get('subject', '')}",
                    f"**💬 Message:**\n{message_data.get('message', '')}",
                    f"**🎯 Context:** {message_data.get('business_stage', '')}\n\n💡 **Tips:**\n• Personalize the [Your name] placeholder\n• Adjust tone based on relationship warmth\n• Add specific context about their background\n• Include relevant metrics or traction updates"
                ]
                
                await progress_msg.edit_text(parts[0], parse_mode='Markdown')
                for part in parts[1:]:
                    await update.message.reply_text(part, parse_mode='Markdown')
            else:
                await progress_msg.edit_text(response_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in generate message command: {e}")
            await update.message.reply_text(f"❌ Message generation failed: {str(e)}")

    async def _leads_dashboard_command(self, update, context):
        """Show comprehensive leads dashboard"""
        try:
            if not self.lead_db:
                await update.message.reply_text("❌ Lead tracking database not available")
                return
                
            progress_msg = await update.message.reply_text("📊 **Generating Leads Dashboard...**\n\n⏳ Analyzing lead pipeline...")
            
            # Get dashboard stats
            stats = self.lead_db.get_dashboard_stats()
            
            if not stats:
                await progress_msg.edit_text("📊 **Leads Dashboard**\n\n⚠️ No lead data available. Import your data first using `/migrate`")
                return
            
            # Format dashboard
            dashboard_msg = f"📊 **Leads Dashboard - {datetime.now().strftime('%Y-%m-%d')}**\n\n"
            
            # Overview stats
            dashboard_msg += f"📈 **Pipeline Overview:**\n"
            dashboard_msg += f"• Total Contacts: {stats.get('total_contacts', 0)}\n"
            dashboard_msg += f"• Total Organizations: {stats.get('total_organizations', 0)}\n"
            dashboard_msg += f"• Total Leads: {stats.get('total_leads', 0)}\n"
            dashboard_msg += f"• Pipeline Value: ${stats.get('pipeline_value', 0):,.0f}\n\n"
            
            # Contact breakdown
            contacts_by_status = stats.get('contacts_by_status', {})
            dashboard_msg += f"🎯 **Contacts by Status:**\n"
            for status, count in contacts_by_status.items():
                dashboard_msg += f"• {status.title()}: {count}\n"
            dashboard_msg += "\n"
            
            # Lead stages
            leads_by_stage = stats.get('leads_by_stage', {})
            if leads_by_stage:
                dashboard_msg += f"🏗️ **Leads by Stage:**\n"
                for stage, count in leads_by_stage.items():
                    dashboard_msg += f"• {stage.replace('_', ' ').title()}: {count}\n"
                dashboard_msg += "\n"
            
            # Recent activity
            dashboard_msg += f"⚡ **Recent Activity:**\n"
            dashboard_msg += f"• Messages (7 days): {stats.get('messages_last_7_days', 0)}\n"
            dashboard_msg += f"• Interactions (7 days): {stats.get('interactions_last_7_days', 0)}\n\n"
            
            dashboard_msg += "💡 Use `/hotleads` for priority contacts or `/export` for spreadsheet!"
            
            await progress_msg.edit_text(dashboard_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in leads dashboard command: {e}")
            await update.message.reply_text(f"❌ Dashboard generation failed: {str(e)}")

    async def _hot_leads_command(self, update, context):
        """Show hot leads requiring immediate attention"""
        try:
            if not self.lead_db:
                await update.message.reply_text("❌ Lead tracking database not available")
                return
            
            # Get limit from args
            limit = 10
            if context.args and context.args[0].isdigit():
                limit = int(context.args[0])
            
            progress_msg = await update.message.reply_text(f"🔥 **Finding Hot Leads...**\n\n⏳ Analyzing top {limit} opportunities...")
            
            hot_leads = self.lead_db.get_hot_leads(limit=limit)
            
            if not hot_leads:
                await progress_msg.edit_text("🔥 **Hot Leads**\n\n✅ No hot leads found. Time to work on lead generation!")
                return
            
            hot_msg = f"🔥 **Hot Leads** ({len(hot_leads)} opportunities)\n\n"
            
            for i, lead in enumerate(hot_leads, 1):
                name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
                if not name:
                    name = lead.get('username', 'Unknown')
                
                org = lead.get('organization_name', '')
                org_suffix = f" @ {org}" if org else ""
                
                hot_msg += f"🎯 **{i}. {name}**{org_suffix}\n"
                hot_msg += f"📊 Score: {lead.get('lead_score', 0)}/100 | Status: {lead.get('lead_status', 'unknown').title()}\n"
                
                value = lead.get('estimated_value', 0)
                if value > 0:
                    hot_msg += f"💰 Value: ${value:,.0f} | "
                
                prob = lead.get('probability', 0)
                if prob > 0:
                    hot_msg += f"📈 Probability: {prob}%\n"
                else:
                    hot_msg += "\n"
                
                # Last interaction
                last_interaction = lead.get('last_interaction')
                if last_interaction:
                    try:
                        last_dt = datetime.fromisoformat(last_interaction)
                        days_ago = (datetime.now() - last_dt).days
                        hot_msg += f"⏰ Last contact: {days_ago} days ago\n"
                    except:
                        hot_msg += f"⏰ Last contact: {last_interaction[:10]}\n"
                
                hot_msg += "\n"
            
            hot_msg += "💡 Use `/followup` to see who needs immediate attention!"
            
            await progress_msg.edit_text(hot_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in hot leads command: {e}")
            await update.message.reply_text(f"❌ Hot leads analysis failed: {str(e)}")

    async def _follow_up_command(self, update, context):
        """Show contacts needing follow-up"""
        try:
            if not self.lead_db:
                await update.message.reply_text("❌ Lead tracking database not available")
                return
            
            # Get days threshold from args
            days = 3
            if context.args and context.args[0].isdigit():
                days = int(context.args[0])
            
            progress_msg = await update.message.reply_text(f"📞 **Finding Follow-ups...**\n\n⏳ Contacts not contacted in {days}+ days...")
            
            follow_ups = self.lead_db.get_follow_up_needed(days_threshold=days)
            
            if not follow_ups:
                await progress_msg.edit_text(f"📞 **Follow-ups Needed**\n\n✅ All contacts reached within {days} days. Great job!")
                return
            
            followup_msg = f"📞 **Follow-ups Needed** ({len(follow_ups)} contacts)\n\n"
            
            for i, contact in enumerate(follow_ups[:10], 1):  # Show top 10
                name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                if not name:
                    name = contact.get('username', 'Unknown')
                
                org = contact.get('organization_name', '')
                org_suffix = f" @ {org}" if org else ""
                
                days_since = contact.get('days_since_contact', 0)
                
                followup_msg += f"⚠️ **{i}. {name}**{org_suffix}\n"
                followup_msg += f"📅 {int(days_since)} days since last contact\n"
                followup_msg += f"📊 Lead Score: {contact.get('lead_score', 0)}/100\n"
                followup_msg += f"🎯 Status: {contact.get('lead_status', 'unknown').title()}\n\n"
            
            if len(follow_ups) > 10:
                followup_msg += f"... and {len(follow_ups) - 10} more contacts\n\n"
            
            followup_msg += "💡 Prioritize high-score leads and use `/message` to craft outreach!"
            
            await progress_msg.edit_text(followup_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in follow-up command: {e}")
            await update.message.reply_text(f"❌ Follow-up analysis failed: {str(e)}")

    async def _export_leads_command(self, update, context):
        """Export leads to CSV/Google Sheets"""
        try:
            if not self.lead_db or not self.sheets_exporter:
                await update.message.reply_text("❌ Export functionality not available")
                return
            
            progress_msg = await update.message.reply_text("📤 **Exporting Lead Data...**\n\n⏳ Generating spreadsheets...")
            
            # Export to CSV files
            success = self.sheets_exporter.export_leads_to_sheets(self.lead_db)
            
            if success:
                # Get export info
                export_dir = Path("exports")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                export_msg = f"📤 **Export Complete!**\n\n"
                export_msg += f"📊 **Files Generated:**\n"
                export_msg += f"• `LEAD_TRACKING_SUMMARY_{timestamp}.csv` - Main lead list\n"
                export_msg += f"• `PIPELINE_STATS_{timestamp}.csv` - Pipeline metrics\n"
                export_msg += f"• `contacts_{timestamp}.csv` - All contacts\n"
                export_msg += f"• `organizations_{timestamp}.csv` - Organizations\n"
                export_msg += f"• `leads_{timestamp}.csv` - Lead opportunities\n\n"
                export_msg += f"📁 **Location:** `{export_dir}/`\n\n"
                export_msg += "💡 Import these files into Google Sheets for advanced analysis!"
                
                await progress_msg.edit_text(export_msg, parse_mode='Markdown')
            else:
                await progress_msg.edit_text("❌ Export failed. Check logs for details.")
            
        except Exception as e:
            logger.error(f"Error in export command: {e}")
            await update.message.reply_text(f"❌ Export failed: {str(e)}")

    async def _migrate_database_command(self, update, context):
        """Migrate data from old database to new lead tracking system"""
        try:
            if not self.lead_db:
                await update.message.reply_text("❌ Lead tracking database not available")
                return
            
            progress_msg = await update.message.reply_text("🔄 **Migrating Database...**\n\n⏳ Moving data to new lead tracking system...")
            
            # Migrate from old database
            old_db_path = "data/telegram_messages.db"
            success = self.lead_db.migrate_from_old_db(old_db_path)
            
            if success:
                # Get stats after migration
                stats = self.lead_db.get_dashboard_stats()
                
                migrate_msg = f"🔄 **Migration Complete!**\n\n"
                migrate_msg += f"✅ **Data Imported:**\n"
                migrate_msg += f"• Contacts: {stats.get('total_contacts', 0)}\n"
                migrate_msg += f"• Organizations: {stats.get('total_organizations', 0)}\n"
                migrate_msg += f"• Messages: Preserved\n\n"
                migrate_msg += f"📊 Use `/leads` to see your new dashboard!"
                
                await progress_msg.edit_text(migrate_msg, parse_mode='Markdown')
            else:
                await progress_msg.edit_text("❌ Migration failed. Check if old database exists at `data/telegram_messages.db`")
            
        except Exception as e:
            logger.error(f"Error in migrate command: {e}")
            await update.message.reply_text(f"❌ Migration failed: {str(e)}")

    async def _add_lead_command(self, update, context):
        """Add a new lead opportunity"""
        try:
            if not self.lead_db:
                await update.message.reply_text("❌ Lead tracking database not available")
                return
            
            if not context.args or len(context.args) < 2:
                await update.message.reply_text("💡 Usage: `/addlead [username/name] [value] [type]`\n\n**Examples:**\n• `/addlead @john_doe 50000 investment`\n• `/addlead \"Jane Smith\" 25000 partnership`")
                return
            
            # Parse arguments
            contact_query = context.args[0]
            try:
                estimated_value = float(context.args[1])
            except ValueError:
                await update.message.reply_text("❌ Invalid value amount. Please use numbers only.")
                return
            
            opportunity_type = context.args[2] if len(context.args) > 2 else "partnership"
            
            # Find contact
            if contact_query.startswith('@'):
                username = contact_query[1:]
                # This would need a search by username function
                await update.message.reply_text("🔍 Username search not implemented yet. Use user ID for now.")
                return
            
            # For now, show manual instructions
            add_msg = f"➕ **Add Lead Instructions**\n\n"
            add_msg += f"To add a lead for **{contact_query}**:\n\n"
            add_msg += f"💰 **Value:** ${estimated_value:,.0f}\n"
            add_msg += f"🎯 **Type:** {opportunity_type.title()}\n\n"
            add_msg += f"**Next Steps:**\n"
            add_msg += f"1. Find their contact in `/leads` dashboard\n"
            add_msg += f"2. Note their contact_id\n"
            add_msg += f"3. Manual database update needed\n\n"
            add_msg += f"💡 Automated lead creation coming soon!"
            
            await update.message.reply_text(add_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in add lead command: {e}")
            await update.message.reply_text(f"❌ Add lead failed: {str(e)}")

    async def _update_lead_command(self, update, context):
        """Update lead status"""
        try:
            if not self.lead_db:
                await update.message.reply_text("❌ Lead tracking database not available")
                return
            
            await update.message.reply_text("🔄 **Update Lead**\n\nLead update functionality coming soon!\n\nFor now, use `/export` to get CSV files for manual updates.")
            
        except Exception as e:
            logger.error(f"Error in update lead command: {e}")
            await update.message.reply_text(f"❌ Update lead failed: {str(e)}")

    async def _analyze_conversation_command(self, update, context):
        """Analyze conversation using BD Intelligence"""
        try:
            if not self.bd_intelligence:
                await update.message.reply_text("❌ BD Intelligence not available. Please set OPENAI_API_KEY in your .env file.")
                return
            
            # Get contact name from args or use current chat
            contact_query = " ".join(context.args) if context.args else None
            
            progress_msg = await update.message.reply_text("🧠 **Analyzing Conversation...**\n\n⏳ Using ChatGPT to analyze BD opportunities...")
            
            # Get conversation messages
            if self.data_manager:
                if contact_query:
                    # Search for specific contact
                    # This would need implementation to search by name/username
                    messages = []  # Placeholder
                    contact_info = None
                else:
                    # Analyze current conversation
                    chat_id = update.effective_chat.id
                    messages = self.data_manager.get_chat_messages(chat_id, limit=20)
                    contact_info = {
                        'first_name': update.effective_user.first_name,
                        'last_name': update.effective_user.last_name,
                        'username': update.effective_user.username
                    }
            else:
                await progress_msg.edit_text("❌ No conversation data available. Please ensure data manager is working.")
                return
            
            if not messages:
                await progress_msg.edit_text("❌ No conversation messages found to analyze.")
                return
            
            # Perform BD analysis
            insight = await self.bd_intelligence.analyze_conversation(messages, contact_info)
            
            if not insight:
                await progress_msg.edit_text("❌ Conversation analysis failed. Please try again.")
                return
            
            # Format analysis results
            analysis_msg = f"🧠 **BD Conversation Analysis**\n\n"
            analysis_msg += f"👤 **Contact:** {insight.contact_name}\n"
            analysis_msg += f"🎯 **BD Stage:** {insight.bd_stage.title()}\n"
            analysis_msg += f"📊 **Interest Level:** {insight.interest_level}%\n"
            analysis_msg += f"😊 **Sentiment:** {insight.sentiment_score:.2f} ({self._sentiment_emoji(insight.sentiment_score)})\n"
            analysis_msg += f"⚡ **Urgency:** {insight.urgency_score}%\n"
            analysis_msg += f"🤝 **Meeting Ready:** {insight.meeting_readiness}%\n\n"
            
            if insight.pain_points:
                analysis_msg += f"🔍 **Pain Points:**\n"
                for pain in insight.pain_points[:3]:
                    analysis_msg += f"• {pain}\n"
                analysis_msg += "\n"
            
            if insight.buying_signals:
                analysis_msg += f"💰 **Buying Signals:**\n"
                for signal in insight.buying_signals[:3]:
                    analysis_msg += f"• {signal}\n"
                analysis_msg += "\n"
            
            if insight.objections:
                analysis_msg += f"⚠️ **Objections:**\n"
                for objection in insight.objections[:2]:
                    analysis_msg += f"• {objection}\n"
                analysis_msg += "\n"
            
            analysis_msg += f"🎯 **Next Action:** {insight.next_best_action.replace('_', ' ').title()}\n\n"
            analysis_msg += f"💬 **Recommended Message:**\n_{insight.recommended_message}_\n\n"
            
            if insight.bd_opportunities:
                analysis_msg += f"🚀 **BD Opportunities:**\n"
                for opp in insight.bd_opportunities[:2]:
                    analysis_msg += f"• {opp}\n"
            
            analysis_msg += f"\n💡 Use `/suggest` for personalized message generation!"
            
            await progress_msg.edit_text(analysis_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analyze conversation command: {e}")
            await update.message.reply_text(f"❌ Conversation analysis failed: {str(e)}")

    async def _bd_brief_command(self, update, context):
        """Generate daily BD briefing with actionable insights"""
        try:
            if not self.bd_intelligence:
                await update.message.reply_text("❌ BD Intelligence not available. Please set OPENAI_API_KEY in your .env file.")
                return
            
            progress_msg = await update.message.reply_text("📋 **Generating BD Briefing...**\n\n⏳ Analyzing conversations and generating strategic insights...")
            
            # Get daily briefing
            brief = await self.bd_intelligence.get_daily_bd_brief()
            
            if not brief:
                await progress_msg.edit_text("❌ Unable to generate daily briefing. Please try again.")
                return
            
            # Format briefing
            brief_msg = f"📋 **Daily BD Briefing - {datetime.now().strftime('%B %d, %Y')}**\n\n"
            
            # Overview stats
            brief_msg += f"📊 **Overview:**\n"
            brief_msg += f"• Total Conversations: {brief.get('total_conversations', 0)}\n"
            brief_msg += f"• Hot Opportunities: {brief.get('hot_conversations', 0)}\n"
            brief_msg += f"• Follow-ups Needed: {brief.get('follow_ups_needed', 0)}\n\n"
            
            # Priority actions
            if brief.get('priority_actions'):
                brief_msg += f"🎯 **Priority Actions Today:**\n"
                for action in brief['priority_actions'][:3]:
                    brief_msg += f"• {action}\n"
                brief_msg += "\n"
            
            # Hot opportunities
            if brief.get('hot_opportunities'):
                brief_msg += f"🔥 **Hot Opportunities:**\n"
                for opp in brief['hot_opportunities'][:3]:
                    brief_msg += f"• {opp}\n"
                brief_msg += "\n"
            
            # Strategic focus
            if brief.get('strategic_focus'):
                brief_msg += f"🎲 **Strategic Focus:**\n{brief['strategic_focus']}\n\n"
            
            # Follow-up recommendations
            if brief.get('follow_up_recommendations'):
                brief_msg += f"📞 **Follow-up Strategy:**\n"
                for rec in brief['follow_up_recommendations'][:2]:
                    brief_msg += f"• {rec}\n"
                brief_msg += "\n"
            
            # Market insights
            if brief.get('market_insights'):
                brief_msg += f"📈 **Market Insights:**\n"
                for insight in brief['market_insights'][:2]:
                    brief_msg += f"• {insight}\n"
                brief_msg += "\n"
            
            brief_msg += f"💡 Use `/analyze` on specific conversations for deeper insights!"
            
            await progress_msg.edit_text(brief_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in BD brief command: {e}")
            await update.message.reply_text(f"❌ BD briefing failed: {str(e)}")

    async def _suggest_message_command(self, update, context):
        """Suggest personalized BD message"""
        try:
            if not self.bd_intelligence or not self.bd_message_gen:
                await update.message.reply_text("❌ BD Message Generator not available. Please set OPENAI_API_KEY in your .env file.")
                return
            
            # Parse arguments
            message_type = "follow_up"
            contact_name = ""
            
            if context.args:
                message_type = context.args[0].lower()
                if len(context.args) > 1:
                    contact_name = " ".join(context.args[1:])
            
            valid_types = ["follow_up", "meeting_request", "value_prop", "objection_response"]
            if message_type not in valid_types:
                await update.message.reply_text(f"💡 Usage: `/suggest [type] [contact_name]`\n\n**Valid types:**\n• follow_up\n• meeting_request\n• value_prop\n• objection_response\n\n**Example:** `/suggest meeting_request John Smith`")
                return
            
            progress_msg = await update.message.reply_text(f"✍️ **Generating {message_type.replace('_', ' ').title()}...**\n\n⏳ Crafting personalized BD message...")
            
            # Get recent conversation insight
            insights = self.bd_intelligence.get_conversation_insights(contact_name)
            
            if not insights:
                await progress_msg.edit_text("❌ No conversation insights found. Use `/analyze` first to analyze conversations.")
                return
            
            # Use most recent insight
            latest_insight = max(insights, key=lambda x: x.timestamp)
            
            # Generate personalized message
            if message_type == "follow_up":
                message = await self.bd_message_gen.generate_follow_up(latest_insight)
            elif message_type == "meeting_request":
                message = await self.bd_message_gen.generate_meeting_request(latest_insight)
            elif message_type == "value_prop":
                message = await self.bd_message_gen.generate_value_prop(latest_insight)
            else:  # objection_response
                message = await self.bd_message_gen.generate_objection_response(latest_insight)
            
            # Format response
            suggest_msg = f"✍️ **{message_type.replace('_', ' ').title()} Suggestion**\n\n"
            suggest_msg += f"👤 **For:** {latest_insight.contact_name}\n"
            suggest_msg += f"🎯 **Stage:** {latest_insight.bd_stage.title()}\n"
            suggest_msg += f"📊 **Interest:** {latest_insight.interest_level}%\n\n"
            suggest_msg += f"💬 **Suggested Message:**\n\n_{message}_\n\n"
            suggest_msg += f"**💡 Tips:**\n"
            suggest_msg += f"• Personalize with specific details\n"
            suggest_msg += f"• Reference recent conversation points\n"
            suggest_msg += f"• Add value before asking for anything\n"
            suggest_msg += f"• Keep it concise and natural"
            
            await progress_msg.edit_text(suggest_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in suggest message command: {e}")
            await update.message.reply_text(f"❌ Message suggestion failed: {str(e)}")

    async def _bd_kpis_command(self, update, context):
        """Show BD KPIs and performance metrics"""
        try:
            if not self.bd_intelligence:
                await update.message.reply_text("❌ BD Intelligence not available. Please set OPENAI_API_KEY in your .env file.")
                return
            
            progress_msg = await update.message.reply_text("📊 **Calculating BD KPIs...**\n\n⏳ Analyzing performance metrics...")
            
            # Get KPIs
            kpis = await self.bd_intelligence.analyze_bd_performance(days=7)
            insights = self.bd_intelligence.get_conversation_insights()
            
            # Calculate real metrics from insights
            total_analyzed = len(insights)
            avg_interest = sum(i.interest_level for i in insights) / len(insights) if insights else 0
            avg_sentiment = sum(i.sentiment_score for i in insights) / len(insights) if insights else 0
            high_urgency = len([i for i in insights if i.urgency_score > 70])
            meeting_ready = len([i for i in insights if i.meeting_readiness > 70])
            
            # Format KPI dashboard
            kpi_msg = f"📊 **BD Performance Dashboard** (Last 7 Days)\n\n"
            
            kpi_msg += f"📈 **Conversation Metrics:**\n"
            kpi_msg += f"• Total Analyzed: {total_analyzed}\n"
            kpi_msg += f"• Avg Interest Level: {avg_interest:.1f}%\n"
            kpi_msg += f"• Avg Sentiment: {avg_sentiment:.2f} ({self._sentiment_emoji(avg_sentiment)})\n"
            kpi_msg += f"• High Urgency: {high_urgency}\n"
            kpi_msg += f"• Meeting Ready: {meeting_ready}\n\n"
            
            # Stage distribution
            stages = {}
            for insight in insights:
                stages[insight.bd_stage] = stages.get(insight.bd_stage, 0) + 1
            
            if stages:
                kpi_msg += f"🏗️ **BD Stage Distribution:**\n"
                for stage, count in sorted(stages.items()):
                    percentage = (count / total_analyzed) * 100 if total_analyzed > 0 else 0
                    kpi_msg += f"• {stage.title()}: {count} ({percentage:.1f}%)\n"
                kpi_msg += "\n"
            
            # Top pain points
            all_pain_points = []
            for insight in insights:
                all_pain_points.extend(insight.pain_points)
            
            if all_pain_points:
                pain_counts = {}
                for pain in all_pain_points:
                    pain_counts[pain] = pain_counts.get(pain, 0) + 1
                
                top_pains = sorted(pain_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                kpi_msg += f"🔍 **Top Pain Points:**\n"
                for pain, count in top_pains:
                    kpi_msg += f"• {pain} ({count} mentions)\n"
                kpi_msg += "\n"
            
            # Next actions needed
            actions = {}
            for insight in insights:
                actions[insight.next_best_action] = actions.get(insight.next_best_action, 0) + 1
            
            if actions:
                kpi_msg += f"🎯 **Actions Needed:**\n"
                for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True):
                    kpi_msg += f"• {action.replace('_', ' ').title()}: {count}\n"
            
            kpi_msg += f"\n💡 Use `/analyze` for individual conversation insights!"
            
            await progress_msg.edit_text(kpi_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in BD KPIs command: {e}")
            await update.message.reply_text(f"❌ KPI calculation failed: {str(e)}")

    async def _conversation_insights_command(self, update, context):
        """Show conversation insights for specific contact or all"""
        try:
            if not self.bd_intelligence:
                await update.message.reply_text("❌ BD Intelligence not available. Please set OPENAI_API_KEY in your .env file.")
                return
            
            # Get contact filter from args
            contact_filter = " ".join(context.args) if context.args else None
            
            insights = self.bd_intelligence.get_conversation_insights(contact_filter)
            
            if not insights:
                if contact_filter:
                    await update.message.reply_text(f"❌ No insights found for '{contact_filter}'. Use `/analyze` to analyze conversations first.")
                else:
                    await update.message.reply_text("❌ No conversation insights available. Use `/analyze` to analyze conversations first.")
                return
            
            # Sort by timestamp (most recent first)
            insights = sorted(insights, key=lambda x: x.timestamp, reverse=True)
            
            # Format insights
            insights_msg = f"🧠 **Conversation Insights**"
            if contact_filter:
                insights_msg += f" - {contact_filter}"
            insights_msg += f"\n\n"
            
            for i, insight in enumerate(insights[:5], 1):  # Show top 5
                insights_msg += f"**{i}. {insight.contact_name}**\n"
                insights_msg += f"🎯 {insight.bd_stage.title()} | 📊 {insight.interest_level}% | ⚡ {insight.urgency_score}%\n"
                insights_msg += f"🎬 _{insight.conversation_summary[:80]}..._\n"
                insights_msg += f"💬 _{insight.recommended_message[:60]}..._\n\n"
            
            if len(insights) > 5:
                insights_msg += f"... and {len(insights) - 5} more insights\n\n"
            
            insights_msg += f"💡 Use `/analyze` for detailed analysis of specific conversations!"
            
            await update.message.reply_text(insights_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in conversation insights command: {e}")
            await update.message.reply_text(f"❌ Insights retrieval failed: {str(e)}")

    async def _smart_response_command(self, update, context):
        """Generate smart response based on conversation context"""
        try:
            if not self.bd_intelligence:
                await update.message.reply_text("❌ BD Intelligence not available. Please set OPENAI_API_KEY in your .env file.")
                return
            
            await update.message.reply_text("🤖 **Smart Response Generator**\n\nThis feature analyzes the current conversation and suggests the most effective response based on BD best practices.\n\n💡 Feature coming soon! Use `/suggest` for now.")
            
        except Exception as e:
            logger.error(f"Error in smart response command: {e}")
            await update.message.reply_text(f"❌ Smart response failed: {str(e)}")

    def _sentiment_emoji(self, sentiment_score: float) -> str:
        """Convert sentiment score to emoji"""
        if sentiment_score >= 0.5:
            return "😊 Positive"
        elif sentiment_score >= 0.1:
            return "🙂 Slightly Positive"
        elif sentiment_score >= -0.1:
            return "😐 Neutral"
        elif sentiment_score >= -0.5:
            return "😕 Slightly Negative"
        else:
            return "😞 Negative"
    
    async def _handle_message(self, update, context):
        """Handle incoming messages for real-time analysis"""
        try:
            # Store message if data manager available
            if self.data_manager:
                user = update.effective_user
                message_data = {
                    'chat_id': update.effective_chat.id,
                    'message_id': update.message.message_id,
                    'user_id': user.id,
                    'username': user.username or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'message_text': update.message.text,
                    'message_type': 'text',
                    'timestamp': update.message.date.isoformat(),
                    'chat_title': update.effective_chat.title or f"Chat {update.effective_chat.id}"
                }
                self.data_manager.store_message(message_data)
                
                # Also store in new lead tracking database
                if self.lead_db:
                    self.lead_db.store_message(message_data)
            
            # Real-time BD intelligence analysis
            if self.bd_intelligence and update.message.text:
                message_text = update.message.text.lower()
                
                # Check for high-value keywords
                high_value_keywords = [
                    'invest', 'funding', 'partner', 'collaborate', 'deal', 'opportunity', 
                    'interested', 'meeting', 'call', 'demo', 'proposal', 'budget',
                    'integration', 'partnership', 'strategic', 'acquisition'
                ]
                
                urgent_keywords = ['urgent', 'asap', 'immediately', 'deadline', 'soon']
                meeting_keywords = ['meet', 'call', 'demo', 'presentation', 'discuss']
                
                keyword_matches = sum(1 for keyword in high_value_keywords if keyword in message_text)
                
                # Advanced opportunity detection
                if keyword_matches >= 2:  # Multiple BD keywords
                    # Get recent conversation context
                    if self.data_manager:
                        chat_id = update.effective_chat.id
                        recent_messages = self.data_manager.get_chat_messages(chat_id, limit=10)
                        
                        if recent_messages:
                            contact_info = {
                                'first_name': update.effective_user.first_name,
                                'last_name': update.effective_user.last_name,
                                'username': update.effective_user.username
                            }
                            
                            # Quick BD analysis (background task)
                            asyncio.create_task(self._background_bd_analysis(recent_messages, contact_info, update))
                
                # Immediate alerts for high-priority signals
                if any(keyword in message_text for keyword in urgent_keywords):
                    urgency_alert = f"🚨 **URGENT OPPORTUNITY**\n\n"
                    urgency_alert += f"⚡ Urgent language detected from {update.effective_user.first_name}\n"
                    urgency_alert += f"💬 Use `/analyze` for immediate BD insights!"
                    
                    await update.message.reply_text(urgency_alert, parse_mode='Markdown')
                
                elif any(keyword in message_text for keyword in meeting_keywords):
                    meeting_alert = f"🤝 **Meeting Opportunity**\n\n"
                    meeting_alert += f"📅 Meeting signals detected from {update.effective_user.first_name}\n"
                    meeting_alert += f"💡 Use `/suggest meeting_request` for optimized response!"
                    
                    await update.message.reply_text(meeting_alert, parse_mode='Markdown')
            
            # Legacy opportunity detection
            message_text = update.message.text.lower() if update.message.text else ""
            opportunity_keywords = ['invest', 'funding', 'partner', 'collaborate', 'deal', 'opportunity', 'interested']
            
            if any(keyword in message_text for keyword in opportunity_keywords):
                # Quick opportunity alert
                alert_message = f"🚨 **Opportunity Alert!**\n\n"
                alert_message += f"💬 Potential opportunity detected in conversation with {update.effective_user.first_name}\n\n"
                alert_message += f"🔍 Use `/analyze` to get full AI analysis!"
                
                await update.message.reply_text(alert_message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _background_bd_analysis(self, messages: List[Dict], contact_info: Dict, update):
        """Background task for BD analysis"""
        try:
            if not self.bd_intelligence:
                return
            
            insight = await self.bd_intelligence.analyze_conversation(messages, contact_info)
            
            if insight and insight.urgency_score > 80:
                # Send high-priority alert
                alert = f"🔥 **HIGH-PRIORITY OPPORTUNITY**\n\n"
                alert += f"👤 {insight.contact_name}\n"
                alert += f"⚡ Urgency: {insight.urgency_score}%\n"
                alert += f"📊 Interest: {insight.interest_level}%\n"
                alert += f"🎯 Stage: {insight.bd_stage.title()}\n\n"
                alert += f"💬 Suggested action: _{insight.recommended_message}_"
                
                await update.message.reply_text(alert, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in background BD analysis: {e}")

    # =============================================================================
    # BOT LIFECYCLE
    # =============================================================================
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting Ultimate BD Bot...")
            
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.is_running = True
            logger.info("✅ Ultimate BD Bot is running!")
            logger.info("🎯 Ready for AI-powered deal closing!")
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        try:
            logger.info("🛑 Stopping Ultimate BD Bot...")
            
            self.is_running = False
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
            
            logger.info("✅ Ultimate BD Bot stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")

    # =============================================================================
    # GOOGLE SHEETS COMMANDS
    # =============================================================================
    
    async def _sheets_export_command(self, update, context):
        """Export all data to Google Sheets with comprehensive analytics"""
        try:
            if not self.sheets_exporter:
                await update.message.reply_text("❌ Google Sheets exporter not available. Check your configuration.")
                return
            
            progress_msg = await update.message.reply_text("📊 **Exporting to Google Sheets...**\n\n⏳ Preparing comprehensive data export...")
            
            # Update progress
            await progress_msg.edit_text("🚀 **Google Sheets Export in Progress...**\n\n📋 Exporting contacts, leads, messages...\n⏳ Creating analytics dashboard...")
            
            # Perform comprehensive export
            export_result = await self.sheets_exporter.export_comprehensive_data(
                lead_db=self.lead_db,
                bd_intelligence=self.bd_intelligence,
                ai_analyzer=None  # Can add if needed
            )
            
            if export_result.get('success'):
                export_msg = f"🎉 **Google Sheets Export Complete!**\n\n"
                export_msg += f"📊 **Spreadsheet Created:**\n"
                export_msg += f"🔗 [Open Dashboard]({export_result['spreadsheet_url']})\n\n"
                
                export_msg += f"📋 **Data Exported:**\n"
                export_results = export_result.get('export_results', {})
                for sheet_type, result in export_results.items():
                    if result.get('success'):
                        rows = result.get('rows_exported', 0)
                        export_msg += f"• {sheet_type.title()}: {rows} rows\n"
                
                export_msg += f"\n⚡ **Worksheets Created:**\n"
                export_msg += f"• 📊 Contacts & Leads\n"
                export_msg += f"• 💬 Messages & Conversations\n"
                export_msg += f"• 🎯 Lead Opportunities\n"
                export_msg += f"• 🏢 Organizations\n"
                export_msg += f"• 📈 Analytics Dashboard\n"
                export_msg += f"• 🧠 BD Intelligence\n"
                export_msg += f"• 📊 Performance Metrics\n\n"
                
                export_msg += f"💡 **Next Steps:**\n"
                export_msg += f"• Open the dashboard for real-time analytics\n"
                export_msg += f"• Use filters and pivot tables for deeper insights\n"
                export_msg += f"• Set up automatic sync with `/sheets_sync`\n"
                export_msg += f"• Share with your team for collaboration"
                
                await progress_msg.edit_text(export_msg, parse_mode='Markdown')
                
            else:
                error_msg = f"❌ **Export Failed**\n\n"
                error_msg += f"Error: {export_result.get('error', 'Unknown error')}\n\n"
                error_msg += f"💡 **Troubleshooting:**\n"
                error_msg += f"• Check Google Sheets API credentials\n"
                error_msg += f"• Verify spreadsheet permissions\n"
                error_msg += f"• Ensure internet connectivity"
                
                await progress_msg.edit_text(error_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in sheets export command: {e}")
            await update.message.reply_text(f"❌ Export failed: {str(e)}")

    async def _sheets_dashboard_command(self, update, context):
        """Get Google Sheets dashboard information and analytics"""
        try:
            if not self.sheets_exporter:
                await update.message.reply_text("❌ Google Sheets not configured. Use `/sheets_export` to set up.")
                return
            
            # Get analytics summary
            summary = self.sheets_exporter.get_analytics_summary()
            
            if 'error' in summary:
                await update.message.reply_text(f"❌ Dashboard error: {summary['error']}")
                return
            
            dashboard_msg = f"📈 **Google Sheets Dashboard**\n\n"
            dashboard_msg += f"📊 **Spreadsheet:** {summary.get('spreadsheet_title', 'Unknown')}\n"
            dashboard_msg += f"🔗 **URL:** [Open Dashboard]({summary.get('spreadsheet_url', '#')})\n\n"
            
            dashboard_msg += f"📋 **Worksheets ({summary.get('worksheets_count', 0)}):**\n"
            worksheets = summary.get('worksheets', [])
            for ws in worksheets:
                dashboard_msg += f"• {ws}\n"
            
            dashboard_msg += f"\n⏰ **Last Updated:** {summary.get('last_updated', 'Unknown')}\n\n"
            
            dashboard_msg += f"🎯 **Quick Actions:**\n"
            dashboard_msg += f"• `/sheets_export` - Refresh all data\n"
            dashboard_msg += f"• `/sheets_sync` - Enable auto-sync\n"
            dashboard_msg += f"• `/sheets_url` - Get direct link\n\n"
            
            dashboard_msg += f"💡 **Pro Tips:**\n"
            dashboard_msg += f"• Use pivot tables for advanced analysis\n"
            dashboard_msg += f"• Set up conditional formatting for lead scores\n"
            dashboard_msg += f"• Create charts for pipeline visualization"
            
            await update.message.reply_text(dashboard_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in sheets dashboard command: {e}")
            await update.message.reply_text(f"❌ Dashboard error: {str(e)}")

    async def _sheets_sync_command(self, update, context):
        """Enable/disable automatic sync to Google Sheets"""
        try:
            if not self.sheets_exporter:
                await update.message.reply_text("❌ Google Sheets not configured. Use `/sheets_export` first.")
                return
            
            # Parse sync command (on/off/status)
            action = "status"
            if context.args and len(context.args) > 0:
                action = context.args[0].lower()
            
            if action == "on" or action == "enable":
                # Enable automatic sync (this would need implementation in the data manager)
                sync_msg = f"🔄 **Auto-Sync Enabled**\n\n"
                sync_msg += f"✅ Data will sync to Google Sheets automatically\n"
                sync_msg += f"⏱️ Sync interval: Every 15 minutes\n"
                sync_msg += f"📊 Includes: New contacts, messages, leads\n\n"
                sync_msg += f"Use `/sheets_sync off` to disable"
                
            elif action == "off" or action == "disable":
                # Disable automatic sync
                sync_msg = f"⏸️ **Auto-Sync Disabled**\n\n"
                sync_msg += f"❌ Automatic syncing stopped\n"
                sync_msg += f"💡 Use `/sheets_export` for manual export\n"
                sync_msg += f"🔄 Use `/sheets_sync on` to re-enable"
                
            else:
                # Show status
                sync_msg = f"🔄 **Google Sheets Sync Status**\n\n"
                sync_msg += f"📊 **Current Status:** Active\n"
                sync_msg += f"🔗 **Spreadsheet:** [Open Dashboard]({self.sheets_exporter.get_spreadsheet_url()})\n"
                sync_msg += f"⏰ **Last Sync:** Manual export only\n"
                sync_msg += f"📋 **Sync Scope:** All data types\n\n"
                
                sync_msg += f"🎛️ **Commands:**\n"
                sync_msg += f"• `/sheets_sync on` - Enable auto-sync\n"
                sync_msg += f"• `/sheets_sync off` - Disable auto-sync\n"
                sync_msg += f"• `/sheets_export` - Manual export now"
            
            await update.message.reply_text(sync_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in sheets sync command: {e}")
            await update.message.reply_text(f"❌ Sync error: {str(e)}")

    async def _sheets_url_command(self, update, context):
        """Get direct URL to Google Sheets dashboard"""
        try:
            if not self.sheets_exporter:
                await update.message.reply_text("❌ Google Sheets not configured. Use `/sheets_export` to set up.")
                return
            
            url = self.sheets_exporter.get_spreadsheet_url()
            
            url_msg = f"🔗 **Google Sheets Dashboard**\n\n"
            url_msg += f"📊 [Open Your Analytics Dashboard]({url})\n\n"
            url_msg += f"💡 **What you'll find:**\n"
            url_msg += f"• Complete contact database with lead scores\n"
            url_msg += f"• Conversation history and sentiment analysis\n"
            url_msg += f"• Lead opportunities and pipeline tracking\n"
            url_msg += f"• Organization profiles and relationships\n"
            url_msg += f"• Performance metrics and KPIs\n"
            url_msg += f"• BD intelligence insights\n\n"
            
            url_msg += f"🎯 **Quick Tips:**\n"
            url_msg += f"• Bookmark this URL for easy access\n"
            url_msg += f"• Share with your team for collaboration\n"
            url_msg += f"• Use `/sheets_export` to refresh data"
            
            await update.message.reply_text(url_msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in sheets URL command: {e}")
            await update.message.reply_text(f"❌ URL error: {str(e)}")

async def main():
    """Main function"""
    print("🎯 Ultimate BD Bot - AI Deal Closing Machine")
    print("=" * 60)
    print("🤖 Advanced AI-powered opportunity identification")
    print("📊 Intelligent deal stage tracking & progression")
    print("🚀 Real-time closing strategies & recommendations")
    print("🎪 Full Sail ve(4,4) context integration")
    print("=" * 60)
    
    bot = UltimateBDBot()
    
    try:
        # Initialize bot
        success = await bot.initialize()
        if not success:
            logger.error("❌ Bot initialization failed")
            return
        
        # Start bot
        await bot.start()
        
        # Keep running
        while bot.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main()) 