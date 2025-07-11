#!/usr/bin/env python3
"""
Telegram Lead Analysis System
============================
Analyzes your actual Telegram chat history to identify real business leads
and organize them into proper databases for tracking and Google Sheets sync.

Features:
- Load your real Telegram data (10,028 messages, 311 contacts)
- AI-powered lead identification and scoring
- Separate contacts database vs leads database
- Business opportunity analysis
- Google Sheets integration
- Lead tracking and pipeline management
"""

import json
import sqlite3
import logging
import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_lead_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TelegramContact:
    user_id: int
    username: str = None
    first_name: str = None
    last_name: str = None
    phone: str = None
    is_verified: bool = False
    is_premium: bool = False
    is_bot: bool = False
    last_seen: str = None
    message_count: int = 0
    business_score: float = 0.0
    lead_probability: float = 0.0
    business_keywords: List[str] = None
    conversation_topics: List[str] = None

@dataclass
class BusinessLead:
    contact_id: str
    user_id: int
    lead_score: float
    estimated_value: float
    probability: float
    stage: str
    opportunity_type: str
    decision_makers: List[str]
    pain_points: List[str]
    timeline: str
    next_action: str
    source: str = "telegram"

class TelegramLeadAnalyzer:
    """Analyze Telegram data to identify and score business leads"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.db_path = Path("data/telegram_leads.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize the leads tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- All contacts from Telegram
                CREATE TABLE IF NOT EXISTS telegram_contacts (
                    contact_id TEXT PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_premium BOOLEAN DEFAULT FALSE,
                    is_bot BOOLEAN DEFAULT FALSE,
                    last_seen TEXT,
                    message_count INTEGER DEFAULT 0,
                    business_score REAL DEFAULT 0.0,
                    lead_probability REAL DEFAULT 0.0,
                    business_keywords TEXT, -- JSON array
                    conversation_topics TEXT, -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Business leads identified from contacts
                CREATE TABLE IF NOT EXISTS business_leads (
                    lead_id TEXT PRIMARY KEY,
                    contact_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    lead_score REAL DEFAULT 0.0,
                    estimated_value REAL DEFAULT 0.0,
                    probability REAL DEFAULT 0.0,
                    stage TEXT DEFAULT 'prospect',
                    opportunity_type TEXT,
                    decision_makers TEXT, -- JSON array
                    pain_points TEXT, -- JSON array
                    timeline TEXT,
                    next_action TEXT,
                    source TEXT DEFAULT 'telegram',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES telegram_contacts (contact_id)
                );
                
                -- Conversation analysis
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    chat_id INTEGER,
                    contact_id TEXT,
                    message_count INTEGER DEFAULT 0,
                    business_relevance REAL DEFAULT 0.0,
                    sentiment_overall TEXT,
                    key_topics TEXT, -- JSON array
                    opportunities_mentioned TEXT, -- JSON array
                    last_activity TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES telegram_contacts (contact_id)
                );
                
                -- Messages with business analysis
                CREATE TABLE IF NOT EXISTS analyzed_messages (
                    message_id INTEGER PRIMARY KEY,
                    chat_id INTEGER,
                    from_user_id INTEGER,
                    contact_id TEXT,
                    date TIMESTAMP,
                    text TEXT,
                    message_type TEXT,
                    contains_business_keywords BOOLEAN DEFAULT FALSE,
                    is_question BOOLEAN DEFAULT FALSE,
                    sentiment_preliminary TEXT,
                    word_count INTEGER DEFAULT 0,
                    has_contact_info BOOLEAN DEFAULT FALSE,
                    business_relevance_score REAL DEFAULT 0.0,
                    opportunity_indicators TEXT, -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES telegram_contacts (contact_id)
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON telegram_contacts(user_id);
                CREATE INDEX IF NOT EXISTS idx_contacts_business_score ON telegram_contacts(business_score);
                CREATE INDEX IF NOT EXISTS idx_leads_score ON business_leads(lead_score);
                CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON analyzed_messages(chat_id);
                CREATE INDEX IF NOT EXISTS idx_messages_user_id ON analyzed_messages(from_user_id);
            """)
            
        logger.info("✅ Telegram leads database initialized")
    
    async def load_telegram_data(self, data_file: str = "data/telegram_extraction_20250709_224424.json"):
        """Load and analyze your actual Telegram data"""
        try:
            logger.info(f"📱 Loading Telegram data from {data_file}...")
            
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            contacts = data.get('contacts', {})
            messages = data.get('messages', [])
            chats = data.get('chats', {})
            stats = data.get('extraction_stats', {})
            
            logger.info(f"📊 Found {len(contacts)} contacts, {len(messages)} messages, {len(chats)} chats")
            
            # Process contacts
            await self._process_contacts(contacts, messages)
            
            # Process messages
            await self._process_messages(messages, contacts)
            
            # Analyze for business leads
            await self._analyze_business_leads()
            
            # Generate summary
            summary = await self._generate_analysis_summary()
            
            logger.info("✅ Telegram data analysis complete!")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error loading Telegram data: {e}")
            return None
    
    async def _process_contacts(self, contacts: Dict, messages: List):
        """Process and analyze all contacts"""
        logger.info("👥 Processing contacts...")
        
        # Count messages per user
        message_counts = {}
        for msg in messages:
            user_id = msg.get('from_user_id')
            if user_id:
                message_counts[user_id] = message_counts.get(user_id, 0) + 1
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            processed_count = 0
            for user_id_str, contact_data in contacts.items():
                try:
                    user_id = int(user_id_str)
                    contact_id = f"contact_{user_id}"
                    
                    # Skip bots unless they're business-related
                    if contact_data.get('is_bot', False):
                        continue
                    
                    message_count = message_counts.get(user_id, 0)
                    
                    # Calculate preliminary business score
                    business_score = self._calculate_preliminary_business_score(contact_data, message_count)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO telegram_contacts (
                            contact_id, user_id, username, first_name, last_name,
                            phone, is_verified, is_premium, is_bot, last_seen,
                            message_count, business_score, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        contact_id, user_id,
                        contact_data.get('username'),
                        contact_data.get('first_name'),
                        contact_data.get('last_name'),
                        contact_data.get('phone'),
                        contact_data.get('is_verified', False),
                        contact_data.get('is_premium', False),
                        contact_data.get('is_bot', False),
                        contact_data.get('last_seen'),
                        message_count,
                        business_score,
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing contact {user_id_str}: {e}")
                    continue
            
            conn.commit()
            logger.info(f"✅ Processed {processed_count} contacts")
    
    async def _process_messages(self, messages: List, contacts: Dict):
        """Process and analyze all messages"""
        logger.info("💬 Processing messages...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            processed_count = 0
            for msg in messages:
                try:
                    user_id = msg.get('from_user_id')
                    if not user_id or user_id not in contacts:
                        continue
                    
                    contact_id = f"contact_{user_id}"
                    
                    # Enhanced business relevance scoring
                    business_relevance = self._calculate_message_business_relevance(msg)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO analyzed_messages (
                            message_id, chat_id, from_user_id, contact_id, date,
                            text, message_type, contains_business_keywords,
                            is_question, sentiment_preliminary, word_count,
                            has_contact_info, business_relevance_score, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        msg.get('message_id'),
                        msg.get('chat_id'),
                        user_id,
                        contact_id,
                        msg.get('date'),
                        msg.get('text', ''),
                        msg.get('message_type', 'text'),
                        msg.get('contains_business_keywords', False),
                        msg.get('is_question', False),
                        msg.get('sentiment_preliminary', 'neutral'),
                        msg.get('word_count', 0),
                        msg.get('has_contact_info', False),
                        business_relevance,
                        datetime.now()
                    ))
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing message: {e}")
                    continue
            
            conn.commit()
            logger.info(f"✅ Processed {processed_count} messages")
    
    def _calculate_preliminary_business_score(self, contact_data: Dict, message_count: int) -> float:
        """Calculate preliminary business score based on available data"""
        score = 0.0
        
        # Message activity (0-30 points)
        if message_count > 0:
            score += min(30, message_count * 2)
        
        # Verification status (10 points)
        if contact_data.get('is_verified', False):
            score += 10
        
        # Premium status (5 points) 
        if contact_data.get('is_premium', False):
            score += 5
        
        # Has username (5 points)
        if contact_data.get('username'):
            score += 5
        
        # Has full name (10 points)
        if contact_data.get('first_name') and contact_data.get('last_name'):
            score += 10
        
        # Has phone (15 points)
        if contact_data.get('phone'):
            score += 15
        
        return min(100.0, score)
    
    def _calculate_message_business_relevance(self, msg: Dict) -> float:
        """Calculate business relevance score for a message"""
        score = 0.0
        
        # Existing business indicators
        if msg.get('contains_business_keywords', False):
            score += 30
        
        if msg.get('has_contact_info', False):
            score += 20
        
        if msg.get('is_question', False):
            score += 10
        
        # Sentiment analysis
        sentiment = msg.get('sentiment_preliminary', 'neutral')
        if sentiment == 'positive':
            score += 10
        elif sentiment == 'negative':
            score += 5  # Even negative can be business-relevant
        
        # Message length (longer messages often more business-relevant)
        word_count = msg.get('word_count', 0)
        if word_count > 20:
            score += 10
        elif word_count > 10:
            score += 5
        
        # Business keywords in text
        text = msg.get('text', '').lower()
        business_keywords = [
            'business', 'deal', 'partnership', 'collaboration', 'project',
            'investment', 'funding', 'revenue', 'client', 'customer',
            'proposal', 'contract', 'meeting', 'call', 'schedule',
            'budget', 'price', 'cost', 'sale', 'buy', 'sell'
        ]
        
        keyword_matches = sum(1 for keyword in business_keywords if keyword in text)
        score += min(25, keyword_matches * 5)
        
        return min(100.0, score)
    
    async def _analyze_business_leads(self):
        """Use AI to analyze contacts and identify business leads"""
        if not self.openai_api_key:
            logger.warning("⚠️ No OpenAI API key - using heuristic lead scoring")
            await self._heuristic_lead_analysis()
            return
        
        logger.info("🤖 Analyzing contacts with AI for lead identification...")
        
        # Get high-scoring contacts for AI analysis
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get contacts with business_score > 30 or message_count > 5
            cursor.execute("""
                SELECT c.*, 
                       GROUP_CONCAT(m.text, ' | ') as sample_messages,
                       AVG(m.business_relevance_score) as avg_business_relevance
                FROM telegram_contacts c
                LEFT JOIN analyzed_messages m ON c.contact_id = m.contact_id
                WHERE c.business_score > 30 OR c.message_count > 5
                GROUP BY c.contact_id
                ORDER BY c.business_score DESC
                LIMIT 50
            """)
            
            candidates = cursor.fetchall()
            logger.info(f"🎯 Analyzing {len(candidates)} high-potential contacts with AI...")
            
            # Process in batches for AI analysis
            for candidate in candidates:
                await self._ai_analyze_contact(candidate)
    
    async def _ai_analyze_contact(self, contact_data):
        """Analyze individual contact with AI to determine if they're a lead"""
        try:
            if not self.openai_api_key:
                return
            
            import openai
            openai.api_key = self.openai_api_key
            
            # Prepare context for AI analysis
            contact_info = {
                'name': f"{contact_data[3] or ''} {contact_data[4] or ''}".strip(),
                'username': contact_data[2],
                'is_verified': contact_data[6],
                'is_premium': contact_data[7],
                'message_count': contact_data[10],
                'business_score': contact_data[11],
                'sample_messages': contact_data[13] or '',
                'avg_business_relevance': contact_data[14] or 0
            }
            
            # AI prompt for lead analysis
            prompt = f"""
            Analyze this Telegram contact to determine if they are a potential business lead:
            
            Contact Information:
            - Name: {contact_info['name']}
            - Username: @{contact_info['username'] or 'None'}
            - Verified: {contact_info['is_verified']}
            - Premium: {contact_info['is_premium']}
            - Message Count: {contact_info['message_count']}
            - Business Score: {contact_info['business_score']}/100
            - Average Business Relevance: {contact_info['avg_business_relevance']}/100
            
            Sample Messages: {contact_info['sample_messages'][:500]}...
            
            Based on this information, assess:
            1. Lead Probability (0-100): How likely is this a business lead?
            2. Estimated Value ($): Potential business value if converted
            3. Stage: prospect/qualified/proposal/negotiation
            4. Opportunity Type: What kind of business opportunity?
            5. Decision Makers: Who appears to be decision makers?
            6. Pain Points: What business problems do they have?
            7. Timeline: When might they make a decision?
            8. Next Action: What should be the next step?
            
            Return ONLY a JSON object with these fields:
            {{
                "is_lead": true/false,
                "lead_probability": 0-100,
                "estimated_value": dollar_amount,
                "stage": "stage_name",
                "opportunity_type": "description",
                "decision_makers": ["name1", "name2"],
                "pain_points": ["point1", "point2"],
                "timeline": "timeframe",
                "next_action": "specific_action"
            }}
            """
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # Parse AI response
            ai_analysis = json.loads(response.choices[0].message.content)
            
            # If AI identifies as lead, create lead record
            if ai_analysis.get('is_lead', False) and ai_analysis.get('lead_probability', 0) > 50:
                await self._create_lead_record(contact_data, ai_analysis)
                
        except Exception as e:
            logger.error(f"❌ Error in AI analysis for contact {contact_data[0]}: {e}")
    
    async def _heuristic_lead_analysis(self):
        """Fallback heuristic analysis when no AI available"""
        logger.info("📊 Using heuristic analysis for lead identification...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Heuristic rules for lead identification
            cursor.execute("""
                SELECT * FROM telegram_contacts 
                WHERE (business_score > 60 OR message_count > 10)
                AND is_bot = FALSE
                ORDER BY business_score DESC
            """)
            
            candidates = cursor.fetchall()
            
            for candidate in candidates:
                # Simple heuristic scoring
                lead_probability = min(90, candidate[11] + (candidate[10] * 2))  # business_score + message_count*2
                
                if lead_probability > 70:
                    estimated_value = min(100000, lead_probability * 1000)  # Simple value estimation
                    
                    heuristic_analysis = {
                        'is_lead': True,
                        'lead_probability': lead_probability,
                        'estimated_value': estimated_value,
                        'stage': 'prospect',
                        'opportunity_type': 'General Business Opportunity',
                        'decision_makers': [f"{candidate[3] or ''} {candidate[4] or ''}".strip()],
                        'pain_points': ['To be determined'],
                        'timeline': '3-6 months',
                        'next_action': 'Schedule follow-up conversation'
                    }
                    
                    await self._create_lead_record(candidate, heuristic_analysis)
    
    async def _create_lead_record(self, contact_data, analysis: Dict):
        """Create a lead record in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                lead_id = f"lead_{contact_data[1]}_{int(datetime.now().timestamp())}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO business_leads (
                        lead_id, contact_id, user_id, lead_score, estimated_value,
                        probability, stage, opportunity_type, decision_makers,
                        pain_points, timeline, next_action, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead_id,
                    contact_data[0],  # contact_id
                    contact_data[1],  # user_id
                    analysis.get('lead_probability', 0),
                    analysis.get('estimated_value', 0),
                    analysis.get('lead_probability', 0),
                    analysis.get('stage', 'prospect'),
                    analysis.get('opportunity_type', ''),
                    json.dumps(analysis.get('decision_makers', [])),
                    json.dumps(analysis.get('pain_points', [])),
                    analysis.get('timeline', ''),
                    analysis.get('next_action', ''),
                    datetime.now(),
                    datetime.now()
                ))
                
                conn.commit()
                logger.info(f"✅ Created lead record: {lead_id}")
                
        except Exception as e:
            logger.error(f"❌ Error creating lead record: {e}")
    
    async def _generate_analysis_summary(self) -> Dict[str, Any]:
        """Generate summary of the analysis"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM telegram_contacts")
            total_contacts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM business_leads")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analyzed_messages")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(business_score) FROM telegram_contacts WHERE business_score > 0")
            avg_business_score = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(estimated_value) FROM business_leads")
            total_pipeline_value = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT stage, COUNT(*), AVG(estimated_value)
                FROM business_leads 
                GROUP BY stage
            """)
            pipeline_by_stage = cursor.fetchall()
            
            # Top leads
            cursor.execute("""
                SELECT c.first_name, c.last_name, c.username, l.lead_score, l.estimated_value, l.stage
                FROM business_leads l
                JOIN telegram_contacts c ON l.contact_id = c.contact_id
                ORDER BY l.lead_score DESC
                LIMIT 10
            """)
            top_leads = cursor.fetchall()
            
            summary = {
                'total_contacts': total_contacts,
                'total_leads': total_leads,
                'total_messages': total_messages,
                'avg_business_score': round(avg_business_score, 2),
                'total_pipeline_value': total_pipeline_value,
                'pipeline_by_stage': pipeline_by_stage,
                'top_leads': top_leads,
                'analysis_date': datetime.now().isoformat()
            }
            
            return summary
    
    async def export_to_google_sheets(self):
        """Export leads data to Google Sheets"""
        try:
            logger.info("📊 Exporting to Google Sheets...")
            
            # Export to CSV first
            await self.export_to_csv()
            
            # If Google Sheets service is available, sync there too
            google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
            if google_sheet_id:
                # Use existing Google Sheets integration
                from core.real_google_sheets_exporter import RealGoogleSheetsExporter
                exporter = RealGoogleSheetsExporter()
                
                # Export leads and contacts
                await exporter.export_leads_data(self.db_path)
                logger.info("✅ Exported to Google Sheets")
            else:
                logger.info("ℹ️ Google Sheets ID not configured - CSV export completed")
                
        except Exception as e:
            logger.error(f"❌ Error exporting to Google Sheets: {e}")
    
    async def export_to_csv(self):
        """Export data to CSV files"""
        try:
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with sqlite3.connect(self.db_path) as conn:
                # Export contacts
                contacts_df = pd.read_sql_query("""
                    SELECT contact_id, user_id, username, first_name, last_name,
                           phone, is_verified, is_premium, message_count, business_score
                    FROM telegram_contacts
                    ORDER BY business_score DESC
                """, conn)
                contacts_df.to_csv(export_dir / f"telegram_contacts_{timestamp}.csv", index=False)
                
                # Export leads
                leads_df = pd.read_sql_query("""
                    SELECT l.*, c.first_name, c.last_name, c.username, c.phone
                    FROM business_leads l
                    JOIN telegram_contacts c ON l.contact_id = c.contact_id
                    ORDER BY l.lead_score DESC
                """, conn)
                leads_df.to_csv(export_dir / f"business_leads_{timestamp}.csv", index=False)
                
                # Export messages with high business relevance
                messages_df = pd.read_sql_query("""
                    SELECT m.*, c.first_name, c.last_name, c.username
                    FROM analyzed_messages m
                    JOIN telegram_contacts c ON m.contact_id = c.contact_id
                    WHERE m.business_relevance_score > 50
                    ORDER BY m.business_relevance_score DESC
                """, conn)
                messages_df.to_csv(export_dir / f"business_messages_{timestamp}.csv", index=False)
                
            logger.info(f"✅ Exported data to CSV files in {export_dir}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting to CSV: {e}")

async def main():
    """Main function to run the analysis"""
    load_dotenv()
    
    print("🚀 Telegram Lead Analysis System")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = TelegramLeadAnalyzer()
    
    # Load and analyze data
    print("\n📱 Step 1: Loading your Telegram data...")
    summary = await analyzer.load_telegram_data()
    
    if summary:
        print("\n📊 Analysis Summary:")
        print(f"   👥 Total Contacts: {summary['total_contacts']}")
        print(f"   🎯 Identified Leads: {summary['total_leads']}")
        print(f"   💬 Analyzed Messages: {summary['total_messages']}")
        print(f"   📈 Average Business Score: {summary['avg_business_score']}/100")
        print(f"   💰 Total Pipeline Value: ${summary['total_pipeline_value']:,.2f}")
        
        if summary['top_leads']:
            print(f"\n🏆 Top {len(summary['top_leads'])} Leads:")
            for i, lead in enumerate(summary['top_leads'], 1):
                name = f"{lead[0] or ''} {lead[1] or ''}".strip() or f"@{lead[2]}" or "Unknown"
                print(f"   {i}. {name} - Score: {lead[3]}/100, Value: ${lead[4]:,.0f}, Stage: {lead[5]}")
        
        print("\n📊 Step 2: Exporting to Google Sheets...")
        await analyzer.export_to_google_sheets()
        
        print("\n✅ Analysis Complete!")
        print(f"   📁 Database: data/telegram_leads.db")
        print(f"   📊 CSV Exports: exports/")
        print(f"   📈 Google Sheets: {os.getenv('GOOGLE_SHEET_ID', 'Not configured')}")
        
    else:
        print("❌ Analysis failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main()) 