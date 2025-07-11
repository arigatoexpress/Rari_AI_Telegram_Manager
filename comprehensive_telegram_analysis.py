#!/usr/bin/env python3
"""
Comprehensive Telegram Analysis System
=====================================
Analyzes EVERY Telegram chat organized by contact/group chat, 
uses batched ChatGPT analysis to avoid API limits, and creates 
a complete leads database and Google Sheets.

Features:
- Process ALL 10,028 messages organized by contact
- Batch ChatGPT requests (max 60 requests/minute)
- Complete conversation analysis per contact
- Advanced lead scoring with full context
- Automatic Google Sheets upload with your personal account
"""

import json
import sqlite3
import logging
import asyncio
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pandas as pd
from collections import defaultdict, Counter
import openai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/comprehensive_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContactConversation:
    """Complete conversation data for a contact"""
    contact_id: str
    user_id: int
    username: str = None
    first_name: str = None
    last_name: str = None
    phone: str = None
    total_messages: int = 0
    first_message_date: str = None
    last_message_date: str = None
    conversation_text: str = ""
    business_keywords: List[str] = None
    chat_groups: List[str] = None
    message_frequency: Dict[str, int] = None
    response_pattern: str = ""

@dataclass
class LeadAnalysis:
    """Complete lead analysis from ChatGPT"""
    contact_id: str
    is_lead: bool
    lead_probability: float
    estimated_value: float
    stage: str
    opportunity_type: str
    decision_makers: List[str]
    pain_points: List[str]
    timeline: str
    next_action: str
    business_context: str
    conversation_quality: str
    relationship_strength: str

