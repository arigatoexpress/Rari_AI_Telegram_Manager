#!/usr/bin/env python3
"""
AI Analytics Engine
==================
Enhanced standalone AI-powered analytics application with local database management.

Features:
- Local database as primary source of truth
- Google Sheets synchronization  
- AI-powered insights generation
- Automated reporting
- Performance metrics tracking
- Lead scoring and pipeline analysis

Usage:
    python ai_analytics_engine.py --analyze-all
    python ai_analytics_engine.py --export-sheets
    python ai_analytics_engine.py --generate-report
    python ai_analytics_engine.py --dashboard
"""

import os
import sys
import argparse
import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

# Enhanced core analytics imports
from core.local_database_manager import LocalDatabaseManager, get_local_db_manager
from core.sheets_sync_manager import SheetsyncManager, get_sheets_sync_manager
from core.lead_tracking_db import LeadTrackingDB
from core.real_google_sheets_exporter import RealGoogleSheetsExporter
from core.bd_intelligence import BDIntelligence
from core.ai_deal_analyzer import AIDealAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_analytics.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AIAnalyticsEngine:
    """Enhanced AI Analytics Engine with Local Database Management"""
    
    def __init__(self):
        # Enhanced database managers
        self.local_db = None
        self.sync_manager = None
        
        # Legacy components (for compatibility)
        self.lead_db = None
        self.sheets_exporter = None
        self.bd_intelligence = None
        self.ai_deal_analyzer = None
        
        # Configuration
        self.config = self._load_config()
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and config files"""
        # Try to load from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        config = {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'google_spreadsheet_id': os.getenv('GOOGLE_SPREADSHEET_ID'),
            'google_service_account': os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'google_service_account.json'),
            'database_path': 'data/telegram_manager.db',
            'local_database_path': 'data/local_bd_database.db',
            'reports_dir': 'reports',
            'exports_dir': 'exports'
        }
        
        # Ensure directories exist
        Path(config['reports_dir']).mkdir(exist_ok=True)
        Path(config['exports_dir']).mkdir(exist_ok=True)
        Path('data').mkdir(exist_ok=True)
        
        return config
    
    def _initialize_components(self):
        """Initialize all analytics components"""
        try:
            # Initialize enhanced local database (async, will be initialized when needed)
            # This replaces the old database system
            
            # Initialize legacy lead tracking database for compatibility
            self.lead_db = LeadTrackingDB()
            logger.info("✅ Lead tracking database initialized")
            
            # Initialize Google Sheets exporter
            if self.config['google_spreadsheet_id']:
                self.sheets_exporter = RealGoogleSheetsExporter(
                    credentials_path=self.config['google_service_account'],
                    spreadsheet_id=self.config['google_spreadsheet_id']
                )
                logger.info("✅ Google Sheets exporter initialized")
            else:
                logger.warning("⚠️ Google Sheets not configured")
            
            # Initialize BD Intelligence
            if self.config['openai_api_key']:
                self.bd_intelligence = BDIntelligence(
                    self.config['openai_api_key'], 
                    self.lead_db
                )
                logger.info("✅ BD Intelligence initialized")
                
                # Initialize AI Deal Analyzer
                self.ai_deal_analyzer = AIDealAnalyzer(self.config['openai_api_key'])
                logger.info("✅ AI Deal Analyzer initialized")
            else:
                logger.warning("⚠️ OpenAI API key not found - AI features disabled")
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
    
    async def check_configuration(self) -> Dict[str, Any]:
        """Check system configuration status"""
        config_status = {
            'openai_configured': bool(self.config.get('openai_api_key')),
            'google_sheets_configured': bool(self.config.get('google_spreadsheet_id')) and Path(self.config.get('google_service_account', '')).exists(),
            'database_available': Path(self.config.get('database_path', '')).exists() or Path(self.config.get('local_database_path', '')).exists(),
            'local_database_available': Path(self.config.get('local_database_path', '')).exists()
        }
        
        return config_status
    
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis using the enhanced local database system"""
        try:
            # Initialize local database manager if not already done
            if not self.local_db:
                self.local_db = await get_local_db_manager()
            
            # Get database statistics
            db_stats = await self.local_db.get_database_stats()
            
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'database_stats': db_stats,
                'analysis': {},
                'recommendations': [],
                'key_insights': [],
                'opportunities': []
            }
            
            # Process messages to create contacts if needed
            if db_stats.get('total_contacts', 0) == 0 and db_stats.get('total_messages', 0) > 0:
                logger.info("🔄 Creating contacts from imported messages...")
                contacts_created = await self.local_db._create_contacts_from_messages()
                logger.info(f"✅ Created {contacts_created} contacts from messages")
                
                # Create interactions from messages
                interactions_created = await self.local_db._create_interactions_from_messages()
                logger.info(f"✅ Created {interactions_created} interactions from messages")
                
                # Update stats
                db_stats = await self.local_db.get_database_stats()
                analysis_results['database_stats'] = db_stats
            
            # Generate AI insights if OpenAI is configured
            if self.config.get('openai_api_key') and db_stats.get('total_contacts', 0) > 0:
                analysis_results['analysis'] = await self._generate_ai_insights(db_stats)
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_recommendations_from_stats(db_stats)
            analysis_results['key_insights'] = self._generate_key_insights(db_stats)
            analysis_results['opportunities'] = self._identify_opportunities(db_stats)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e),
                'database_stats': {},
                'analysis': {},
                'recommendations': [],
                'key_insights': [],
                'opportunities': []
            }
    
    async def generate_executive_report(self) -> Dict[str, Any]:
        """Generate executive report with AI insights"""
        try:
            # Run analysis first
            analysis = await self.run_comprehensive_analysis()
            
            if not analysis.get('success'):
                return analysis
            
            # Create executive report
            report = {
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'report': {
                    'executive_summary': self._create_executive_summary(analysis),
                    'key_metrics': analysis.get('database_stats', {}),
                    'insights': analysis.get('key_insights', []),
                    'opportunities': analysis.get('opportunities', []),
                    'recommendations': analysis.get('recommendations', []),
                    'next_steps': self._generate_next_steps_from_analysis(analysis)
                }
            }
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = Path(self.config['reports_dir']) / f"executive_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Generate markdown version
            markdown_file = Path(self.config['reports_dir']) / f"executive_report_{timestamp}.md"
            markdown_content = self._generate_markdown_report(report['report'])
            
            with open(markdown_file, 'w') as f:
                f.write(markdown_content)
            
            report['output_file'] = str(report_file)
            report['markdown_file'] = str(markdown_file)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Executive report generation failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def _create_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """Create executive summary from analysis"""
        stats = analysis.get('database_stats', {})
        
        total_contacts = stats.get('total_contacts', 0)
        total_interactions = stats.get('total_interactions', 0)
        hot_leads = stats.get('hot_leads', 0)
        pipeline_value = stats.get('total_pipeline_value', 0)
        
        summary = f"""
        Business Development Analytics Summary
        
        Our database contains {total_contacts:,} contacts with {total_interactions:,} recorded interactions.
        We have identified {hot_leads} high-potential leads with a total pipeline value of ${pipeline_value:,.2f}.
        
        The system has successfully processed and analyzed all available data to provide actionable insights
        for business development activities.
        """.strip()
        
        return summary
    
    def _generate_ai_insights(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights (placeholder for now)"""
        return {
            'lead_quality_score': min(100, (stats.get('avg_lead_score', 0) * 2)),
            'engagement_rate': min(100, (stats.get('interactions_last_7_days', 0) / max(1, stats.get('total_contacts', 1)) * 100)),
            'pipeline_health': 'good' if stats.get('hot_leads', 0) > 0 else 'needs_attention'
        }
    
    def _generate_recommendations_from_stats(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on database statistics"""
        recommendations = []
        
        if stats.get('total_contacts', 0) == 0:
            recommendations.append("Import contact data to begin analysis")
        
        if stats.get('follow_ups_needed', 0) > 0:
            recommendations.append(f"Follow up with {stats.get('follow_ups_needed', 0)} contacts")
        
        if stats.get('hot_leads', 0) == 0:
            recommendations.append("Focus on lead qualification to identify hot prospects")
        
        if stats.get('interactions_last_7_days', 0) < stats.get('total_contacts', 0) * 0.1:
            recommendations.append("Increase engagement frequency with existing contacts")
        
        return recommendations
    
    def _generate_key_insights(self, stats: Dict[str, Any]) -> List[str]:
        """Generate key insights from statistics"""
        insights = []
        
        total_contacts = stats.get('total_contacts', 0)
        if total_contacts > 0:
            insights.append(f"Database contains {total_contacts:,} contacts across various industries")
        
        avg_score = stats.get('avg_lead_score', 0)
        if avg_score > 0:
            insights.append(f"Average lead score is {avg_score:.1f}, indicating overall lead quality")
        
        pipeline_value = stats.get('total_pipeline_value', 0)
        if pipeline_value > 0:
            insights.append(f"Total pipeline value of ${pipeline_value:,.2f} across active opportunities")
        
        return insights
    
    def _identify_opportunities(self, stats: Dict[str, Any]) -> List[str]:
        """Identify business opportunities from statistics"""
        opportunities = []
        
        hot_leads = stats.get('hot_leads', 0)
        if hot_leads > 0:
            opportunities.append(f"{hot_leads} high-scoring leads ready for immediate follow-up")
        
        messages_count = stats.get('total_messages', 0)
        contacts_count = stats.get('total_contacts', 0)
        if messages_count > contacts_count * 10:
            opportunities.append("Rich communication history available for deeper analysis")
        
        if stats.get('sync_pending', 0) > 0:
            opportunities.append("Data ready for Google Sheets synchronization and team collaboration")
        
        return opportunities
    
    def _generate_next_steps_from_analysis(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps from analysis"""
        next_steps = []
        
        stats = analysis.get('database_stats', {})
        
        if stats.get('total_contacts', 0) > 0:
            next_steps.append("Review hot leads and schedule follow-up activities")
        
        if stats.get('sync_pending', 0) > 0:
            next_steps.append("Sync data to Google Sheets for team collaboration")
        
        next_steps.append("Monitor lead scores and update contact priorities")
        next_steps.append("Generate weekly analytics reports for stakeholders")
        
        return next_steps
    
    async def analyze_all_data(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of all available data"""
        logger.info("🚀 Starting comprehensive data analysis...")
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'database_stats': {},
            'lead_analysis': {},
            'bd_intelligence': {},
            'deal_opportunities': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        try:
            # 1. Database Statistics
            if self.lead_db:
                analysis_results['database_stats'] = self.lead_db.get_dashboard_stats()
                logger.info("✅ Database statistics generated")
            
            # 2. Lead Analysis
            if self.lead_db:
                hot_leads = self.lead_db.get_hot_leads(limit=50)
                follow_ups = self.lead_db.get_follow_up_needed(days_threshold=3)
                
                analysis_results['lead_analysis'] = {
                    'hot_leads_count': len(hot_leads),
                    'follow_ups_needed': len(follow_ups),
                    'hot_leads': [self._format_lead_summary(lead) for lead in hot_leads[:10]],
                    'urgent_follow_ups': [self._format_lead_summary(lead) for lead in follow_ups[:10]]
                }
                logger.info("✅ Lead analysis completed")
            
            # 3. BD Intelligence Analysis
            if self.bd_intelligence:
                bd_brief = await self.bd_intelligence.get_daily_bd_brief()
                analysis_results['bd_intelligence'] = bd_brief
                logger.info("✅ BD Intelligence analysis completed")
            
            # 4. Deal Opportunities Analysis
            if self.ai_deal_analyzer and self.lead_db:
                # Get recent interactions for deal analysis
                interactions = self.lead_db.get_recent_interactions(days=30)
                if interactions:
                    # Convert to format expected by AI analyzer
                    messages = [self._interaction_to_message(interaction) for interaction in interactions]
                    opportunities = await self.ai_deal_analyzer.analyze_conversation_for_deals(messages)
                    
                    analysis_results['deal_opportunities'] = {
                        'total_opportunities': len(opportunities),
                        'high_probability': len([o for o in opportunities if o.probability > 70]),
                        'total_value': sum(o.estimated_value for o in opportunities),
                        'top_opportunities': [self._format_opportunity(opp) for opp in opportunities[:10]]
                    }
                    logger.info("✅ Deal opportunities analysis completed")
            
            # 5. Performance Metrics
            analysis_results['performance_metrics'] = self._calculate_performance_metrics()
            logger.info("✅ Performance metrics calculated")
            
            # 6. Generate Recommendations
            analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
            logger.info("✅ Recommendations generated")
            
            logger.info("🎉 Comprehensive analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            analysis_results['error'] = str(e)
            return analysis_results
    
    async def export_to_google_sheets(self) -> Dict[str, Any]:
        """Export all data to Google Sheets with comprehensive analytics"""
        if not self.sheets_exporter:
            return {"success": False, "error": "Google Sheets not configured"}
        
        logger.info("📊 Starting Google Sheets export...")
        
        try:
            export_result = await self.sheets_exporter.export_comprehensive_data(
                lead_db=self.lead_db,
                bd_intelligence=self.bd_intelligence,
                ai_analyzer=self.ai_deal_analyzer
            )
            
            if export_result.get('success'):
                logger.info("✅ Google Sheets export completed successfully")
                logger.info(f"📊 Spreadsheet URL: {export_result['spreadsheet_url']}")
            else:
                logger.error(f"❌ Google Sheets export failed: {export_result.get('error')}")
            
            return export_result
            
        except Exception as e:
            logger.error(f"❌ Google Sheets export error: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive business intelligence report"""
        logger.info("📋 Generating comprehensive report...")
        
        # Perform analysis
        analysis = await self.analyze_all_data()
        
        # Generate report
        report = {
            'report_id': f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'executive_summary': self._generate_executive_summary(analysis),
            'key_metrics': self._extract_key_metrics(analysis),
            'detailed_analysis': analysis,
            'action_items': self._generate_action_items(analysis),
            'next_steps': self._generate_next_steps(analysis)
        }
        
        # Save report
        report_path = Path(self.config['reports_dir']) / f"{report['report_id']}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate markdown report
        markdown_report = self._generate_markdown_report(report)
        markdown_path = report_path.with_suffix('.md')
        with open(markdown_path, 'w') as f:
            f.write(markdown_report)
        
        logger.info(f"✅ Report saved to: {report_path}")
        logger.info(f"📝 Markdown report: {markdown_path}")
        
        return report
    
    def create_dashboard_summary(self) -> str:
        """Create a quick dashboard summary for CLI display"""
        if not self.lead_db:
            return "❌ Database not available"
        
        stats = self.lead_db.get_dashboard_stats()
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    AI ANALYTICS DASHBOARD                        ║
╠══════════════════════════════════════════════════════════════════╣
║ 📊 OVERVIEW                                                     ║
║   • Total Contacts: {stats.get('total_contacts', 0):,}                                        ║
║   • Total Leads: {stats.get('total_leads', 0):,}                                           ║
║   • Pipeline Value: ${stats.get('pipeline_value', 0):,.0f}                               ║
║   • Hot Leads (70+): {stats.get('hot_leads', 0):,}                                       ║
║                                                                  ║
║ 🎯 LEAD PERFORMANCE                                             ║
║   • Average Lead Score: {stats.get('avg_lead_score', 0):.1f}/100                                  ║
║   • Conversion Rate: {(stats.get('qualified_leads', 0) / max(stats.get('total_contacts', 1), 1) * 100):.1f}%                                    ║
║   • Follow-ups Needed: {stats.get('follow_ups_needed', 0):,}                                  ║
║                                                                  ║
║ 📈 RECENT ACTIVITY (7 days)                                    ║
║   • New Messages: {stats.get('messages_last_7_days', 0):,}                                     ║
║   • New Interactions: {stats.get('interactions_last_7_days', 0):,}                                ║
║                                                                  ║
║ 🔗 GOOGLE SHEETS                                               ║
║   • Status: {'✅ Connected' if self.sheets_exporter else '❌ Not configured'}                                          ║
║   • AI Analysis: {'✅ Enabled' if self.bd_intelligence else '❌ Disabled'}                                       ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        return dashboard.strip()
    
    # Helper methods
    def _format_lead_summary(self, lead: Dict) -> Dict[str, Any]:
        """Format lead data for summary display"""
        return {
            'name': f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip() or lead.get('username', 'Unknown'),
            'organization': lead.get('organization_name', ''),
            'lead_score': lead.get('lead_score', 0),
            'estimated_value': lead.get('estimated_value', 0),
            'last_contact': lead.get('last_interaction', ''),
            'status': lead.get('lead_status', '')
        }
    
    def _interaction_to_message(self, interaction: Dict) -> Dict[str, Any]:
        """Convert database interaction to message format for AI analysis"""
        return {
            'id': interaction.get('interaction_id'),
            'chat_id': interaction.get('chat_id'),
            'user_id': interaction.get('contact_id'),
            'username': interaction.get('username'),
            'first_name': interaction.get('first_name'),
            'last_name': interaction.get('last_name'),
            'message_text': interaction.get('interaction_notes'),
            'timestamp': interaction.get('interaction_date'),
            'chat_title': interaction.get('chat_title', 'Direct Message')
        }
    
    def _format_opportunity(self, opp) -> Dict[str, Any]:
        """Format opportunity data for display"""
        return {
            'contact_name': opp.contact_name,
            'opportunity_type': opp.opportunity_type.value,
            'probability': opp.probability,
            'estimated_value': opp.estimated_value,
            'deal_stage': opp.deal_stage.value,
            'urgency': opp.urgency_level.value,
            'next_action': opp.next_action
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        if not self.lead_db:
            return {}
        
        stats = self.lead_db.get_dashboard_stats()
        
        return {
            'total_contacts': stats.get('total_contacts', 0),
            'qualified_leads': stats.get('qualified_leads', 0),
            'conversion_rate': (stats.get('qualified_leads', 0) / max(stats.get('total_contacts', 1), 1)) * 100,
            'pipeline_value': stats.get('pipeline_value', 0),
            'avg_deal_size': stats.get('pipeline_value', 0) / max(stats.get('total_leads', 1), 1),
            'hot_leads_percentage': (stats.get('hot_leads', 0) / max(stats.get('total_contacts', 1), 1)) * 100
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Lead scoring recommendations
        lead_analysis = analysis.get('lead_analysis', {})
        if lead_analysis.get('follow_ups_needed', 0) > 5:
            recommendations.append("🚨 High follow-up backlog: Prioritize reaching out to contacts not contacted in 3+ days")
        
        # Performance recommendations
        metrics = analysis.get('performance_metrics', {})
        if metrics.get('conversion_rate', 0) < 10:
            recommendations.append("📈 Low conversion rate: Focus on lead qualification and scoring accuracy")
        
        if metrics.get('hot_leads_percentage', 0) < 20:
            recommendations.append("🎯 Few hot leads: Increase outreach and engagement activities")
        
        # BD Intelligence recommendations
        bd_intel = analysis.get('bd_intelligence', {})
        if bd_intel.get('hot_conversations', 0) > 0:
            recommendations.append(f"🔥 {bd_intel.get('hot_conversations', 0)} hot conversations identified: Review for immediate action")
        
        return recommendations
    
    def _generate_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate executive summary of analysis"""
        metrics = analysis.get('performance_metrics', {})
        lead_analysis = analysis.get('lead_analysis', {})
        
        summary = f"""
Executive Summary - {datetime.now().strftime('%B %d, %Y')}

Pipeline Overview:
• Total contacts in database: {metrics.get('total_contacts', 0):,}
• Active leads: {lead_analysis.get('hot_leads_count', 0):,}
• Pipeline value: ${metrics.get('pipeline_value', 0):,.0f}
• Conversion rate: {metrics.get('conversion_rate', 0):.1f}%

Key Insights:
• {lead_analysis.get('follow_ups_needed', 0)} contacts require follow-up
• Average deal size: ${metrics.get('avg_deal_size', 0):,.0f}
• Hot leads percentage: {metrics.get('hot_leads_percentage', 0):.1f}%

Immediate Actions Required:
• Review hot leads for closing opportunities
• Execute follow-up plan for pending contacts
• Analyze conversion bottlenecks
        """.strip()
        
        return summary
    
    def _extract_key_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for quick reference"""
        return {
            'total_contacts': analysis.get('performance_metrics', {}).get('total_contacts', 0),
            'hot_leads': analysis.get('lead_analysis', {}).get('hot_leads_count', 0),
            'pipeline_value': analysis.get('performance_metrics', {}).get('pipeline_value', 0),
            'conversion_rate': analysis.get('performance_metrics', {}).get('conversion_rate', 0),
            'follow_ups_needed': analysis.get('lead_analysis', {}).get('follow_ups_needed', 0)
        }
    
    def _generate_action_items(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific action items"""
        actions = []
        
        lead_analysis = analysis.get('lead_analysis', {})
        
        # Follow-up actions
        if lead_analysis.get('urgent_follow_ups'):
            actions.append("📞 Contact urgent follow-ups within 24 hours")
        
        # Hot leads actions
        if lead_analysis.get('hot_leads'):
            actions.append("🔥 Schedule meetings with hot leads this week")
        
        # Deal opportunities
        deal_opps = analysis.get('deal_opportunities', {})
        if deal_opps.get('high_probability', 0) > 0:
            actions.append(f"💰 Focus on {deal_opps.get('high_probability')} high-probability deals")
        
        return actions
    
    def _generate_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate strategic next steps"""
        return [
            "🔄 Schedule weekly analysis reviews",
            "📊 Set up automated Google Sheets sync",
            "🎯 Refine lead scoring criteria based on results",
            "📈 Track conversion improvements over time",
            "🤝 Share insights with team for collaborative action"
        ]
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown formatted report"""
        markdown = f"""# AI Analytics Report
*Generated: {report['generated_at']}*

## Executive Summary
{report['executive_summary']}

## Key Metrics
"""
        
        metrics = report['key_metrics']
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                if 'value' in metric or 'pipeline' in metric:
                    markdown += f"- **{metric.replace('_', ' ').title()}**: ${value:,.0f}\n"
                elif 'rate' in metric or 'percentage' in metric:
                    markdown += f"- **{metric.replace('_', ' ').title()}**: {value:.1f}%\n"
                else:
                    markdown += f"- **{metric.replace('_', ' ').title()}**: {value:,}\n"
            else:
                markdown += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
        
        markdown += f"""
## Action Items
"""
        for action in report['action_items']:
            markdown += f"- {action}\n"
        
        markdown += f"""
## Next Steps
"""
        for step in report['next_steps']:
            markdown += f"- {step}\n"
        
        return markdown

# CLI Interface
def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='AI Analytics Engine for Business Development')
    parser.add_argument('--analyze-all', action='store_true', help='Perform comprehensive analysis')
    parser.add_argument('--export-sheets', action='store_true', help='Export data to Google Sheets')
    parser.add_argument('--generate-report', action='store_true', help='Generate comprehensive report')
    parser.add_argument('--dashboard', action='store_true', help='Show dashboard summary')
    parser.add_argument('--config', action='store_true', help='Show configuration status')
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = AIAnalyticsEngine()
    
    if args.config:
        print("🔧 Configuration Status:")
        print(f"  • OpenAI API Key: {'✅ Configured' if engine.config['openai_api_key'] else '❌ Missing'}")
        print(f"  • Google Sheets: {'✅ Configured' if engine.config['google_spreadsheet_id'] else '❌ Missing'}")
        print(f"  • Database: {'✅ Available' if engine.lead_db else '❌ Not found'}")
        return
    
    if args.dashboard:
        print(engine.create_dashboard_summary())
        return
    
    # Async operations
    async def run_async_operations():
        if args.analyze_all:
            print("🚀 Starting comprehensive analysis...")
            analysis = await engine.analyze_all_data()
            print("✅ Analysis completed!")
            print(f"📊 Found {analysis.get('lead_analysis', {}).get('hot_leads_count', 0)} hot leads")
            print(f"💰 Pipeline value: ${analysis.get('performance_metrics', {}).get('pipeline_value', 0):,.0f}")
        
        if args.export_sheets:
            print("📊 Exporting to Google Sheets...")
            result = await engine.export_to_google_sheets()
            if result.get('success'):
                print("✅ Export successful!")
                print(f"🔗 Spreadsheet: {result['spreadsheet_url']}")
            else:
                print(f"❌ Export failed: {result.get('error')}")
        
        if args.generate_report:
            print("📋 Generating comprehensive report...")
            report = await engine.generate_comprehensive_report()
            print(f"✅ Report generated: {report['report_id']}")
            print(f"📁 Saved to: reports/{report['report_id']}.json")
            print(f"📝 Markdown: reports/{report['report_id']}.md")
    
    if args.analyze_all or args.export_sheets or args.generate_report:
        asyncio.run(run_async_operations())
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 