#!/usr/bin/env python3
"""
Real Google Sheets Exporter
===========================
Comprehensive Google Sheets integration for exporting:
- Telegram conversation data
- Lead tracking database
- Business intelligence insights
- Performance analytics
- Automated dashboard creation
"""

import os
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import pandas as pd

# Google Sheets integration
try:
    import gspread
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

logger = logging.getLogger(__name__)

class RealGoogleSheetsExporter:
    """Real Google Sheets integration with full API access"""
    
    def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
        self.credentials_path = credentials_path or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "google_service_account.json")
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SPREADSHEET_ID")
        
        self.sheets_client = None
        self.sheets_service = None
        self.spreadsheet = None
        self.worksheets = {}
        
        self._init_google_sheets()
    
    def _init_google_sheets(self):
        """Initialize Google Sheets API client"""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.error("❌ Google Sheets packages not available. Install: pip install gspread google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False
        
        try:
            # Check credentials file exists
            if not os.path.exists(self.credentials_path):
                logger.error(f"❌ Google service account file not found: {self.credentials_path}")
                return False
            
            # Load credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            
            # Initialize gspread client
            self.sheets_client = gspread.authorize(credentials)
            
            # Initialize Google Sheets API service
            self.sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # Open or create spreadsheet
            if self.spreadsheet_id:
                try:
                    self.spreadsheet = self.sheets_client.open_by_key(self.spreadsheet_id)
                    logger.info(f"✅ Connected to existing spreadsheet: {self.spreadsheet.title}")
                except Exception as e:
                    logger.error(f"❌ Could not open spreadsheet {self.spreadsheet_id}: {e}")
                    return False
            else:
                # Create new spreadsheet
                self.spreadsheet = self.sheets_client.create("Telegram BD Analytics Dashboard")
                self.spreadsheet_id = self.spreadsheet.id
                logger.info(f"✅ Created new spreadsheet: {self.spreadsheet.title} ({self.spreadsheet_id})")
            
            logger.info("✅ Google Sheets integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google Sheets initialization failed: {e}")
            return False
    
    async def export_comprehensive_data(self, lead_db, bd_intelligence=None, ai_analyzer=None) -> Dict[str, Any]:
        """Export all data to Google Sheets with comprehensive analysis"""
        if not self.sheets_client:
            logger.error("❌ Google Sheets not initialized")
            return {"success": False, "error": "Google Sheets not initialized"}
        
        try:
            logger.info("🚀 Starting comprehensive data export to Google Sheets...")
            
            # Get all data from database
            dataframes = lead_db.export_to_dataframes() if lead_db else {}
            
            # Get BD intelligence data
            bd_data = bd_intelligence.export_bd_intelligence() if bd_intelligence else {}
            
            export_results = {}
            
            # 1. Export Contacts with enhanced data
            if 'contacts' in dataframes and not dataframes['contacts'].empty:
                contacts_result = await self._export_contacts_sheet(dataframes['contacts'])
                export_results['contacts'] = contacts_result
            
            # 2. Export Messages/Conversations
            if 'interactions' in dataframes and not dataframes['interactions'].empty:
                messages_result = await self._export_messages_sheet(dataframes['interactions'])
                export_results['messages'] = messages_result
            
            # 3. Export Leads/Opportunities
            if 'leads' in dataframes and not dataframes['leads'].empty:
                leads_result = await self._export_leads_sheet(dataframes['leads'])
                export_results['leads'] = leads_result
            
            # 4. Export Organizations
            if 'organizations' in dataframes and not dataframes['organizations'].empty:
                orgs_result = await self._export_organizations_sheet(dataframes['organizations'])
                export_results['organizations'] = orgs_result
            
            # 5. Create Analytics Dashboard
            dashboard_result = await self._create_analytics_dashboard(dataframes, bd_data)
            export_results['dashboard'] = dashboard_result
            
            # 6. Create BD Intelligence Sheet
            if bd_data:
                bd_result = await self._export_bd_intelligence_sheet(bd_data)
                export_results['bd_intelligence'] = bd_result
            
            # 7. Create Performance Metrics
            metrics_result = await self._create_performance_metrics_sheet(dataframes)
            export_results['metrics'] = metrics_result
            
            logger.info("✅ Comprehensive data export completed successfully")
            
            return {
                "success": True,
                "spreadsheet_id": self.spreadsheet_id,
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}",
                "worksheets_created": len(export_results),
                "export_results": export_results,
                "export_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive export failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _export_contacts_sheet(self, contacts_df: pd.DataFrame) -> Dict[str, Any]:
        """Export contacts with lead scoring and analytics"""
        try:
            worksheet_name = "📊 Contacts & Leads"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            # Prepare enhanced contacts data
            export_data = []
            
            # Header row with formatting
            headers = [
                "Contact ID", "Full Name", "Username", "Organization", 
                "Contact Type", "Lead Status", "Lead Score", "Estimated Value",
                "Probability %", "Days Since Contact", "Next Follow-up",
                "Phone", "Email", "Notes", "Last Interaction", "Created Date"
            ]
            export_data.append(headers)
            
            # Process each contact
            for _, contact in contacts_df.iterrows():
                full_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                if not full_name:
                    full_name = contact.get('username', 'Unknown')
                
                # Calculate days since contact
                last_interaction = contact.get('last_interaction')
                days_since = ""
                if last_interaction:
                    try:
                        last_date = pd.to_datetime(last_interaction)
                        days_since = (datetime.now() - last_date).days
                    except:
                        pass
                
                row = [
                    contact.get('contact_id', ''),
                    full_name,
                    contact.get('username', ''),
                    contact.get('organization_name', ''),
                    contact.get('contact_type', '').title(),
                    contact.get('lead_status', '').title(),
                    contact.get('lead_score', 0),
                    contact.get('estimated_value', 0),
                    contact.get('probability', 0),
                    days_since,
                    contact.get('next_follow_up', ''),
                    contact.get('phone', ''),
                    contact.get('email', ''),
                    contact.get('notes', ''),
                    contact.get('last_interaction', ''),
                    contact.get('created_at', '')
                ]
                export_data.append(row)
            
            # Clear and update worksheet
            worksheet.clear()
            worksheet.update('A1', export_data)
            
            # Apply formatting
            await self._format_contacts_sheet(worksheet, len(export_data))
            
            logger.info(f"✅ Exported {len(contacts_df)} contacts to '{worksheet_name}'")
            
            return {
                "success": True,
                "worksheet": worksheet_name,
                "rows_exported": len(contacts_df),
                "url": f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}#gid={worksheet.id}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting contacts sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _export_messages_sheet(self, interactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Export conversation messages and interactions"""
        try:
            worksheet_name = "💬 Messages & Conversations"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            # Prepare messages data
            export_data = []
            
            headers = [
                "Date", "Contact", "Chat Title", "Message Preview", 
                "Interaction Type", "Sentiment", "BD Stage", "Key Topics",
                "Opportunities Identified", "Follow-up Required", "Chat ID", "Contact ID"
            ]
            export_data.append(headers)
            
            # Process interactions (limit to recent 1000 for performance)
            recent_interactions = interactions_df.head(1000)
            
            for _, interaction in recent_interactions.iterrows():
                contact_name = f"{interaction.get('first_name', '')} {interaction.get('last_name', '')}".strip()
                if not contact_name:
                    contact_name = interaction.get('username', 'Unknown')
                
                # Truncate message preview
                message_preview = str(interaction.get('interaction_notes', ''))[:100]
                if len(message_preview) >= 100:
                    message_preview += "..."
                
                row = [
                    interaction.get('interaction_date', ''),
                    contact_name,
                    interaction.get('chat_title', ''),
                    message_preview,
                    interaction.get('interaction_type', '').title(),
                    interaction.get('sentiment_score', ''),
                    interaction.get('bd_stage', '').title(),
                    interaction.get('key_topics', ''),
                    interaction.get('opportunities', ''),
                    interaction.get('follow_up_required', ''),
                    interaction.get('chat_id', ''),
                    interaction.get('contact_id', '')
                ]
                export_data.append(row)
            
            # Update worksheet
            worksheet.clear()
            worksheet.update('A1', export_data)
            
            # Apply formatting
            await self._format_messages_sheet(worksheet, len(export_data))
            
            logger.info(f"✅ Exported {len(recent_interactions)} messages to '{worksheet_name}'")
            
            return {
                "success": True,
                "worksheet": worksheet_name,
                "rows_exported": len(recent_interactions),
                "url": f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}#gid={worksheet.id}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting messages sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _export_leads_sheet(self, leads_df: pd.DataFrame) -> Dict[str, Any]:
        """Export lead opportunities with deal tracking"""
        try:
            worksheet_name = "🎯 Lead Opportunities"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            export_data = []
            
            headers = [
                "Lead ID", "Contact Name", "Organization", "Lead Type",
                "Deal Stage", "Estimated Value", "Probability %", "Priority",
                "Created Date", "Last Update", "Next Action", "Close Date Target",
                "Competitive Notes", "Decision Makers", "Budget Confirmed", "Timeline"
            ]
            export_data.append(headers)
            
            for _, lead in leads_df.iterrows():
                contact_name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
                if not contact_name:
                    contact_name = lead.get('username', 'Unknown')
                
                row = [
                    lead.get('lead_id', ''),
                    contact_name,
                    lead.get('organization_name', ''),
                    lead.get('lead_type', '').title(),
                    lead.get('lead_stage', '').title(),
                    lead.get('estimated_value', 0),
                    lead.get('probability', 0),
                    lead.get('priority', '').title(),
                    lead.get('created_at', ''),
                    lead.get('updated_at', ''),
                    lead.get('next_action', ''),
                    lead.get('target_close_date', ''),
                    lead.get('competitive_notes', ''),
                    lead.get('decision_makers', ''),
                    lead.get('budget_confirmed', ''),
                    lead.get('timeline', '')
                ]
                export_data.append(row)
            
            worksheet.clear()
            worksheet.update('A1', export_data)
            
            await self._format_leads_sheet(worksheet, len(export_data))
            
            logger.info(f"✅ Exported {len(leads_df)} leads to '{worksheet_name}'")
            
            return {
                "success": True,
                "worksheet": worksheet_name,
                "rows_exported": len(leads_df)
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting leads sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _export_organizations_sheet(self, orgs_df: pd.DataFrame) -> Dict[str, Any]:
        """Export organizations and companies"""
        try:
            worksheet_name = "🏢 Organizations"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            export_data = []
            
            headers = [
                "Organization ID", "Company Name", "Industry", "Organization Type",
                "Size", "Location", "Website", "Contact Count", "Total Pipeline Value",
                "Key Decision Makers", "Relationship Status", "Last Interaction",
                "Notes", "Created Date"
            ]
            export_data.append(headers)
            
            for _, org in orgs_df.iterrows():
                row = [
                    org.get('organization_id', ''),
                    org.get('name', ''),
                    org.get('industry', ''),
                    org.get('organization_type', '').title(),
                    org.get('size', ''),
                    org.get('location', ''),
                    org.get('website', ''),
                    org.get('contact_count', 0),
                    org.get('pipeline_value', 0),
                    org.get('key_contacts', ''),
                    org.get('relationship_status', '').title(),
                    org.get('last_interaction', ''),
                    org.get('notes', ''),
                    org.get('created_at', '')
                ]
                export_data.append(row)
            
            worksheet.clear()
            worksheet.update('A1', export_data)
            
            await self._format_organizations_sheet(worksheet, len(export_data))
            
            logger.info(f"✅ Exported {len(orgs_df)} organizations to '{worksheet_name}'")
            
            return {"success": True, "worksheet": worksheet_name, "rows_exported": len(orgs_df)}
            
        except Exception as e:
            logger.error(f"❌ Error exporting organizations sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_analytics_dashboard(self, dataframes: Dict[str, pd.DataFrame], bd_data: Dict) -> Dict[str, Any]:
        """Create comprehensive analytics dashboard"""
        try:
            worksheet_name = "📈 Analytics Dashboard"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            # Calculate key metrics
            contacts_df = dataframes.get('contacts', pd.DataFrame())
            leads_df = dataframes.get('leads', pd.DataFrame())
            interactions_df = dataframes.get('interactions', pd.DataFrame())
            
            # Dashboard data structure
            dashboard_data = []
            
            # Title
            dashboard_data.append(["🎯 TELEGRAM BD ANALYTICS DASHBOARD", "", "", ""])
            dashboard_data.append([f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "", ""])
            dashboard_data.append(["", "", "", ""])
            
            # Key Performance Indicators
            dashboard_data.append(["📊 KEY PERFORMANCE INDICATORS", "", "", ""])
            dashboard_data.append(["Metric", "Value", "Target", "Status"])
            
            total_contacts = len(contacts_df) if not contacts_df.empty else 0
            total_leads = len(leads_df) if not leads_df.empty else 0
            pipeline_value = contacts_df['estimated_value'].sum() if not contacts_df.empty and 'estimated_value' in contacts_df.columns else 0
            avg_lead_score = contacts_df['lead_score'].mean() if not contacts_df.empty and 'lead_score' in contacts_df.columns else 0
            
            hot_leads = len(contacts_df[contacts_df['lead_score'] >= 70]) if not contacts_df.empty and 'lead_score' in contacts_df.columns else 0
            
            dashboard_data.append(["Total Contacts", total_contacts, "100+", "✅" if total_contacts >= 100 else "⏳"])
            dashboard_data.append(["Active Leads", total_leads, "50+", "✅" if total_leads >= 50 else "⏳"])
            dashboard_data.append(["Pipeline Value", f"${pipeline_value:,.0f}", "$1M+", "✅" if pipeline_value >= 1000000 else "⏳"])
            dashboard_data.append(["Avg Lead Score", f"{avg_lead_score:.1f}", "60+", "✅" if avg_lead_score >= 60 else "⏳"])
            dashboard_data.append(["Hot Leads (70+)", hot_leads, "20+", "✅" if hot_leads >= 20 else "⏳"])
            
            dashboard_data.append(["", "", "", ""])
            
            # Lead Distribution
            dashboard_data.append(["🎯 LEAD DISTRIBUTION", "", "", ""])
            dashboard_data.append(["Lead Status", "Count", "Percentage", ""])
            
            if not contacts_df.empty and 'lead_status' in contacts_df.columns:
                lead_distribution = contacts_df['lead_status'].value_counts()
                for status, count in lead_distribution.items():
                    percentage = (count / total_contacts * 100) if total_contacts > 0 else 0
                    dashboard_data.append([status.title(), count, f"{percentage:.1f}%", ""])
            
            dashboard_data.append(["", "", "", ""])
            
            # Recent Activity
            dashboard_data.append(["📅 RECENT ACTIVITY (Last 7 Days)", "", "", ""])
            dashboard_data.append(["Activity Type", "Count", "", ""])
            
            if not interactions_df.empty:
                recent_interactions = interactions_df[
                    pd.to_datetime(interactions_df['interaction_date']) >= 
                    (datetime.now() - timedelta(days=7))
                ] if 'interaction_date' in interactions_df.columns else pd.DataFrame()
                
                dashboard_data.append(["New Interactions", len(recent_interactions), "", ""])
                dashboard_data.append(["New Contacts", len(contacts_df[pd.to_datetime(contacts_df['created_at']) >= (datetime.now() - timedelta(days=7))]) if 'created_at' in contacts_df.columns else 0, "", ""])
                dashboard_data.append(["New Leads", len(leads_df[pd.to_datetime(leads_df['created_at']) >= (datetime.now() - timedelta(days=7))]) if 'created_at' in leads_df.columns else 0, "", ""])
            
            # Update worksheet
            worksheet.clear()
            worksheet.update('A1', dashboard_data)
            
            # Apply dashboard formatting
            await self._format_dashboard_sheet(worksheet, len(dashboard_data))
            
            logger.info(f"✅ Created analytics dashboard with {len(dashboard_data)} rows")
            
            return {"success": True, "worksheet": worksheet_name, "metrics_count": len(dashboard_data)}
            
        except Exception as e:
            logger.error(f"❌ Error creating analytics dashboard: {e}")
            return {"success": False, "error": str(e)}
    
    async def _export_bd_intelligence_sheet(self, bd_data: Dict) -> Dict[str, Any]:
        """Export BD intelligence insights"""
        try:
            worksheet_name = "🧠 BD Intelligence"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            export_data = []
            
            # Header
            export_data.append(["🧠 BUSINESS DEVELOPMENT INTELLIGENCE", "", "", ""])
            export_data.append([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "", ""])
            export_data.append(["", "", "", ""])
            
            # Conversation insights
            conversations = bd_data.get('conversations', [])
            if conversations:
                export_data.append(["📋 CONVERSATION INSIGHTS", "", "", ""])
                export_data.append(["Contact", "BD Stage", "Sentiment", "Opportunities"])
                
                for conv in conversations[:20]:  # Limit to top 20
                    export_data.append([
                        conv.get('contact_name', ''),
                        conv.get('bd_stage', ''),
                        conv.get('sentiment_score', ''),
                        conv.get('bd_opportunities', '')
                    ])
            
            export_data.append(["", "", "", ""])
            
            # BD Context
            bd_context = bd_data.get('bd_context', {})
            if bd_context:
                export_data.append(["🎯 BUSINESS CONTEXT", "", "", ""])
                for key, value in bd_context.items():
                    if isinstance(value, list):
                        value = "; ".join(str(v) for v in value[:3])  # Limit list items
                    export_data.append([key.replace('_', ' ').title(), str(value)[:200], "", ""])  # Limit length
            
            worksheet.clear()
            worksheet.update('A1', export_data)
            
            logger.info(f"✅ Exported BD intelligence data to '{worksheet_name}'")
            
            return {"success": True, "worksheet": worksheet_name}
            
        except Exception as e:
            logger.error(f"❌ Error exporting BD intelligence sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_performance_metrics_sheet(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Create performance metrics and KPIs sheet"""
        try:
            worksheet_name = "📊 Performance Metrics"
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            contacts_df = dataframes.get('contacts', pd.DataFrame())
            leads_df = dataframes.get('leads', pd.DataFrame())
            
            metrics_data = []
            
            # Title
            metrics_data.append(["📊 PERFORMANCE METRICS & KPIs", "", ""])
            metrics_data.append([f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", "", ""])
            metrics_data.append(["", "", ""])
            
            # Conversion Metrics
            metrics_data.append(["🎯 CONVERSION METRICS", "", ""])
            metrics_data.append(["Metric", "Value", "Formula"])
            
            if not contacts_df.empty:
                qualified_leads = len(contacts_df[contacts_df['lead_score'] >= 50]) if 'lead_score' in contacts_df.columns else 0
                hot_leads = len(contacts_df[contacts_df['lead_score'] >= 70]) if 'lead_score' in contacts_df.columns else 0
                
                conversion_rate = (qualified_leads / len(contacts_df) * 100) if len(contacts_df) > 0 else 0
                hot_lead_rate = (hot_leads / len(contacts_df) * 100) if len(contacts_df) > 0 else 0
                
                metrics_data.append(["Lead Conversion Rate", f"{conversion_rate:.1f}%", "Qualified Leads / Total Contacts"])
                metrics_data.append(["Hot Lead Rate", f"{hot_lead_rate:.1f}%", "Hot Leads (70+) / Total Contacts"])
                metrics_data.append(["Qualified Leads", qualified_leads, "Lead Score >= 50"])
                metrics_data.append(["Hot Leads", hot_leads, "Lead Score >= 70"])
            
            metrics_data.append(["", "", ""])
            
            # Pipeline Health
            metrics_data.append(["💰 PIPELINE HEALTH", "", ""])
            metrics_data.append(["Metric", "Value", "Target"])
            
            if not contacts_df.empty and 'estimated_value' in contacts_df.columns:
                total_pipeline = contacts_df['estimated_value'].sum()
                avg_deal_size = contacts_df['estimated_value'].mean()
                weighted_pipeline = (contacts_df['estimated_value'] * contacts_df['probability'] / 100).sum() if 'probability' in contacts_df.columns else 0
                
                metrics_data.append(["Total Pipeline Value", f"${total_pipeline:,.0f}", "$1,000,000"])
                metrics_data.append(["Average Deal Size", f"${avg_deal_size:,.0f}", "$50,000"])
                metrics_data.append(["Weighted Pipeline", f"${weighted_pipeline:,.0f}", "$500,000"])
            
            # Update worksheet
            worksheet.clear()
            worksheet.update('A1', metrics_data)
            
            await self._format_metrics_sheet(worksheet, len(metrics_data))
            
            logger.info(f"✅ Created performance metrics sheet")
            
            return {"success": True, "worksheet": worksheet_name}
            
        except Exception as e:
            logger.error(f"❌ Error creating performance metrics sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_or_create_worksheet(self, worksheet_name: str):
        """Get existing worksheet or create new one"""
        try:
            # Try to get existing worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                logger.info(f"📋 Using existing worksheet: {worksheet_name}")
                return worksheet
            except gspread.WorksheetNotFound:
                pass
            
            # Create new worksheet
            worksheet = self.spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=26
            )
            logger.info(f"✅ Created new worksheet: {worksheet_name}")
            return worksheet
            
        except Exception as e:
            logger.error(f"❌ Error creating worksheet {worksheet_name}: {e}")
            raise
    
    # Formatting methods
    async def _format_contacts_sheet(self, worksheet, row_count: int):
        """Apply formatting to contacts sheet"""
        try:
            # Header formatting
            worksheet.format('A1:P1', {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
            })
            
            # Freeze header row
            worksheet.freeze(rows=1)
            
            # Lead score conditional formatting
            if row_count > 1:
                worksheet.format(f'G2:G{row_count}', {
                    'numberFormat': {'type': 'NUMBER', 'pattern': '0.0'}
                })
        
        except Exception as e:
            logger.warning(f"⚠️ Formatting warning for contacts sheet: {e}")
    
    async def _format_messages_sheet(self, worksheet, row_count: int):
        """Apply formatting to messages sheet"""
        try:
            worksheet.format('A1:L1', {
                'backgroundColor': {'red': 0.8, 'green': 0.4, 'blue': 0.2},
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
            })
            worksheet.freeze(rows=1)
        except Exception as e:
            logger.warning(f"⚠️ Formatting warning for messages sheet: {e}")
    
    async def _format_leads_sheet(self, worksheet, row_count: int):
        """Apply formatting to leads sheet"""
        try:
            worksheet.format('A1:P1', {
                'backgroundColor': {'red': 0.2, 'green': 0.8, 'blue': 0.4},
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
            })
            worksheet.freeze(rows=1)
        except Exception as e:
            logger.warning(f"⚠️ Formatting warning for leads sheet: {e}")
    
    async def _format_organizations_sheet(self, worksheet, row_count: int):
        """Apply formatting to organizations sheet"""
        try:
            worksheet.format('A1:N1', {
                'backgroundColor': {'red': 0.4, 'green': 0.2, 'blue': 0.8},
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
            })
            worksheet.freeze(rows=1)
        except Exception as e:
            logger.warning(f"⚠️ Formatting warning for organizations sheet: {e}")
    
    async def _format_dashboard_sheet(self, worksheet, row_count: int):
        """Apply formatting to dashboard sheet"""
        try:
            # Title formatting
            worksheet.format('A1:D1', {
                'backgroundColor': {'red': 1, 'green': 0.8, 'blue': 0},
                'textFormat': {'bold': True, 'fontSize': 16}
            })
            
            # Section headers
            worksheet.format('A4:D4', {
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                'textFormat': {'bold': True}
            })
        except Exception as e:
            logger.warning(f"⚠️ Formatting warning for dashboard sheet: {e}")
    
    async def _format_metrics_sheet(self, worksheet, row_count: int):
        """Apply formatting to metrics sheet"""
        try:
            worksheet.format('A1:C1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
            })
        except Exception as e:
            logger.warning(f"⚠️ Formatting warning for metrics sheet: {e}")
    
    def get_spreadsheet_url(self) -> str:
        """Get the URL to the Google Spreadsheet"""
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of exported analytics"""
        if not self.spreadsheet:
            return {"error": "No spreadsheet available"}
        
        try:
            worksheets = self.spreadsheet.worksheets()
            return {
                "spreadsheet_title": self.spreadsheet.title,
                "spreadsheet_id": self.spreadsheet_id,
                "spreadsheet_url": self.get_spreadsheet_url(),
                "worksheets_count": len(worksheets),
                "worksheets": [ws.title for ws in worksheets],
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)} 