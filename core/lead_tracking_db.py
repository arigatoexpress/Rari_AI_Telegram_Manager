#!/usr/bin/env python3
"""
Lead Tracking Database Manager
=============================
Comprehensive database system for organizing contacts, organizations, 
group chats, and tracking leads with Google Sheets integration.
"""

import sqlite3
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
from enum import Enum

logger = logging.getLogger(__name__)

# Enums for better data consistency
class ContactType(Enum):
    LEAD = "lead"
    CUSTOMER = "customer"
    PARTNER = "partner"
    INVESTOR = "investor"
    ADVISOR = "advisor"
    VENDOR = "vendor"
    COMMUNITY = "community"

class LeadStatus(Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class OrganizationType(Enum):
    VC_FUND = "vc_fund"
    DEFI_PROTOCOL = "defi_protocol"
    EXCHANGE = "exchange"
    BLOCKCHAIN = "blockchain"
    STARTUP = "startup"
    CORPORATION = "corporation"
    DAO = "dao"
    MEDIA = "media"
    EDUCATION = "education"
    OTHER = "other"

class InteractionType(Enum):
    MESSAGE = "message"
    CALL = "call"
    MEETING = "meeting"
    EMAIL = "email"
    DEMO = "demo"
    PROPOSAL = "proposal"

@dataclass
class Contact:
    contact_id: int = None
    user_id: int = None
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    phone_number: str = ""
    bio: str = ""
    organization_id: int = None
    contact_type: str = ContactType.LEAD.value
    lead_status: str = LeadStatus.COLD.value
    lead_score: int = 0
    estimated_value: float = 0.0
    probability: int = 0
    tags: str = ""  # JSON array of tags
    notes: str = ""
    last_interaction: str = None
    next_follow_up: str = None
    created_at: str = None
    updated_at: str = None

@dataclass
class Organization:
    organization_id: int = None
    name: str = ""
    industry: str = ""
    size: str = ""
    location: str = ""
    website: str = ""
    description: str = ""
    organization_type: str = OrganizationType.OTHER.value
    funding_stage: str = ""
    market_cap: str = ""
    employee_count: int = 0
    tags: str = ""  # JSON array of tags
    created_at: str = None
    updated_at: str = None

@dataclass
class GroupChat:
    chat_id: int = None
    title: str = ""
    chat_type: str = ""
    member_count: int = 0
    description: str = ""
    organization_id: int = None
    is_active: bool = True
    tags: str = ""  # JSON array of tags
    created_at: str = None
    updated_at: str = None

@dataclass
class Interaction:
    interaction_id: int = None
    contact_id: int = None
    chat_id: int = None
    interaction_type: str = InteractionType.MESSAGE.value
    interaction_date: str = None
    subject: str = ""
    notes: str = ""
    outcome: str = ""
    next_action: str = ""
    created_at: str = None

@dataclass
class Lead:
    lead_id: int = None
    contact_id: int = None
    opportunity_type: str = ""
    estimated_value: float = 0.0
    probability: int = 0
    stage: str = LeadStatus.COLD.value
    source: str = ""
    assigned_to: str = ""
    last_activity: str = None
    next_follow_up: str = None
    deal_size: str = ""
    timeline: str = ""
    decision_makers: str = ""  # JSON array
    pain_points: str = ""  # JSON array
    created_at: str = None
    updated_at: str = None

class LeadTrackingDB:
    """Enhanced database for lead tracking and CRM functionality"""
    
    def __init__(self, db_path: str = "data/lead_tracking.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        logger.info("✅ Lead Tracking Database initialized")
    
    def _init_database(self):
        """Initialize database with comprehensive schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Organizations table
                CREATE TABLE IF NOT EXISTS organizations (
                    organization_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    industry TEXT,
                    size TEXT,
                    location TEXT,
                    website TEXT,
                    description TEXT,
                    organization_type TEXT DEFAULT 'other',
                    funding_stage TEXT,
                    market_cap TEXT,
                    employee_count INTEGER DEFAULT 0,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Contacts table
                CREATE TABLE IF NOT EXISTS contacts (
                    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    phone_number TEXT,
                    bio TEXT,
                    organization_id INTEGER,
                    contact_type TEXT DEFAULT 'lead',
                    lead_status TEXT DEFAULT 'cold',
                    lead_score INTEGER DEFAULT 0,
                    estimated_value REAL DEFAULT 0.0,
                    probability INTEGER DEFAULT 0,
                    tags TEXT,
                    notes TEXT,
                    last_interaction TIMESTAMP,
                    next_follow_up TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
                );
                
                -- Group chats table
                CREATE TABLE IF NOT EXISTS group_chats (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    chat_type TEXT,
                    member_count INTEGER DEFAULT 0,
                    description TEXT,
                    organization_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
                );
                
                -- Enhanced messages table
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_message_id INTEGER,
                    chat_id INTEGER,
                    contact_id INTEGER,
                    message_text TEXT,
                    message_type TEXT DEFAULT 'text',
                    timestamp TIMESTAMP,
                    is_outbound BOOLEAN DEFAULT 0,
                    sentiment_score REAL,
                    contains_opportunity BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES group_chats (chat_id),
                    FOREIGN KEY (contact_id) REFERENCES contacts (contact_id)
                );
                
                -- Interactions table
                CREATE TABLE IF NOT EXISTS interactions (
                    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    chat_id INTEGER,
                    interaction_type TEXT DEFAULT 'message',
                    interaction_date TIMESTAMP,
                    subject TEXT,
                    notes TEXT,
                    outcome TEXT,
                    next_action TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (contact_id),
                    FOREIGN KEY (chat_id) REFERENCES group_chats (chat_id)
                );
                
                -- Leads/Opportunities table
                CREATE TABLE IF NOT EXISTS leads (
                    lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    opportunity_type TEXT,
                    estimated_value REAL DEFAULT 0.0,
                    probability INTEGER DEFAULT 0,
                    stage TEXT DEFAULT 'cold',
                    source TEXT,
                    assigned_to TEXT,
                    last_activity TIMESTAMP,
                    next_follow_up TIMESTAMP,
                    deal_size TEXT,
                    timeline TEXT,
                    decision_makers TEXT,
                    pain_points TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (contact_id)
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts(user_id);
                CREATE INDEX IF NOT EXISTS idx_contacts_organization ON contacts(organization_id);
                CREATE INDEX IF NOT EXISTS idx_contacts_lead_status ON contacts(lead_status);
                CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
                CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
                CREATE INDEX IF NOT EXISTS idx_interactions_contact_id ON interactions(contact_id);
                CREATE INDEX IF NOT EXISTS idx_leads_contact_id ON leads(contact_id);
                CREATE INDEX IF NOT EXISTS idx_leads_stage ON leads(stage);
            """)
            conn.commit()
    
    # Organization Management
    def create_organization(self, org_data: Dict) -> int:
        """Create a new organization"""
        try:
            org = Organization(**org_data)
            org.created_at = datetime.now().isoformat()
            org.updated_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO organizations (
                        name, industry, size, location, website, description,
                        organization_type, funding_stage, market_cap, employee_count,
                        tags, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    org.name, org.industry, org.size, org.location, org.website,
                    org.description, org.organization_type, org.funding_stage,
                    org.market_cap, org.employee_count, org.tags,
                    org.created_at, org.updated_at
                ))
                org_id = cursor.lastrowid
                conn.commit()
                logger.info(f"✅ Created organization: {org.name} (ID: {org_id})")
                return org_id
        except Exception as e:
            logger.error(f"❌ Error creating organization: {e}")
            return None
    
    def get_organization(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM organizations WHERE organization_id = ?", (org_id,))
                row = cursor.fetchone()
                if row:
                    return Organization(**dict(row))
                return None
        except Exception as e:
            logger.error(f"❌ Error getting organization: {e}")
            return None
    
    def search_organizations(self, query: str) -> List[Organization]:
        """Search organizations by name or industry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM organizations 
                    WHERE name LIKE ? OR industry LIKE ? OR description LIKE ?
                    ORDER BY name
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
                rows = cursor.fetchall()
                return [Organization(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"❌ Error searching organizations: {e}")
            return []
    
    # Contact Management
    def create_contact(self, contact_data: Dict) -> int:
        """Create or update a contact"""
        try:
            contact = Contact(**contact_data)
            contact.created_at = datetime.now().isoformat()
            contact.updated_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if contact exists by user_id
                if contact.user_id:
                    cursor.execute("SELECT contact_id FROM contacts WHERE user_id = ?", (contact.user_id,))
                    existing = cursor.fetchone()
                    if existing:
                        return self.update_contact(existing[0], contact_data)
                
                cursor.execute("""
                    INSERT INTO contacts (
                        user_id, first_name, last_name, username, phone_number, bio,
                        organization_id, contact_type, lead_status, lead_score,
                        estimated_value, probability, tags, notes, last_interaction,
                        next_follow_up, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact.user_id, contact.first_name, contact.last_name,
                    contact.username, contact.phone_number, contact.bio,
                    contact.organization_id, contact.contact_type, contact.lead_status,
                    contact.lead_score, contact.estimated_value, contact.probability,
                    contact.tags, contact.notes, contact.last_interaction,
                    contact.next_follow_up, contact.created_at, contact.updated_at
                ))
                contact_id = cursor.lastrowid
                conn.commit()
                logger.info(f"✅ Created contact: {contact.first_name} {contact.last_name} (ID: {contact_id})")
                return contact_id
        except Exception as e:
            logger.error(f"❌ Error creating contact: {e}")
            return None
    
    def update_contact(self, contact_id: int, updates: Dict) -> bool:
        """Update contact information"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            for key, value in updates.items():
                if key != 'contact_id':
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(contact_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = f"UPDATE contacts SET {', '.join(set_clauses)} WHERE contact_id = ?"
                cursor.execute(query, values)
                conn.commit()
                logger.info(f"✅ Updated contact ID: {contact_id}")
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error updating contact: {e}")
            return False
    
    def get_contact_by_user_id(self, user_id: int) -> Optional[Contact]:
        """Get contact by Telegram user ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM contacts WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    return Contact(**dict(row))
                return None
        except Exception as e:
            logger.error(f"❌ Error getting contact: {e}")
            return None
    
    def get_contacts_by_status(self, status: str) -> List[Contact]:
        """Get contacts by lead status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.*, o.name as organization_name 
                    FROM contacts c
                    LEFT JOIN organizations o ON c.organization_id = o.organization_id
                    WHERE c.lead_status = ?
                    ORDER BY c.lead_score DESC, c.last_interaction DESC
                """, (status,))
                rows = cursor.fetchall()
                return [Contact(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"❌ Error getting contacts by status: {e}")
            return []
    
    # Group Chat Management
    def create_group_chat(self, chat_data: Dict) -> bool:
        """Create or update group chat"""
        try:
            chat = GroupChat(**chat_data)
            chat.created_at = datetime.now().isoformat()
            chat.updated_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO group_chats (
                        chat_id, title, chat_type, member_count, description,
                        organization_id, is_active, tags, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat.chat_id, chat.title, chat.chat_type, chat.member_count,
                    chat.description, chat.organization_id, chat.is_active,
                    chat.tags, chat.created_at, chat.updated_at
                ))
                conn.commit()
                logger.info(f"✅ Created/updated group chat: {chat.title}")
                return True
        except Exception as e:
            logger.error(f"❌ Error creating group chat: {e}")
            return False
    
    # Message Storage
    def store_message(self, message_data: Dict) -> bool:
        """Store message with enhanced metadata"""
        try:
            # Ensure contact exists
            if message_data.get('user_id'):
                contact = self.get_contact_by_user_id(message_data['user_id'])
                if not contact:
                    # Create contact automatically
                    contact_data = {
                        'user_id': message_data.get('user_id'),
                        'first_name': message_data.get('first_name', ''),
                        'last_name': message_data.get('last_name', ''),
                        'username': message_data.get('username', ''),
                        'last_interaction': datetime.now().isoformat()
                    }
                    contact_id = self.create_contact(contact_data)
                else:
                    contact_id = contact.contact_id
                    # Update last interaction
                    self.update_contact(contact_id, {'last_interaction': datetime.now().isoformat()})
            else:
                contact_id = None
            
            # Ensure group chat exists
            if message_data.get('chat_id'):
                chat_data = {
                    'chat_id': message_data.get('chat_id'),
                    'title': message_data.get('chat_title', f"Chat {message_data.get('chat_id')}"),
                    'chat_type': message_data.get('chat_type', 'private')
                }
                self.create_group_chat(chat_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO messages (
                        telegram_message_id, chat_id, contact_id, message_text,
                        message_type, timestamp, is_outbound, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message_data.get('message_id'),
                    message_data.get('chat_id'),
                    contact_id,
                    message_data.get('message_text', ''),
                    message_data.get('message_type', 'text'),
                    message_data.get('timestamp', datetime.now().isoformat()),
                    message_data.get('is_outbound', False),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Error storing message: {e}")
            return False
    
    # Analytics and Reporting
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Contact stats
                cursor.execute("SELECT COUNT(*) FROM contacts")
                stats['total_contacts'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT lead_status, COUNT(*) FROM contacts GROUP BY lead_status")
                stats['contacts_by_status'] = dict(cursor.fetchall())
                
                cursor.execute("SELECT contact_type, COUNT(*) FROM contacts GROUP BY contact_type")
                stats['contacts_by_type'] = dict(cursor.fetchall())
                
                # Organization stats
                cursor.execute("SELECT COUNT(*) FROM organizations")
                stats['total_organizations'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT organization_type, COUNT(*) FROM organizations GROUP BY organization_type")
                stats['organizations_by_type'] = dict(cursor.fetchall())
                
                # Lead stats
                cursor.execute("SELECT COUNT(*) FROM leads")
                stats['total_leads'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(estimated_value) FROM leads WHERE stage NOT IN ('closed_lost')")
                pipeline_value = cursor.fetchone()[0]
                stats['pipeline_value'] = pipeline_value or 0
                
                cursor.execute("SELECT stage, COUNT(*) FROM leads GROUP BY stage")
                stats['leads_by_stage'] = dict(cursor.fetchall())
                
                # Activity stats
                cursor.execute("SELECT COUNT(*) FROM messages WHERE timestamp > datetime('now', '-7 days')")
                stats['messages_last_7_days'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM interactions WHERE interaction_date > datetime('now', '-7 days')")
                stats['interactions_last_7_days'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            logger.error(f"❌ Error getting dashboard stats: {e}")
            return {}
    
    def export_to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Export all data to pandas DataFrames for analysis"""
        try:
            dataframes = {}
            
            with sqlite3.connect(self.db_path) as conn:
                # Contacts with organization info
                dataframes['contacts'] = pd.read_sql_query("""
                    SELECT 
                        c.*,
                        o.name as organization_name,
                        o.industry as organization_industry,
                        o.organization_type
                    FROM contacts c
                    LEFT JOIN organizations o ON c.organization_id = o.organization_id
                    ORDER BY c.lead_score DESC, c.last_interaction DESC
                """, conn)
                
                # Organizations
                dataframes['organizations'] = pd.read_sql_query("""
                    SELECT * FROM organizations ORDER BY name
                """, conn)
                
                # Group chats
                dataframes['group_chats'] = pd.read_sql_query("""
                    SELECT 
                        gc.*,
                        o.name as organization_name
                    FROM group_chats gc
                    LEFT JOIN organizations o ON gc.organization_id = o.organization_id
                    ORDER BY gc.member_count DESC
                """, conn)
                
                # Leads/Opportunities
                dataframes['leads'] = pd.read_sql_query("""
                    SELECT 
                        l.*,
                        c.first_name,
                        c.last_name,
                        c.username,
                        o.name as organization_name
                    FROM leads l
                    JOIN contacts c ON l.contact_id = c.contact_id
                    LEFT JOIN organizations o ON c.organization_id = o.organization_id
                    ORDER BY l.estimated_value DESC, l.probability DESC
                """, conn)
                
                # Recent interactions
                dataframes['interactions'] = pd.read_sql_query("""
                    SELECT 
                        i.*,
                        c.first_name,
                        c.last_name,
                        c.username,
                        gc.title as chat_title
                    FROM interactions i
                    JOIN contacts c ON i.contact_id = c.contact_id
                    LEFT JOIN group_chats gc ON i.chat_id = gc.chat_id
                    ORDER BY i.interaction_date DESC
                """, conn)
                
                logger.info("✅ Data exported to DataFrames")
                return dataframes
                
        except Exception as e:
            logger.error(f"❌ Error exporting to DataFrames: {e}")
            return {}

    def get_hot_leads(self, limit: int = 10) -> List[Dict]:
        """Get hot leads for immediate action"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        c.contact_id,
                        c.first_name,
                        c.last_name,
                        c.username,
                        c.lead_status,
                        c.lead_score,
                        c.estimated_value,
                        c.probability,
                        c.last_interaction,
                        c.next_follow_up,
                        o.name as organization_name,
                        o.organization_type
                    FROM contacts c
                    LEFT JOIN organizations o ON c.organization_id = o.organization_id
                    WHERE c.lead_status IN ('hot', 'qualified', 'proposal', 'negotiation')
                       OR c.lead_score >= 70
                    ORDER BY c.lead_score DESC, c.estimated_value DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"❌ Error getting hot leads: {e}")
            return []

    def get_follow_up_needed(self, days_threshold: int = 3) -> List[Dict]:
        """Get contacts that need follow-up"""
        try:
            threshold_date = (datetime.now() - timedelta(days=days_threshold)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        c.*,
                        o.name as organization_name,
                        julianday('now') - julianday(c.last_interaction) as days_since_contact
                    FROM contacts c
                    LEFT JOIN organizations o ON c.organization_id = o.organization_id
                    WHERE c.last_interaction < ?
                       AND c.lead_status NOT IN ('closed_won', 'closed_lost')
                       AND c.contact_type IN ('lead', 'customer', 'investor', 'partner')
                    ORDER BY days_since_contact DESC, c.lead_score DESC
                """, (threshold_date,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"❌ Error getting follow-up needed: {e}")
            return []

    def add_interaction(self, interaction_data: Dict) -> bool:
        """Add an interaction record"""
        try:
            interaction = Interaction(**interaction_data)
            interaction.created_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO interactions (
                        contact_id, chat_id, interaction_type, interaction_date,
                        subject, notes, outcome, next_action, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.contact_id, interaction.chat_id, interaction.interaction_type,
                    interaction.interaction_date, interaction.subject, interaction.notes,
                    interaction.outcome, interaction.next_action, interaction.created_at
                ))
                conn.commit()
                
                # Update contact's last interaction
                self.update_contact(interaction.contact_id, {
                    'last_interaction': interaction.interaction_date or datetime.now().isoformat()
                })
                
                logger.info(f"✅ Added interaction for contact {interaction.contact_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Error adding interaction: {e}")
            return False

    def create_lead(self, lead_data: Dict) -> int:
        """Create a new lead/opportunity"""
        try:
            lead = Lead(**lead_data)
            lead.created_at = datetime.now().isoformat()
            lead.updated_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO leads (
                        contact_id, opportunity_type, estimated_value, probability,
                        stage, source, assigned_to, last_activity, next_follow_up,
                        deal_size, timeline, decision_makers, pain_points,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead.contact_id, lead.opportunity_type, lead.estimated_value,
                    lead.probability, lead.stage, lead.source, lead.assigned_to,
                    lead.last_activity, lead.next_follow_up, lead.deal_size,
                    lead.timeline, lead.decision_makers, lead.pain_points,
                    lead.created_at, lead.updated_at
                ))
                lead_id = cursor.lastrowid
                conn.commit()
                
                # Update contact with lead info
                self.update_contact(lead.contact_id, {
                    'estimated_value': lead.estimated_value,
                    'probability': lead.probability,
                    'lead_status': lead.stage
                })
                
                logger.info(f"✅ Created lead for contact {lead.contact_id} (Lead ID: {lead_id})")
                return lead_id
        except Exception as e:
            logger.error(f"❌ Error creating lead: {e}")
            return None

    def migrate_from_old_db(self, old_db_path: str) -> bool:
        """Migrate data from old database format"""
        try:
            if not Path(old_db_path).exists():
                logger.warning(f"Old database not found: {old_db_path}")
                return False
            
            with sqlite3.connect(old_db_path) as old_conn:
                old_conn.row_factory = sqlite3.Row
                cursor = old_conn.cursor()
                
                # Migrate messages and create contacts
                cursor.execute("SELECT * FROM messages")
                messages = cursor.fetchall()
                
                migrated_contacts = set()
                migrated_chats = set()
                
                for msg in messages:
                    msg_dict = dict(msg)
                    
                    # Create contact if not exists
                    if msg_dict.get('user_id') and msg_dict['user_id'] not in migrated_contacts:
                        contact_data = {
                            'user_id': msg_dict['user_id'],
                            'first_name': msg_dict.get('first_name', ''),
                            'last_name': msg_dict.get('last_name', ''),
                            'username': msg_dict.get('username', ''),
                            'last_interaction': msg_dict.get('timestamp')
                        }
                        self.create_contact(contact_data)
                        migrated_contacts.add(msg_dict['user_id'])
                    
                    # Create group chat if not exists
                    if msg_dict.get('chat_id') and msg_dict['chat_id'] not in migrated_chats:
                        chat_data = {
                            'chat_id': msg_dict['chat_id'],
                            'title': msg_dict.get('chat_title', f"Chat {msg_dict['chat_id']}"),
                            'chat_type': 'group' if str(msg_dict['chat_id']).startswith('-') else 'private'
                        }
                        self.create_group_chat(chat_data)
                        migrated_chats.add(msg_dict['chat_id'])
                    
                    # Store message
                    self.store_message(msg_dict)
                
                logger.info(f"✅ Migrated {len(messages)} messages, {len(migrated_contacts)} contacts, {len(migrated_chats)} chats")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error migrating from old database: {e}")
            return False


class GoogleSheetsExporter:
    """Google Sheets integration for lead tracking"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path
        self.sheets_client = None
        self._init_sheets_client()
    
    def _init_sheets_client(self):
        """Initialize Google Sheets client"""
        try:
            # This would need proper Google Sheets API setup
            # For now, we'll create a placeholder that exports to CSV
            logger.info("📊 Google Sheets exporter initialized (CSV mode)")
        except Exception as e:
            logger.error(f"❌ Error initializing Google Sheets: {e}")
    
    def export_leads_to_sheets(self, db: LeadTrackingDB, sheet_id: str = None) -> bool:
        """Export lead data to Google Sheets or CSV"""
        try:
            # Get data from database
            dataframes = db.export_to_dataframes()
            
            if not dataframes:
                logger.error("No data to export")
                return False
            
            # Create exports directory
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export each dataframe to CSV
            for table_name, df in dataframes.items():
                csv_path = export_dir / f"{table_name}_{timestamp}.csv"
                df.to_csv(csv_path, index=False)
                logger.info(f"✅ Exported {table_name} to {csv_path}")
            
            # Create a comprehensive lead tracking sheet
            self._create_lead_tracking_sheet(dataframes, export_dir, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting to sheets: {e}")
            return False
    
    def _create_lead_tracking_sheet(self, dataframes: Dict, export_dir: Path, timestamp: str):
        """Create a comprehensive lead tracking spreadsheet"""
        try:
            contacts_df = dataframes.get('contacts', pd.DataFrame())
            leads_df = dataframes.get('leads', pd.DataFrame())
            
            if contacts_df.empty:
                return
            
            # Create lead tracking summary
            lead_summary = contacts_df[[
                'contact_id', 'first_name', 'last_name', 'username',
                'organization_name', 'contact_type', 'lead_status', 
                'lead_score', 'estimated_value', 'probability',
                'last_interaction', 'next_follow_up', 'notes'
            ]].copy()
            
            # Add calculated fields
            lead_summary['full_name'] = lead_summary['first_name'] + ' ' + lead_summary['last_name']
            lead_summary['days_since_contact'] = pd.to_datetime('now') - pd.to_datetime(lead_summary['last_interaction'])
            lead_summary['days_since_contact'] = lead_summary['days_since_contact'].dt.days
            
            # Sort by lead score and estimated value
            lead_summary = lead_summary.sort_values(['lead_score', 'estimated_value'], ascending=[False, False])
            
            # Export lead tracking summary
            summary_path = export_dir / f"LEAD_TRACKING_SUMMARY_{timestamp}.csv"
            lead_summary.to_csv(summary_path, index=False)
            
            # Create pipeline report
            pipeline_stats = {
                'Total Contacts': len(contacts_df),
                'Total Pipeline Value': contacts_df['estimated_value'].sum(),
                'Average Lead Score': contacts_df['lead_score'].mean(),
                'Hot Leads (Score 70+)': len(contacts_df[contacts_df['lead_score'] >= 70]),
                'High Value Leads (>$50k)': len(contacts_df[contacts_df['estimated_value'] > 50000]),
                'Contacts Needing Follow-up': len(contacts_df[contacts_df['days_since_contact'] > 3])
            }
            
            pipeline_df = pd.DataFrame(list(pipeline_stats.items()), columns=['Metric', 'Value'])
            pipeline_path = export_dir / f"PIPELINE_STATS_{timestamp}.csv"
            pipeline_df.to_csv(pipeline_path, index=False)
            
            logger.info(f"✅ Created lead tracking summary: {summary_path}")
            logger.info(f"✅ Created pipeline stats: {pipeline_path}")
            
        except Exception as e:
            logger.error(f"❌ Error creating lead tracking sheet: {e}")


# Utility functions for lead management
def calculate_lead_score(contact: Dict, interactions_count: int = 0) -> int:
    """Calculate lead score based on various factors"""
    score = 0
    
    # Base scoring
    if contact.get('contact_type') == 'investor':
        score += 30
    elif contact.get('contact_type') == 'partner':
        score += 20
    elif contact.get('contact_type') == 'customer':
        score += 15
    
    # Organization type bonus
    org_type = contact.get('organization_type', '')
    if org_type in ['vc_fund', 'defi_protocol']:
        score += 25
    elif org_type in ['exchange', 'blockchain']:
        score += 20
    
    # Interaction frequency
    score += min(interactions_count * 5, 30)
    
    # Recent activity bonus
    if contact.get('last_interaction'):
        try:
            last_interaction = datetime.fromisoformat(contact['last_interaction'])
            days_ago = (datetime.now() - last_interaction).days
            if days_ago <= 1:
                score += 20
            elif days_ago <= 3:
                score += 15
            elif days_ago <= 7:
                score += 10
        except:
            pass
    
    # Estimated value bonus
    estimated_value = contact.get('estimated_value', 0)
    if estimated_value > 100000:
        score += 25
    elif estimated_value > 50000:
        score += 15
    elif estimated_value > 10000:
        score += 10
    
    return min(score, 100)  # Cap at 100

def analyze_lead_health(db: LeadTrackingDB) -> Dict[str, Any]:
    """Analyze overall lead pipeline health"""
    try:
        stats = db.get_dashboard_stats()
        
        # Calculate health metrics
        total_contacts = stats.get('total_contacts', 0)
        pipeline_value = stats.get('pipeline_value', 0)
        
        health_score = 0
        issues = []
        recommendations = []
        
        # Contact volume check
        if total_contacts < 50:
            issues.append("Low contact volume")
            recommendations.append("Focus on networking and lead generation")
        else:
            health_score += 20
        
        # Pipeline value check
        if pipeline_value < 100000:
            issues.append("Low pipeline value")
            recommendations.append("Target higher-value opportunities")
        else:
            health_score += 25
        
        # Lead status distribution
        status_dist = stats.get('contacts_by_status', {})
        hot_leads = status_dist.get('hot', 0) + status_dist.get('qualified', 0)
        
        if hot_leads < total_contacts * 0.1:  # Less than 10% hot leads
            issues.append("Low conversion rate")
            recommendations.append("Improve lead qualification and nurturing")
        else:
            health_score += 25
        
        # Activity level
        recent_activity = stats.get('messages_last_7_days', 0)
        if recent_activity < total_contacts * 0.2:  # Less than 20% activity rate
            issues.append("Low engagement activity")
            recommendations.append("Increase outreach frequency")
        else:
            health_score += 30
        
        return {
            'health_score': health_score,
            'grade': 'A' if health_score >= 80 else 'B' if health_score >= 60 else 'C' if health_score >= 40 else 'D',
            'issues': issues,
            'recommendations': recommendations,
            'metrics': stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing lead health: {e}")
        return {'health_score': 0, 'grade': 'F', 'issues': ['Analysis failed'], 'recommendations': [], 'metrics': {}} 