class ComprehensiveTelegramAnalyzer:
    """Complete Telegram analysis with ChatGPT integration"""
    
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.db_path = Path("data/comprehensive_telegram_analysis.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.telegram_data = None
        self.contacts_conversations = {}
        self.group_conversations = {}
        
        # Rate limiting for ChatGPT (60 requests/minute)
        self.last_request_time = 0
        self.request_interval = 1.0  # 1 second between requests
        self.batch_size = 10  # Process 10 contacts per batch
        
        openai.api_key = self.openai_api_key
        self._init_database()
        
    def _init_database(self):
        """Initialize comprehensive database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Complete contact conversations
                CREATE TABLE IF NOT EXISTS contact_conversations (
                    contact_id TEXT PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    total_messages INTEGER DEFAULT 0,
                    first_message_date TEXT,
                    last_message_date TEXT,
                    conversation_text TEXT,
                    business_keywords TEXT, -- JSON array
                    chat_groups TEXT, -- JSON array  
                    message_frequency TEXT, -- JSON object
                    response_pattern TEXT,
                    conversation_length INTEGER DEFAULT 0,
                    avg_message_length REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Group chat analysis
                CREATE TABLE IF NOT EXISTS group_conversations (
                    group_id TEXT PRIMARY KEY,
                    chat_id INTEGER,
                    group_title TEXT,
                    member_count INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    business_relevance REAL DEFAULT 0,
                    key_participants TEXT, -- JSON array
                    main_topics TEXT, -- JSON array
                    opportunity_mentions TEXT, -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Complete lead analysis
                CREATE TABLE IF NOT EXISTS comprehensive_leads (
                    lead_id TEXT PRIMARY KEY,
                    contact_id TEXT NOT NULL,
                    user_id INTEGER,
                    is_lead BOOLEAN DEFAULT FALSE,
                    lead_probability REAL DEFAULT 0,
                    estimated_value REAL DEFAULT 0,
                    stage TEXT DEFAULT 'prospect',
                    opportunity_type TEXT,
                    decision_makers TEXT, -- JSON array
                    pain_points TEXT, -- JSON array
                    timeline TEXT,
                    next_action TEXT,
                    business_context TEXT,
                    conversation_quality TEXT,
                    relationship_strength TEXT,
                    chatgpt_analysis TEXT, -- Full ChatGPT response
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contact_conversations (contact_id)
                );
                
                -- All messages organized by contact
                CREATE TABLE IF NOT EXISTS organized_messages (
                    message_id INTEGER PRIMARY KEY,
                    chat_id INTEGER,
                    contact_id TEXT,
                    from_user_id INTEGER,
                    date TEXT,
                    text TEXT,
                    message_type TEXT DEFAULT 'text',
                    is_business_relevant BOOLEAN DEFAULT FALSE,
                    sentiment TEXT,
                    word_count INTEGER DEFAULT 0,
                    contains_opportunities BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contact_conversations (contact_id)
                );
                
                -- Processing status tracking
                CREATE TABLE IF NOT EXISTS processing_status (
                    id INTEGER PRIMARY KEY,
                    stage TEXT,
                    contacts_processed INTEGER DEFAULT 0,
                    total_contacts INTEGER DEFAULT 0,
                    chatgpt_requests_made INTEGER DEFAULT 0,
                    leads_identified INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes
                CREATE INDEX IF NOT EXISTS idx_contact_user_id ON contact_conversations(user_id);
                CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON organized_messages(contact_id);
                CREATE INDEX IF NOT EXISTS idx_leads_probability ON comprehensive_leads(lead_probability);
            """)
        logger.info("✅ Comprehensive database initialized")
    
    async def load_all_telegram_data(self, data_file: str = "data/telegram_extraction_20250709_224424.json"):
        """Load and organize ALL Telegram data"""
        try:
            logger.info(f"📱 Loading complete Telegram data from {data_file}...")
            
            with open(data_file, 'r') as f:
                self.telegram_data = json.load(f)
            
            contacts = self.telegram_data.get('contacts', {})
            messages = self.telegram_data.get('messages', [])
            chats = self.telegram_data.get('chats', {})
            groups = self.telegram_data.get('groups', {})
            
            logger.info(f"📊 Loaded: {len(contacts)} contacts, {len(messages)} messages, {len(chats)} chats, {len(groups)} groups")
            
            # Organize data by contact and group
            await self._organize_by_contact(contacts, messages)
            await self._organize_groups(groups, messages, chats)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading Telegram data: {e}")
            return False
    
    async def _organize_by_contact(self, contacts: Dict, messages: List):
        """Organize all messages by contact with complete conversation history"""
        logger.info("👥 Organizing messages by contact...")
        
        # Group messages by user
        messages_by_user = defaultdict(list)
        for msg in messages:
            user_id = msg.get('from_user_id')
            if user_id and str(user_id) in contacts:
                messages_by_user[user_id].append(msg)
        
        logger.info(f"📊 Found conversations with {len(messages_by_user)} contacts")
        
        # Process each contact's complete conversation
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            processed_count = 0
            for user_id, user_messages in messages_by_user.items():
                try:
                    contact_data = contacts.get(str(user_id), {})
                    contact_id = f"contact_{user_id}"
                    
                    # Skip bots unless business-related
                    if contact_data.get('is_bot', False):
                        continue
                    
                    # Sort messages chronologically
                    user_messages.sort(key=lambda x: x.get('date', ''))
                    
                    # Build complete conversation
                    conversation = self._build_conversation(user_id, contact_data, user_messages)
                    
                    # Store contact conversation
                    cursor.execute("""
                        INSERT OR REPLACE INTO contact_conversations (
                            contact_id, user_id, username, first_name, last_name, phone,
                            total_messages, first_message_date, last_message_date,
                            conversation_text, business_keywords, chat_groups,
                            message_frequency, response_pattern, conversation_length,
                            avg_message_length
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        conversation.contact_id, conversation.user_id,
                        conversation.username, conversation.first_name, conversation.last_name,
                        conversation.phone, conversation.total_messages,
                        conversation.first_message_date, conversation.last_message_date,
                        conversation.conversation_text[:50000],  # Limit for storage
                        json.dumps(conversation.business_keywords or []),
                        json.dumps(conversation.chat_groups or []),
                        json.dumps(conversation.message_frequency or {}),
                        conversation.response_pattern,
                        len(conversation.conversation_text),
                        conversation.total_messages and len(conversation.conversation_text) / conversation.total_messages or 0
                    ))
                    
                    # Store individual messages
                    for msg in user_messages:
                        cursor.execute("""
                            INSERT OR REPLACE INTO organized_messages (
                                message_id, chat_id, contact_id, from_user_id, date,
                                text, message_type, is_business_relevant, sentiment,
                                word_count, contains_opportunities
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            msg.get('message_id'),
                            msg.get('chat_id'),
                            contact_id,
                            user_id,
                            msg.get('date'),
                            msg.get('text', ''),
                            msg.get('message_type', 'text'),
                            msg.get('contains_business_keywords', False),
                            msg.get('sentiment_preliminary', 'neutral'),
                            msg.get('word_count', 0),
                            self._contains_opportunities(msg.get('text', ''))
                        ))
                    
                    self.contacts_conversations[user_id] = conversation
                    processed_count += 1
                    
                    if processed_count % 50 == 0:
                        logger.info(f"📊 Processed {processed_count} contact conversations...")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing contact {user_id}: {e}")
                    continue
            
            conn.commit()
            logger.info(f"✅ Organized {processed_count} contact conversations")
    
    def _build_conversation(self, user_id: int, contact_data: Dict, messages: List) -> ContactConversation:
        """Build complete conversation object for a contact"""
        if not messages:
            return ContactConversation(contact_id=f"contact_{user_id}", user_id=user_id)
        
        # Extract business keywords from all messages
        business_keywords = []
        conversation_parts = []
        chat_groups = set()
        message_frequency = defaultdict(int)
        
        for msg in messages:
            text = msg.get('text', '')
            if text:
                conversation_parts.append(f"[{msg.get('date', '')}] {text}")
                
                # Track business keywords
                if msg.get('contains_business_keywords', False):
                    words = text.lower().split()
                    business_words = [w for w in words if self._is_business_keyword(w)]
                    business_keywords.extend(business_words)
                
                # Track chat groups
                chat_id = msg.get('chat_id')
                if chat_id and chat_id < 0:  # Negative chat_id indicates group
                    chat_groups.add(str(chat_id))
                
                # Message frequency by month
                date_str = msg.get('date', '')
                if date_str:
                    try:
                        month = date_str[:7]  # YYYY-MM
                        message_frequency[month] += 1
                    except:
                        pass
        
        # Build conversation text (limited for ChatGPT processing)
        full_conversation = "\n".join(conversation_parts)
        
        # Truncate if too long (keep last 20,000 chars for recency)
        if len(full_conversation) > 20000:
            full_conversation = "..." + full_conversation[-20000:]
        
        return ContactConversation(
            contact_id=f"contact_{user_id}",
            user_id=user_id,
            username=contact_data.get('username'),
            first_name=contact_data.get('first_name'),
            last_name=contact_data.get('last_name'),
            phone=contact_data.get('phone'),
            total_messages=len(messages),
            first_message_date=messages[0].get('date') if messages else None,
            last_message_date=messages[-1].get('date') if messages else None,
            conversation_text=full_conversation,
            business_keywords=list(set(business_keywords)),
            chat_groups=list(chat_groups),
            message_frequency=dict(message_frequency)
        )
    
    def _is_business_keyword(self, word: str) -> bool:
        """Check if word is business-related"""
        business_words = {
            'business', 'deal', 'partnership', 'collaboration', 'project',
            'investment', 'funding', 'revenue', 'client', 'customer',
            'proposal', 'contract', 'meeting', 'call', 'schedule',
            'budget', 'price', 'cost', 'sale', 'buy', 'sell', 'money',
            'startup', 'company', 'venture', 'opportunity', 'work'
        }
        return word.lower() in business_words
    
    def _contains_opportunities(self, text: str) -> bool:
        """Check if message contains business opportunities"""
        if not text:
            return False
        
        opportunity_phrases = [
            'opportunity', 'interested in', 'partnership', 'collaboration',
            'work together', 'business', 'deal', 'project', 'investment',
            'funding', 'meeting', 'call', 'discuss', 'proposal'
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in opportunity_phrases)
    
    async def _organize_groups(self, groups: Dict, messages: List, chats: Dict):
        """Organize group chat analysis"""
        logger.info("📱 Organizing group chats...")
        
        # Group messages by chat_id for groups
        group_messages = defaultdict(list)
        for msg in messages:
            chat_id = msg.get('chat_id')
            if chat_id and chat_id < 0:  # Negative chat_id = group
                group_messages[chat_id].append(msg)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for chat_id, msgs in group_messages.items():
                try:
                    chat_info = chats.get(str(chat_id), {})
                    group_id = f"group_{abs(chat_id)}"
                    
                    # Analyze group business relevance
                    business_relevance = self._calculate_group_business_relevance(msgs)
                    
                    # Extract key participants and topics
                    participants = set()
                    topics = []
                    
                    for msg in msgs:
                        if msg.get('from_user_id'):
                            participants.add(msg['from_user_id'])
                        
                        if msg.get('contains_business_keywords'):
                            topics.append(msg.get('text', '')[:100])
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO group_conversations (
                            group_id, chat_id, group_title, member_count,
                            total_messages, business_relevance, key_participants,
                            main_topics
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        group_id, chat_id,
                        chat_info.get('title', f'Group {abs(chat_id)}'),
                        len(participants),
                        len(msgs),
                        business_relevance,
                        json.dumps(list(participants)),
                        json.dumps(topics[:20])  # Top 20 business topics
                    ))
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing group {chat_id}: {e}")
            
            conn.commit()
            logger.info(f"✅ Organized {len(group_messages)} group conversations")
    
    def _calculate_group_business_relevance(self, messages: List) -> float:
        """Calculate business relevance score for group"""
        if not messages:
            return 0.0
        
        business_messages = sum(1 for msg in messages if msg.get('contains_business_keywords', False))
        return min(100.0, (business_messages / len(messages)) * 100)
    
    async def analyze_all_contacts_with_chatgpt(self):
        """Analyze ALL contacts with ChatGPT using proper batching"""
        logger.info("🤖 Starting comprehensive ChatGPT analysis...")
        
        # Get all contacts with significant conversations
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT contact_id, user_id, username, first_name, last_name,
                       total_messages, conversation_text, business_keywords
                FROM contact_conversations
                WHERE total_messages >= 3 OR length(business_keywords) > 10
                ORDER BY total_messages DESC
            """)
            contacts_to_analyze = cursor.fetchall()
        
        logger.info(f"🎯 Analyzing {len(contacts_to_analyze)} contacts with ChatGPT...")
        
        # Process in batches to respect rate limits
        leads_found = 0
        for i in range(0, len(contacts_to_analyze), self.batch_size):
            batch = contacts_to_analyze[i:i + self.batch_size]
            logger.info(f"🔄 Processing batch {i//self.batch_size + 1}/{(len(contacts_to_analyze)-1)//self.batch_size + 1}")
            
            # Process each contact in the batch
            for contact in batch:
                lead_analysis = await self._analyze_contact_with_chatgpt(contact)
                if lead_analysis and lead_analysis.is_lead:
                    await self._save_lead_analysis(lead_analysis)
                    leads_found += 1
                
                # Rate limiting
                await asyncio.sleep(self.request_interval)
            
            # Longer pause between batches
            if i + self.batch_size < len(contacts_to_analyze):
                logger.info("⏸️ Pausing 10 seconds between batches...")
                await asyncio.sleep(10)
        
        logger.info(f"✅ ChatGPT analysis complete! Found {leads_found} leads from {len(contacts_to_analyze)} contacts")
        return leads_found
    
    async def _analyze_contact_with_chatgpt(self, contact_data) -> Optional[LeadAnalysis]:
        """Analyze individual contact with ChatGPT"""
        try:
            contact_id, user_id, username, first_name, last_name, total_messages, conversation_text, business_keywords = contact_data
            
            # Build comprehensive prompt
            name = f"{first_name or ''} {last_name or ''}".strip() or username or f"User {user_id}"
            
            prompt = f"""
            Analyze this complete Telegram conversation history to determine if this person is a potential business lead:
            
            CONTACT INFORMATION:
            - Name: {name}
            - Username: @{username or 'None'}
            - Total Messages: {total_messages}
            - Business Keywords Found: {business_keywords}
            
            COMPLETE CONVERSATION HISTORY:
            {conversation_text}
            
            Based on this COMPLETE conversation history, provide a comprehensive business analysis:
            
            1. Is this a potential business lead? (true/false)
            2. Lead probability (0-100): How likely is this person to become a business opportunity?
            3. Estimated value ($): Potential business value if this becomes an opportunity
            4. Stage: prospect/qualified/proposal/negotiation/customer
            5. Opportunity type: What kind of business opportunity do they represent?
            6. Decision makers: Who appears to make decisions in their organization?
            7. Pain points: What business challenges do they have based on conversations?
            8. Timeline: When might they make a decision or need services?
            9. Next action: Specific next step to advance this relationship
            10. Business context: What business/industry are they in?
            11. Conversation quality: professional/casual/mixed
            12. Relationship strength: weak/moderate/strong based on conversation depth
            
            Return ONLY a JSON object:
            {{
                "is_lead": true/false,
                "lead_probability": 0-100,
                "estimated_value": dollar_amount,
                "stage": "stage_name",
                "opportunity_type": "description",
                "decision_makers": ["name1", "name2"],
                "pain_points": ["point1", "point2"],
                "timeline": "timeframe",
                "next_action": "specific_action",
                "business_context": "industry/business_description",
                "conversation_quality": "professional/casual/mixed",
                "relationship_strength": "weak/moderate/strong"
            }}
            """
            
            # Make ChatGPT request
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            analysis_data = json.loads(analysis_text)
            
            # Create lead analysis object
            return LeadAnalysis(
                contact_id=contact_id,
                is_lead=analysis_data.get('is_lead', False),
                lead_probability=analysis_data.get('lead_probability', 0),
                estimated_value=analysis_data.get('estimated_value', 0),
                stage=analysis_data.get('stage', 'prospect'),
                opportunity_type=analysis_data.get('opportunity_type', ''),
                decision_makers=analysis_data.get('decision_makers', []),
                pain_points=analysis_data.get('pain_points', []),
                timeline=analysis_data.get('timeline', ''),
                next_action=analysis_data.get('next_action', ''),
                business_context=analysis_data.get('business_context', ''),
                conversation_quality=analysis_data.get('conversation_quality', 'casual'),
                relationship_strength=analysis_data.get('relationship_strength', 'weak')
            )
            
        except Exception as e:
            logger.error(f"❌ ChatGPT analysis failed for {contact_id}: {e}")
            return None
    
    async def _save_lead_analysis(self, analysis: LeadAnalysis):
        """Save lead analysis to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            lead_id = f"lead_{analysis.contact_id}_{int(time.time())}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO comprehensive_leads (
                    lead_id, contact_id, is_lead, lead_probability, estimated_value,
                    stage, opportunity_type, decision_makers, pain_points,
                    timeline, next_action, business_context, conversation_quality,
                    relationship_strength, chatgpt_analysis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead_id, analysis.contact_id, analysis.is_lead,
                analysis.lead_probability, analysis.estimated_value,
                analysis.stage, analysis.opportunity_type,
                json.dumps(analysis.decision_makers),
                json.dumps(analysis.pain_points),
                analysis.timeline, analysis.next_action,
                analysis.business_context, analysis.conversation_quality,
                analysis.relationship_strength,
                f"Analyzed on {datetime.now().isoformat()}"
            ))
            
            conn.commit()
    
    async def create_comprehensive_google_sheets(self):
        """Create complete Google Sheets with all analysis"""
        logger.info("📊 Creating comprehensive Google Sheets...")
        
        try:
            from setup_personal_google_sheets import PersonalGoogleSheetsManager
            
            manager = PersonalGoogleSheetsManager()
            
            # Authenticate
            if not manager.authenticate():
                logger.error("❌ Google Sheets authentication failed")
                return None
            
            # Create spreadsheet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title = f"Complete Telegram Business Analysis - {timestamp}"
            spreadsheet_id = manager.create_leads_spreadsheet(title)
            
            if not spreadsheet_id:
                logger.error("❌ Failed to create spreadsheet")
                return None
            
            # Upload comprehensive data
            await self._upload_comprehensive_data(manager, spreadsheet_id)
            
            logger.info(f"✅ Complete analysis uploaded to Google Sheets!")
            logger.info(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            
            return spreadsheet_id
            
        except Exception as e:
            logger.error(f"❌ Error creating Google Sheets: {e}")
            return None
    
    async def _upload_comprehensive_data(self, manager, spreadsheet_id):
        """Upload all comprehensive analysis data"""
        with sqlite3.connect(self.db_path) as conn:
            # Get comprehensive leads
            leads_df = pd.read_sql_query("""
                SELECT 
                    cl.lead_probability,
                    cl.estimated_value,
                    cl.stage,
                    cl.opportunity_type,
                    cl.business_context,
                    cl.conversation_quality,
                    cl.relationship_strength,
                    cl.timeline,
                    cl.next_action,
                    cl.decision_makers,
                    cl.pain_points,
                    cc.first_name,
                    cc.last_name,
                    cc.username,
                    cc.phone,
                    cc.total_messages,
                    cc.conversation_length,
                    cc.business_keywords
                FROM comprehensive_leads cl
                JOIN contact_conversations cc ON cl.contact_id = cc.contact_id
                WHERE cl.is_lead = TRUE
                ORDER BY cl.lead_probability DESC
            """, conn)
            
            # Get all contacts
            contacts_df = pd.read_sql_query("""
                SELECT 
                    first_name,
                    last_name,
                    username,
                    phone,
                    total_messages,
                    conversation_length,
                    business_keywords,
                    first_message_date,
                    last_message_date
                FROM contact_conversations
                ORDER BY total_messages DESC
            """, conn)
            
            # Get group analysis
            groups_df = pd.read_sql_query("""
                SELECT 
                    group_title,
                    member_count,
                    total_messages,
                    business_relevance,
                    main_topics
                FROM group_conversations
                ORDER BY business_relevance DESC
            """, conn)
        
        # Create comprehensive worksheets
        self._create_comprehensive_leads_sheet(manager, spreadsheet_id, leads_df)
        self._create_all_contacts_sheet(manager, spreadsheet_id, contacts_df)
        self._create_groups_analysis_sheet(manager, spreadsheet_id, groups_df)
        self._create_executive_dashboard(manager, spreadsheet_id, leads_df, contacts_df, groups_df)
    
    def _create_comprehensive_leads_sheet(self, manager, spreadsheet_id, leads_df):
        """Create comprehensive leads worksheet"""
        # Rename first sheet to leads
        manager.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': 0,
                            'title': '🎯 AI-Identified Business Leads'
                        },
                        'fields': 'title'
                    }
                }]
            }
        ).execute()
        
        # Prepare comprehensive headers
        headers = [
            'Lead Score', 'Est. Value', 'Stage', 'Opportunity Type',
            'Business Context', 'Relationship', 'Conversation Quality',
            'Timeline', 'Next Action', 'Decision Makers', 'Pain Points',
            'Name', 'Username', 'Phone', 'Total Messages', 'Conv. Length'
        ]
        
        values = [headers]
        for _, row in leads_df.iterrows():
            name = f"{row['first_name'] or ''} {row['last_name'] or ''}".strip()
            values.append([
                f"{row['lead_probability']}/100",
                f"${row['estimated_value']:,.0f}",
                row['stage'],
                row['opportunity_type'],
                row['business_context'],
                row['relationship_strength'],
                row['conversation_quality'],
                row['timeline'],
                row['next_action'],
                row['decision_makers'],
                row['pain_points'],
                name,
                f"@{row['username']}" if row['username'] else '',
                row['phone'] or '',
                row['total_messages'],
                f"{row['conversation_length']:,} chars"
            ])
        
        body = {'values': values}
        manager.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='🎯 AI-Identified Business Leads!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _create_all_contacts_sheet(self, manager, spreadsheet_id, contacts_df):
        """Create all contacts analysis sheet"""
        # Add sheet for all contacts
        manager.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': '👥 Complete Contact Database'
                        }
                    }
                }]
            }
        ).execute()
        
        headers = [
            'Name', 'Username', 'Phone', 'Total Messages', 'Conversation Length',
            'Business Keywords', 'First Contact', 'Last Contact'
        ]
        
        values = [headers]
        for _, row in contacts_df.iterrows():
            name = f"{row['first_name'] or ''} {row['last_name'] or ''}".strip()
            values.append([
                name,
                f"@{row['username']}" if row['username'] else '',
                row['phone'] or '',
                row['total_messages'],
                f"{row['conversation_length']:,} chars",
                row['business_keywords'],
                row['first_message_date'] or '',
                row['last_message_date'] or ''
            ])
        
        body = {'values': values}
        manager.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='👥 Complete Contact Database!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _create_groups_analysis_sheet(self, manager, spreadsheet_id, groups_df):
        """Create group chats analysis sheet"""
        # Add sheet for groups
        manager.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': '📱 Group Chats Analysis'
                        }
                    }
                }]
            }
        ).execute()
        
        headers = [
            'Group Name', 'Members', 'Total Messages', 'Business Relevance (%)',
            'Main Business Topics'
        ]
        
        values = [headers]
        for _, row in groups_df.iterrows():
            values.append([
                row['group_title'],
                row['member_count'],
                row['total_messages'],
                f"{row['business_relevance']:.1f}%",
                str(row['main_topics'])[:200] + "..." if len(str(row['main_topics'])) > 200 else str(row['main_topics'])
            ])
        
        body = {'values': values}
        manager.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='📱 Group Chats Analysis!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _create_executive_dashboard(self, manager, spreadsheet_id, leads_df, contacts_df, groups_df):
        """Create executive dashboard"""
        # Add dashboard sheet
        manager.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': '📊 Executive Dashboard'
                        }
                    }
                }]
            }
        ).execute()
        
        # Calculate comprehensive metrics
        total_contacts = len(contacts_df)
        total_leads = len(leads_df)
        total_pipeline = leads_df['estimated_value'].sum() if not leads_df.empty else 0
        avg_lead_score = leads_df['lead_probability'].mean() if not leads_df.empty else 0
        qualified_leads = len(leads_df[leads_df['stage'] == 'qualified']) if not leads_df.empty else 0
        strong_relationships = len(leads_df[leads_df['relationship_strength'] == 'strong']) if not leads_df.empty else 0
        
        dashboard_data = [
            ['📊 COMPREHENSIVE TELEGRAM BUSINESS INTELLIGENCE', ''],
            ['', ''],
            ['📈 EXECUTIVE SUMMARY', ''],
            ['Total Contacts Analyzed', total_contacts],
            ['AI-Identified Business Leads', total_leads],
            ['Qualified Leads (Ready to Contact)', qualified_leads],
            ['Strong Relationships Identified', strong_relationships],
            [f'Total Pipeline Value', f'${total_pipeline:,.0f}'],
            ['Average Lead Score', f'{avg_lead_score:.1f}/100'],
            ['', ''],
            ['🎯 TOP BUSINESS OPPORTUNITIES', '']
        ]
        
        # Add top leads
        if not leads_df.empty:
            for i, (_, lead) in enumerate(leads_df.head(10).iterrows()):
                name = f"{lead['first_name'] or ''} {lead['last_name'] or ''}".strip()
                if not name:
                    name = f"@{lead['username']}" if lead['username'] else 'Unknown'
                dashboard_data.append([
                    f"{i+1}. {name}",
                    f"Score: {lead['lead_probability']}/100, Value: ${lead['estimated_value']:,.0f}, Context: {lead['business_context']}"
                ])
        
        dashboard_data.extend([
            ['', ''],
            ['📅 Analysis Completed', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['🔗 Data Source', 'Complete Telegram Chat History'],
            ['🤖 Analysis Method', 'AI-Powered with ChatGPT'],
            ['💬 Total Messages Analyzed', sum(contacts_df['total_messages']) if not contacts_df.empty else 0],
            ['📱 Group Chats Analyzed', len(groups_df)]
        ])
        
        body = {'values': dashboard_data}
        manager.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='📊 Executive Dashboard!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

async def main():
    """Run comprehensive Telegram analysis"""
    print("🚀 COMPREHENSIVE TELEGRAM BUSINESS ANALYSIS")
    print("=" * 60)
    print("📱 Processing ALL your Telegram chats organized by contact")
    print("🤖 Using ChatGPT for complete conversation analysis")
    print("📊 Creating comprehensive Google Sheets database")
    print()
    
    analyzer = ComprehensiveTelegramAnalyzer()
    
    # Step 1: Load and organize all data
    print("📱 Step 1: Loading and organizing ALL Telegram data...")
    if not await analyzer.load_all_telegram_data():
        print("❌ Failed to load Telegram data")
        return
    
    print(f"✅ Organized conversations for {len(analyzer.contacts_conversations)} contacts")
    
    # Step 2: Comprehensive ChatGPT analysis
    print("\n🤖 Step 2: Analyzing ALL contacts with ChatGPT...")
    print("⏱️ This will take time to respect API rate limits...")
    leads_found = await analyzer.analyze_all_contacts_with_chatgpt()
    
    # Step 3: Create comprehensive Google Sheets
    print(f"\n📊 Step 3: Creating comprehensive Google Sheets...")
    spreadsheet_id = await analyzer.create_comprehensive_google_sheets()
    
    if spreadsheet_id:
        print("\n🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
        print(f"📊 Found {leads_found} business leads from your complete Telegram history")
        print(f"🔗 Google Sheets: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print("\n📋 Your spreadsheet includes:")
        print("   • 🎯 AI-Identified Business Leads - Complete ChatGPT analysis")
        print("   • 👥 Complete Contact Database - All contacts organized") 
        print("   • 📱 Group Chats Analysis - Business-relevant groups")
        print("   • 📊 Executive Dashboard - Key metrics and insights")
    else:
        print("❌ Failed to create Google Sheets")

if __name__ == "__main__":
    asyncio.run(main()) 