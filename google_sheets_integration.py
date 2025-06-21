#!/usr/bin/env python3
"""
Google Sheets Integration for Telegram Manager
==============================================
Comprehensive integration for business briefs, lead tracking, and message analytics.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class BusinessBrief:
    """Data structure for business briefs"""
    chat_title: str
    chat_type: str
    date: str
    executive_brief: str
    key_insights: str
    conversion_opportunities: str
    actionable_recommendations: str
    next_steps: str
    priority: str
    status: str

@dataclass
class LeadData:
    """Data structure for lead tracking"""
    chat_title: str
    contact_name: str
    company: str
    phone: str
    email: str
    source: str
    status: str
    last_contact: str
    next_follow_up: str
    notes: str

class GoogleSheetsManager:
    """Manages Google Sheets integration for business data"""
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.credentials_file = self._resolve_service_account_file()
        self.spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
        
        if not self.credentials_file or not self.spreadsheet_id:
            raise ValueError("Missing Google Sheets configuration in .env file")
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            
            # Create client
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            print("✅ Google Sheets client initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets: {e}")
            raise
    
    def _resolve_service_account_file(self) -> Optional[str]:
        """Find the correct service account file, fallback to common alternatives if needed."""
        env_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        candidates = [
            env_file,
            "google_service_account.json",
            "service_account.json"
        ]
        for fname in candidates:
            if fname and os.path.exists(fname):
                if fname != env_file and env_file:
                    # Copy fallback to env_file name for consistency
                    try:
                        import shutil
                        shutil.copy(fname, env_file)
                        print(f"[GoogleSheetsManager] Copied {fname} to {env_file} for compatibility.")
                        return env_file
                    except Exception as e:
                        print(f"[GoogleSheetsManager] Could not copy {fname} to {env_file}: {e}")
                        return fname
                return fname
        print("[GoogleSheetsManager] Service account file not found. Checked:", candidates)
        return None
    
    def create_business_briefs_sheet(self, sheet_name: str = "Business Briefs") -> gspread.Worksheet:
        """Create or get the business briefs worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=20
            )
            
            # Set up headers
            headers = [
                "Chat Title", "Chat Type", "Date", "Executive Brief", 
                "Key Insights", "Conversion Opportunities", 
                "Actionable Recommendations", "Next Steps", 
                "Priority", "Status", "Last Updated"
            ]
            worksheet.update('A1:K1', [headers])
            worksheet.format('A1:K1', {'textFormat': {'bold': True}})
        
        return worksheet
    
    def create_leads_sheet(self, sheet_name: str = "Lead Tracking") -> gspread.Worksheet:
        """Create or get the lead tracking worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=15
            )
            
            # Set up headers
            headers = [
                "Chat Title", "Contact Name", "Company", "Phone", "Email",
                "Source", "Status", "Last Contact", "Next Follow Up", 
                "Notes", "Created Date", "Last Updated"
            ]
            worksheet.update('A1:L1', [headers])
            worksheet.format('A1:L1', {'textFormat': {'bold': True}})
        
        return worksheet
    
    def create_message_analytics_sheet(self, sheet_name: str = "Message Analytics") -> gspread.Worksheet:
        """Create or get the message analytics worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=12
            )
            
            # Set up headers
            headers = [
                "Date", "Chat Title", "Total Messages", "Incoming Messages",
                "Outgoing Messages", "Response Time (avg)", "Keywords Found",
                "Sentiment", "Business Opportunities", "Follow-ups Required",
                "Notes", "Last Updated"
            ]
            worksheet.update('A1:L1', [headers])
            worksheet.format('A1:L1', {'textFormat': {'bold': True}})
        
        return worksheet
    
    def add_business_brief(self, brief: BusinessBrief) -> bool:
        """Add a business brief to the sheet"""
        try:
            worksheet = self.create_business_briefs_sheet()
            
            # Prepare row data
            row_data = [
                brief.chat_title,
                brief.chat_type,
                brief.date,
                brief.executive_brief,
                brief.key_insights,
                brief.conversion_opportunities,
                brief.actionable_recommendations,
                brief.next_steps,
                brief.priority,
                brief.status,
                datetime.now().isoformat()
            ]
            
            # Add to sheet
            worksheet.append_row(row_data)
            
            print(f"✅ Added business brief for {brief.chat_title}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add business brief: {e}")
            return False
    
    def add_lead(self, lead: LeadData) -> bool:
        """Add a lead to the tracking sheet"""
        try:
            worksheet = self.create_leads_sheet()
            
            # Prepare row data
            row_data = [
                lead.chat_title,
                lead.contact_name,
                lead.company,
                lead.phone,
                lead.email,
                lead.source,
                lead.status,
                lead.last_contact,
                lead.next_follow_up,
                lead.notes,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ]
            
            # Add to sheet
            worksheet.append_row(row_data)
            
            print(f"✅ Added lead: {lead.contact_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add lead: {e}")
            return False
    
    def update_lead_status(self, chat_title: str, status: str, notes: str = "") -> bool:
        """Update lead status in the sheet"""
        try:
            worksheet = self.create_leads_sheet()
            
            # Find the row with matching chat title
            cell = worksheet.find(chat_title)
            if cell:
                row = cell.row
                # Update status and notes
                worksheet.update(f'G{row}', status)
                worksheet.update(f'J{row}', notes)
                worksheet.update(f'L{row}', datetime.now().isoformat())
                
                print(f"✅ Updated lead status for {chat_title}")
                return True
            else:
                print(f"⚠️  Lead not found: {chat_title}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to update lead status: {e}")
            return False
    
    def get_pending_follow_ups(self) -> List[Dict[str, Any]]:
        """Get all leads that need follow-up"""
        try:
            worksheet = self.create_leads_sheet()
            
            # Get all data
            data = worksheet.get_all_records()
            
            # Filter for pending follow-ups
            today = datetime.now().date()
            pending = []
            
            for row in data:
                if row.get('Next Follow Up'):
                    try:
                        follow_up_date = datetime.fromisoformat(row['Next Follow Up']).date()
                        if follow_up_date <= today:
                            pending.append(row)
                    except:
                        continue
            
            return pending
            
        except Exception as e:
            print(f"❌ Failed to get pending follow-ups: {e}")
            return []
    
    def export_message_analytics(self, analytics_data: List[Dict[str, Any]]) -> bool:
        """Export message analytics to sheet"""
        try:
            worksheet = self.create_message_analytics_sheet()
            
            # Prepare rows
            rows = []
            for data in analytics_data:
                row = [
                    data.get('date', ''),
                    data.get('chat_title', ''),
                    data.get('total_messages', 0),
                    data.get('incoming_messages', 0),
                    data.get('outgoing_messages', 0),
                    data.get('avg_response_time', ''),
                    data.get('keywords_found', ''),
                    data.get('sentiment', ''),
                    data.get('business_opportunities', ''),
                    data.get('follow_ups_required', ''),
                    data.get('notes', ''),
                    datetime.now().isoformat()
                ]
                rows.append(row)
            
            # Add to sheet
            if rows:
                worksheet.append_rows(rows)
            
            print(f"✅ Exported {len(rows)} analytics records")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export analytics: {e}")
            return False
    
    def create_dashboard_summary(self) -> Dict[str, Any]:
        """Create a summary dashboard of all data"""
        try:
            summary = {
                'total_leads': 0,
                'active_leads': 0,
                'pending_follow_ups': 0,
                'recent_briefs': 0,
                'conversion_opportunities': 0
            }
            
            # Get leads summary
            leads_worksheet = self.create_leads_sheet()
            leads_data = leads_worksheet.get_all_records()
            summary['total_leads'] = len(leads_data)
            summary['active_leads'] = len([l for l in leads_data if l.get('Status') == 'Active'])
            summary['pending_follow_ups'] = len(self.get_pending_follow_ups())
            
            # Get briefs summary
            briefs_worksheet = self.create_business_briefs_sheet()
            briefs_data = briefs_worksheet.get_all_records()
            summary['recent_briefs'] = len([b for b in briefs_data if b.get('Date')])
            
            # Count conversion opportunities
            conversion_count = 0
            for brief in briefs_data:
                if brief.get('Conversion Opportunities') and 'opportunity' in brief['Conversion Opportunities'].lower():
                    conversion_count += 1
            summary['conversion_opportunities'] = conversion_count
            
            return summary
            
        except Exception as e:
            print(f"❌ Failed to create dashboard summary: {e}")
            return {}

def main():
    """Test the Google Sheets integration"""
    try:
        manager = GoogleSheetsManager()
        
        # Test creating sheets
        manager.create_business_briefs_sheet()
        manager.create_leads_sheet()
        manager.create_message_analytics_sheet()
        
        print("✅ Google Sheets integration test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main() 