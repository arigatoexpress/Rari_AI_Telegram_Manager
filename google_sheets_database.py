#!/usr/bin/env python3
"""
Google Sheets Database System for Telegram Manager Bot
=====================================================
A comprehensive database system using Google Sheets as the primary data store.
Replaces local JSON files and SQLite databases with cloud-based storage.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
import logging
from collections import defaultdict
import asyncio
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Note:
    """Note data structure"""
    id: str
    text: str
    timestamp: str
    category: str = "general"
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    completed: bool = False

@dataclass
class Contact:
    """Contact data structure"""
    id: str
    name: str
    username: str
    phone: str
    category: str  # business_partner, lead, organization, random
    priority: int
    message_count: int
    last_message_date: str
    lead_score: float
    company: str = ""
    role: str = ""
    industry: str = ""
    interests: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    next_follow_up: str = ""

@dataclass
class Message:
    """Message data structure"""
    id: str
    chat_id: str
    chat_title: str
    sender_id: str
    sender_name: str
    text: str
    timestamp: str
    is_outgoing: bool
    sentiment_score: float = 0.0
    keywords: List[str] = field(default_factory=list)

@dataclass
class BusinessBrief:
    """Business brief data structure"""
    id: str
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
class Lead:
    """Lead data structure"""
    id: str
    contact_name: str
    company: str
    phone: str
    email: str
    source: str
    status: str
    lead_score: float
    last_contact: str
    next_follow_up: str
    notes: str
    value: float = 0.0

class GoogleSheetsDatabase:
    """Main database class using Google Sheets as storage"""
    
    def __init__(self, spreadsheet_id: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SPREADSHEET_ID")
        self.service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "google_service_account.json")
        self.client = None
        self.spreadsheet = None
        self.lock = Lock()
        
        # Sheet names
        self.sheets = {
            'notes': 'Notes',
            'contacts': 'Contacts',
            'messages': 'Messages',
            'business_briefs': 'Business_Briefs',
            'leads': 'Leads',
            'analytics': 'Analytics',
            'settings': 'Settings'
        }
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Google Sheets connection"""
        try:
            # Check if service account file exists
            if not os.path.exists(self.service_account_file):
                logger.error(f"Service account file not found: {self.service_account_file}")
                return False
            
            # Setup credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.service_account_file, scopes=scope
            )
            
            self.client = gspread.authorize(credentials)
            
            # Open or create spreadsheet
            if self.spreadsheet_id:
                try:
                    self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                    logger.info(f"✅ Connected to existing spreadsheet: {self.spreadsheet.title}")
                except Exception as e:
                    logger.error(f"❌ Error opening spreadsheet: {e}")
                    return False
            else:
                # Create new spreadsheet
                self.spreadsheet = self.client.create("Telegram Manager Database")
                self.spreadsheet_id = self.spreadsheet.id
                logger.info(f"✅ Created new spreadsheet: {self.spreadsheet.title}")
                logger.info(f"📋 Spreadsheet ID: {self.spreadsheet_id}")
            
            # Initialize sheets
            self._initialize_sheets()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing Google Sheets connection: {e}")
            return False
    
    def _initialize_sheets(self):
        """Initialize all required sheets with headers"""
        try:
            for sheet_name, display_name in self.sheets.items():
                try:
                    worksheet = self.spreadsheet.worksheet(display_name)
                    logger.info(f"✅ Sheet '{display_name}' already exists")
                except gspread.WorksheetNotFound:
                    # Create new worksheet
                    worksheet = self.spreadsheet.add_worksheet(
                        title=display_name, rows=1000, cols=20
                    )
                    logger.info(f"✅ Created new sheet: {display_name}")
                
                # Set headers based on sheet type
                headers = self._get_headers_for_sheet(sheet_name)
                if headers:
                    worksheet.update('A1', [headers])
                    worksheet.format('A1:Z1', {'textFormat': {'bold': True}})
        
        except Exception as e:
            logger.error(f"❌ Error initializing sheets: {e}")
    
    def _get_headers_for_sheet(self, sheet_name: str) -> List[str]:
        """Get headers for a specific sheet"""
        headers = {
            'notes': ['ID', 'Text', 'Timestamp', 'Category', 'Priority', 'Tags', 'Completed'],
            'contacts': [
                'ID', 'Name', 'Username', 'Phone', 'Category', 'Priority', 'Message Count',
                'Last Message Date', 'Lead Score', 'Company', 'Role', 'Industry',
                'Interests', 'Pain Points', 'Opportunities', 'Key Insights', 'Action Items', 'Next Follow Up'
            ],
            'messages': [
                'ID', 'Chat ID', 'Chat Title', 'Sender ID', 'Sender Name', 'Text',
                'Timestamp', 'Is Outgoing', 'Sentiment Score', 'Keywords'
            ],
            'business_briefs': [
                'ID', 'Chat Title', 'Chat Type', 'Date', 'Executive Brief', 'Key Insights',
                'Conversion Opportunities', 'Actionable Recommendations', 'Next Steps', 'Priority', 'Status'
            ],
            'leads': [
                'ID', 'Contact Name', 'Company', 'Phone', 'Email', 'Source', 'Status',
                'Lead Score', 'Last Contact', 'Next Follow Up', 'Notes', 'Value'
            ],
            'analytics': [
                'Date', 'Total Contacts', 'Business Partners', 'Leads', 'New Leads',
                'Conversion Rate', 'Pipeline Value', 'Top Industries', 'Engagement Score'
            ],
            'settings': ['Key', 'Value', 'Description', 'Last Updated']
        }
        return headers.get(sheet_name, [])
    
    def _get_worksheet(self, sheet_name: str):
        """Get worksheet by name"""
        try:
            return self.spreadsheet.worksheet(self.sheets[sheet_name])
        except Exception as e:
            logger.error(f"❌ Error getting worksheet '{sheet_name}': {e}")
            return None
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    # === NOTES OPERATIONS ===
    
    def add_note(self, text: str, category: str = "general", priority: str = "medium", tags: List[str] = None) -> Optional[str]:
        """Add a new note"""
        try:
            with self.lock:
                note_id = self._generate_id()
                note = Note(
                    id=note_id,
                    text=text,
                    timestamp=datetime.now().isoformat(),
                    category=category,
                    priority=priority,
                    tags=tags or []
                )
                
                worksheet = self._get_worksheet('notes')
                if not worksheet:
                    return None
                
                # Add to sheet
                row = [
                    note.id, note.text, note.timestamp, note.category, note.priority,
                    '; '.join(note.tags), note.completed
                ]
                worksheet.append_row(row)
                
                logger.info(f"✅ Note added: {note_id}")
                return note_id
                
        except Exception as e:
            logger.error(f"❌ Error adding note: {e}")
            return None
    
    def get_notes(self, limit: int = 50, category: str = None, completed: bool = None) -> List[Note]:
        """Get notes with optional filtering"""
        try:
            worksheet = self._get_worksheet('notes')
            if not worksheet:
                return []
            
            # Get all data
            data = worksheet.get_all_records()
            notes = []
            
            for row in data:
                if 'ID' not in row or not row['ID']:
                    continue
                
                note = Note(
                    id=row['ID'],
                    text=row.get('Text', ''),
                    timestamp=row.get('Timestamp', ''),
                    category=row.get('Category', 'general'),
                    priority=row.get('Priority', 'medium'),
                    tags=row.get('Tags', '').split('; ') if row.get('Tags') else [],
                    completed=row.get('Completed', False) == 'TRUE'
                )
                
                # Apply filters
                if category and note.category != category:
                    continue
                if completed is not None and note.completed != completed:
                    continue
                
                notes.append(note)
            
            # Sort by timestamp (newest first) and limit
            notes.sort(key=lambda x: x.timestamp, reverse=True)
            return notes[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting notes: {e}")
            return []
    
    def update_note(self, note_id: str, **kwargs) -> bool:
        """Update a note"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('notes')
                if not worksheet:
                    return False
                
                # Find the note
                data = worksheet.get_all_records()
                for i, row in enumerate(data, start=2):  # Start from row 2 (after headers)
                    if row.get('ID') == note_id:
                        # Update fields
                        for key, value in kwargs.items():
                            if key == 'tags' and isinstance(value, list):
                                value = '; '.join(value)
                            elif key == 'completed':
                                value = 'TRUE' if value else 'FALSE'
                            
                            # Find column index
                            headers = worksheet.row_values(1)
                            try:
                                col_idx = headers.index(key.title()) + 1
                                worksheet.update_cell(i, col_idx, value)
                            except ValueError:
                                logger.warning(f"Unknown field: {key}")
                        
                        logger.info(f"✅ Note updated: {note_id}")
                        return True
                
                logger.warning(f"Note not found: {note_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating note: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('notes')
                if not worksheet:
                    return False
                
                # Find and delete the note
                data = worksheet.get_all_records()
                for i, row in enumerate(data, start=2):
                    if row.get('ID') == note_id:
                        worksheet.delete_rows(i)
                        logger.info(f"✅ Note deleted: {note_id}")
                        return True
                
                logger.warning(f"Note not found: {note_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting note: {e}")
            return False
    
    # === CONTACTS OPERATIONS ===
    
    def add_contact(self, contact: Contact) -> bool:
        """Add a new contact"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('contacts')
                if not worksheet:
                    return False
                
                row = [
                    contact.id, contact.name, contact.username, contact.phone,
                    contact.category, contact.priority, contact.message_count,
                    contact.last_message_date, contact.lead_score, contact.company,
                    contact.role, contact.industry, '; '.join(contact.interests),
                    '; '.join(contact.pain_points), '; '.join(contact.opportunities),
                    '; '.join(contact.key_insights), '; '.join(contact.action_items),
                    contact.next_follow_up
                ]
                worksheet.append_row(row)
                
                logger.info(f"✅ Contact added: {contact.name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding contact: {e}")
            return False
    
    def get_contacts(self, category: str = None, limit: int = 100) -> List[Contact]:
        """Get contacts with optional filtering"""
        try:
            worksheet = self._get_worksheet('contacts')
            if not worksheet:
                return []
            
            data = worksheet.get_all_records()
            contacts = []
            
            for row in data:
                if 'ID' not in row or not row['ID']:
                    continue
                
                contact = Contact(
                    id=row['ID'],
                    name=row.get('Name', ''),
                    username=row.get('Username', ''),
                    phone=row.get('Phone', ''),
                    category=row.get('Category', 'random'),
                    priority=int(row.get('Priority', 1)),
                    message_count=int(row.get('Message Count', 0)),
                    last_message_date=row.get('Last Message Date', ''),
                    lead_score=float(row.get('Lead Score', 0)),
                    company=row.get('Company', ''),
                    role=row.get('Role', ''),
                    industry=row.get('Industry', ''),
                    interests=row.get('Interests', '').split('; ') if row.get('Interests') else [],
                    pain_points=row.get('Pain Points', '').split('; ') if row.get('Pain Points') else [],
                    opportunities=row.get('Opportunities', '').split('; ') if row.get('Opportunities') else [],
                    key_insights=row.get('Key Insights', '').split('; ') if row.get('Key Insights') else [],
                    action_items=row.get('Action Items', '').split('; ') if row.get('Action Items') else [],
                    next_follow_up=row.get('Next Follow Up', '')
                )
                
                if category and contact.category != category:
                    continue
                
                contacts.append(contact)
            
            # Sort by priority and lead score
            contacts.sort(key=lambda x: (x.priority, x.lead_score), reverse=True)
            return contacts[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting contacts: {e}")
            return []
    
    def update_contact(self, contact_id: str, **kwargs) -> bool:
        """Update a contact"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('contacts')
                if not worksheet:
                    return False
                
                data = worksheet.get_all_records()
                for i, row in enumerate(data, start=2):
                    if row.get('ID') == contact_id:
                        for key, value in kwargs.items():
                            if key in ['interests', 'pain_points', 'opportunities', 'key_insights', 'action_items']:
                                if isinstance(value, list):
                                    value = '; '.join(value)
                            
                            headers = worksheet.row_values(1)
                            try:
                                col_idx = headers.index(key.title()) + 1
                                worksheet.update_cell(i, col_idx, value)
                            except ValueError:
                                logger.warning(f"Unknown field: {key}")
                        
                        logger.info(f"✅ Contact updated: {contact_id}")
                        return True
                
                logger.warning(f"Contact not found: {contact_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating contact: {e}")
            return False
    
    # === MESSAGES OPERATIONS ===
    
    def add_message(self, message: Message) -> bool:
        """Add a new message"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('messages')
                if not worksheet:
                    return False
                
                row = [
                    message.id, message.chat_id, message.chat_title, message.sender_id,
                    message.sender_name, message.text, message.timestamp, message.is_outgoing,
                    message.sentiment_score, '; '.join(message.keywords)
                ]
                worksheet.append_row(row)
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
            return False
    
    def get_messages(self, chat_id: str = None, limit: int = 100) -> List[Message]:
        """Get messages with optional filtering"""
        try:
            worksheet = self._get_worksheet('messages')
            if not worksheet:
                return []
            
            data = worksheet.get_all_records()
            messages = []
            
            for row in data:
                if 'ID' not in row or not row['ID']:
                    continue
                
                message = Message(
                    id=row['ID'],
                    chat_id=row.get('Chat ID', ''),
                    chat_title=row.get('Chat Title', ''),
                    sender_id=row.get('Sender ID', ''),
                    sender_name=row.get('Sender Name', ''),
                    text=row.get('Text', ''),
                    timestamp=row.get('Timestamp', ''),
                    is_outgoing=row.get('Is Outgoing', 'FALSE') == 'TRUE',
                    sentiment_score=float(row.get('Sentiment Score', 0)),
                    keywords=row.get('Keywords', '').split('; ') if row.get('Keywords') else []
                )
                
                if chat_id and message.chat_id != chat_id:
                    continue
                
                messages.append(message)
            
            # Sort by timestamp (newest first)
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            return messages[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    # === BUSINESS BRIEFS OPERATIONS ===
    
    def add_business_brief(self, brief: BusinessBrief) -> bool:
        """Add a new business brief"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('business_briefs')
                if not worksheet:
                    return False
                
                row = [
                    brief.id, brief.chat_title, brief.chat_type, brief.date,
                    brief.executive_brief, brief.key_insights, brief.conversion_opportunities,
                    brief.actionable_recommendations, brief.next_steps, brief.priority, brief.status
                ]
                worksheet.append_row(row)
                
                logger.info(f"✅ Business brief added: {brief.chat_title}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding business brief: {e}")
            return False
    
    def get_business_briefs(self, limit: int = 50) -> List[BusinessBrief]:
        """Get business briefs"""
        try:
            worksheet = self._get_worksheet('business_briefs')
            if not worksheet:
                return []
            
            data = worksheet.get_all_records()
            briefs = []
            
            for row in data:
                if 'ID' not in row or not row['ID']:
                    continue
                
                brief = BusinessBrief(
                    id=row['ID'],
                    chat_title=row.get('Chat Title', ''),
                    chat_type=row.get('Chat Type', ''),
                    date=row.get('Date', ''),
                    executive_brief=row.get('Executive Brief', ''),
                    key_insights=row.get('Key Insights', ''),
                    conversion_opportunities=row.get('Conversion Opportunities', ''),
                    actionable_recommendations=row.get('Actionable Recommendations', ''),
                    next_steps=row.get('Next Steps', ''),
                    priority=row.get('Priority', 'medium'),
                    status=row.get('Status', 'active')
                )
                briefs.append(brief)
            
            # Sort by date (newest first)
            briefs.sort(key=lambda x: x.date, reverse=True)
            return briefs[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting business briefs: {e}")
            return []
    
    # === LEADS OPERATIONS ===
    
    def add_lead(self, lead: Lead) -> bool:
        """Add a new lead"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('leads')
                if not worksheet:
                    return False
                
                row = [
                    lead.id, lead.contact_name, lead.company, lead.phone, lead.email,
                    lead.source, lead.status, lead.lead_score, lead.last_contact,
                    lead.next_follow_up, lead.notes, lead.value
                ]
                worksheet.append_row(row)
                
                logger.info(f"✅ Lead added: {lead.contact_name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding lead: {e}")
            return False
    
    def get_leads(self, status: str = None, limit: int = 100) -> List[Lead]:
        """Get leads with optional filtering"""
        try:
            worksheet = self._get_worksheet('leads')
            if not worksheet:
                return []
            
            data = worksheet.get_all_records()
            leads = []
            
            for row in data:
                if 'ID' not in row or not row['ID']:
                    continue
                
                lead = Lead(
                    id=row['ID'],
                    contact_name=row.get('Contact Name', ''),
                    company=row.get('Company', ''),
                    phone=row.get('Phone', ''),
                    email=row.get('Email', ''),
                    source=row.get('Source', ''),
                    status=row.get('Status', 'New'),
                    lead_score=float(row.get('Lead Score', 0)),
                    last_contact=row.get('Last Contact', ''),
                    next_follow_up=row.get('Next Follow Up', ''),
                    notes=row.get('Notes', ''),
                    value=float(row.get('Value', 0))
                )
                
                if status and lead.status != status:
                    continue
                
                leads.append(lead)
            
            # Sort by lead score (highest first)
            leads.sort(key=lambda x: x.lead_score, reverse=True)
            return leads[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting leads: {e}")
            return []
    
    # === ANALYTICS OPERATIONS ===
    
    def add_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """Add analytics data"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('analytics')
                if not worksheet:
                    return False
                
                row = [
                    analytics_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    analytics_data.get('total_contacts', 0),
                    analytics_data.get('business_partners', 0),
                    analytics_data.get('leads', 0),
                    analytics_data.get('new_leads', 0),
                    analytics_data.get('conversion_rate', 0),
                    analytics_data.get('pipeline_value', 0),
                    analytics_data.get('top_industries', ''),
                    analytics_data.get('engagement_score', 0)
                ]
                worksheet.append_row(row)
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding analytics: {e}")
            return False
    
    def get_analytics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get analytics data for the last N days"""
        try:
            worksheet = self._get_worksheet('analytics')
            if not worksheet:
                return []
            
            data = worksheet.get_all_records()
            analytics = []
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            for row in data:
                if row.get('Date', '') >= cutoff_date:
                    analytics.append(row)
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return []
    
    # === SETTINGS OPERATIONS ===
    
    def set_setting(self, key: str, value: str, description: str = "") -> bool:
        """Set a setting"""
        try:
            with self.lock:
                worksheet = self._get_worksheet('settings')
                if not worksheet:
                    return False
                
                # Check if setting exists
                data = worksheet.get_all_records()
                for i, row in enumerate(data, start=2):
                    if row.get('Key') == key:
                        # Update existing setting
                        worksheet.update_cell(i, 2, value)  # Value column
                        worksheet.update_cell(i, 3, description)  # Description column
                        worksheet.update_cell(i, 4, datetime.now().isoformat())  # Last Updated
                        return True
                
                # Add new setting
                row = [key, value, description, datetime.now().isoformat()]
                worksheet.append_row(row)
                return True
                
        except Exception as e:
            logger.error(f"❌ Error setting setting: {e}")
            return False
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a setting"""
        try:
            worksheet = self._get_worksheet('settings')
            if not worksheet:
                return default
            
            data = worksheet.get_all_records()
            for row in data:
                if row.get('Key') == key:
                    return row.get('Value', default)
            
            return default
            
        except Exception as e:
            logger.error(f"❌ Error getting setting: {e}")
            return default
    
    # === UTILITY METHODS ===
    
    def get_spreadsheet_url(self) -> str:
        """Get the spreadsheet URL"""
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
    
    def export_data(self, sheet_name: str, format: str = "json") -> str:
        """Export data from a sheet"""
        try:
            worksheet = self._get_worksheet(sheet_name)
            if not worksheet:
                return ""
            
            data = worksheet.get_all_records()
            
            if format == "json":
                return json.dumps(data, indent=2)
            elif format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
                writer.writeheader()
                writer.writerows(data)
                return output.getvalue()
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"❌ Error exporting data: {e}")
            return ""
    
    def backup_all_data(self) -> Dict[str, str]:
        """Backup all data from all sheets"""
        backup = {}
        for sheet_name in self.sheets.keys():
            backup[sheet_name] = self.export_data(sheet_name, "json")
        return backup

# Global database instance
_db_instance = None

def get_database() -> GoogleSheetsDatabase:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = GoogleSheetsDatabase()
    return _db_instance

def initialize_database(spreadsheet_id: str = None) -> GoogleSheetsDatabase:
    """Initialize the database with optional spreadsheet ID"""
    global _db_instance
    _db_instance = GoogleSheetsDatabase(spreadsheet_id)
    return _db_instance

if __name__ == "__main__":
    # Test the database
    db = get_database()
    
    # Test adding a note
    note_id = db.add_note("Test note from Google Sheets Database", "test", "high", ["test", "database"])
    print(f"Added note: {note_id}")
    
    # Test getting notes
    notes = db.get_notes(limit=5)
    print(f"Found {len(notes)} notes")
    
    # Test adding a contact
    contact = Contact(
        id=db._generate_id(),
        name="Test Contact",
        username="testuser",
        phone="+1234567890",
        category="lead",
        priority=3,
        message_count=10,
        last_message_date=datetime.now().isoformat(),
        lead_score=75.0,
        company="Test Corp",
        role="Manager",
        industry="Technology"
    )
    
    success = db.add_contact(contact)
    print(f"Added contact: {success}")
    
    # Test getting contacts
    contacts = db.get_contacts(limit=5)
    print(f"Found {len(contacts)} contacts")
    
    print(f"Database URL: {db.get_spreadsheet_url()}") 