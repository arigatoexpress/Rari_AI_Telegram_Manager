#!/usr/bin/env python3
"""
Comprehensive Message Database System
===================================
Organizes ALL 10,028 Telegram messages by chat and group chat 
with rich analytical data for comprehensive analysis.

Features:
- Complete message database organized by chat/group
- Rich analytical metadata per message and chat
- Chat timeline and conversation flow analysis
- Participant analysis and interaction patterns
- Message content analysis and categorization
- Export capabilities for further analysis
"""

import json
import sqlite3
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pandas as pd
from collections import defaultdict, Counter
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/comprehensive_message_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveMessageDatabase:
    """Comprehensive message database with rich analytics"""
    
    def __init__(self):
        self.db_path = Path("data/comprehensive_message_database.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.telegram_data = None
        self._init_database()
        
    def _init_database(self):
        """Initialize comprehensive message database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Chat metadata and analytics
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    chat_type TEXT, -- 'private', 'group', 'supergroup', 'channel'
                    title TEXT,
                    username TEXT,
                    participant_count INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    first_message_date TEXT,
                    last_message_date TEXT,
                    activity_days INTEGER DEFAULT 0,
                    avg_messages_per_day REAL DEFAULT 0,
                    top_participants TEXT, -- JSON array
                    message_types TEXT, -- JSON object with counts
                    business_relevance_score REAL DEFAULT 0,
                    sentiment_distribution TEXT, -- JSON object
                    conversation_themes TEXT, -- JSON array
                    peak_activity_hours TEXT, -- JSON array
                    is_pinned BOOLEAN DEFAULT FALSE,
                    unread_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Complete message database with rich metadata
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER,
                    chat_id INTEGER,
                    from_user_id INTEGER,
                    date TEXT,
                    text TEXT,
                    message_type TEXT DEFAULT 'text',
                    is_reply BOOLEAN DEFAULT FALSE,
                    is_forwarded BOOLEAN DEFAULT FALSE,
                    views INTEGER DEFAULT 0,
                    edit_date TEXT,
                    
                    -- Rich analytical data
                    contains_business_keywords BOOLEAN DEFAULT FALSE,
                    is_question BOOLEAN DEFAULT FALSE,
                    sentiment_preliminary TEXT,
                    word_count INTEGER DEFAULT 0,
                    has_contact_info BOOLEAN DEFAULT FALSE,
                    
                    -- Additional analytics
                    message_length_category TEXT, -- 'short', 'medium', 'long'
                    time_of_day TEXT, -- 'morning', 'afternoon', 'evening', 'night'
                    day_of_week TEXT,
                    response_time_minutes INTEGER, -- Time to respond to previous message
                    conversation_thread_id INTEGER, -- Groups related messages
                    message_sequence_number INTEGER, -- Order in chat
                    contains_media BOOLEAN DEFAULT FALSE,
                    contains_links BOOLEAN DEFAULT FALSE,
                    mentions_count INTEGER DEFAULT 0,
                    engagement_score REAL DEFAULT 0, -- Based on replies, reactions, etc.
                    
                    -- Content categorization
                    content_category TEXT, -- 'business', 'casual', 'technical', 'social'
                    topic_keywords TEXT, -- JSON array
                    entities_mentioned TEXT, -- JSON array (people, places, organizations)
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    PRIMARY KEY (message_id, chat_id),
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
                );
                
                -- Participant analysis per chat
                CREATE TABLE IF NOT EXISTS chat_participants (
                    chat_id INTEGER,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    message_count INTEGER DEFAULT 0,
                    first_message_date TEXT,
                    last_message_date TEXT,
                    avg_message_length REAL DEFAULT 0,
                    response_rate REAL DEFAULT 0, -- Percentage of messages that are responses
                    initiation_rate REAL DEFAULT 0, -- Percentage of conversations started
                    activity_pattern TEXT, -- JSON object with hourly activity
                    engagement_level TEXT, -- 'high', 'medium', 'low'
                    role_in_chat TEXT, -- 'admin', 'active_participant', 'lurker', 'occasional'
                    
                    PRIMARY KEY (chat_id, user_id),
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
                );
                
                -- Conversation threads and topics
                CREATE TABLE IF NOT EXISTS conversation_threads (
                    thread_id INTEGER PRIMARY KEY,
                    chat_id INTEGER,
                    start_message_id INTEGER,
                    end_message_id INTEGER,
                    participant_count INTEGER,
                    message_count INTEGER,
                    duration_minutes INTEGER,
                    topic_summary TEXT,
                    main_participants TEXT, -- JSON array
                    thread_type TEXT, -- 'discussion', 'announcement', 'question_answer'
                    business_relevance REAL DEFAULT 0,
                    
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
                );
                
                -- Chat analytics and insights
                CREATE TABLE IF NOT EXISTS chat_analytics (
                    chat_id INTEGER PRIMARY KEY,
                    daily_message_stats TEXT, -- JSON object {date: count}
                    hourly_activity_pattern TEXT, -- JSON array [24 hours]
                    weekly_pattern TEXT, -- JSON array [7 days] 
                    most_active_periods TEXT, -- JSON array
                    conversation_starters TEXT, -- JSON array of user_ids
                    response_champions TEXT, -- JSON array of user_ids
                    topic_evolution TEXT, -- JSON array showing topic changes over time
                    sentiment_trends TEXT, -- JSON object with sentiment over time
                    engagement_trends TEXT, -- JSON object with engagement metrics
                    business_opportunity_moments TEXT, -- JSON array of high-value message_ids
                    
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
                );
                
                -- Contact information enrichment
                CREATE TABLE IF NOT EXISTS contacts_enriched (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_premium BOOLEAN DEFAULT FALSE,
                    is_bot BOOLEAN DEFAULT FALSE,
                    total_chats INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    avg_response_time_minutes REAL DEFAULT 0,
                    communication_style TEXT, -- 'formal', 'casual', 'technical'
                    activity_level TEXT, -- 'very_active', 'active', 'moderate', 'occasional'
                    preferred_times TEXT, -- JSON array of active hours
                    business_interest_score REAL DEFAULT 0,
                    relationship_strength TEXT -- 'strong', 'moderate', 'weak'
                );
                
                -- Create comprehensive indexes
                CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
                CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(from_user_id);
                CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date);
                CREATE INDEX IF NOT EXISTS idx_messages_business ON messages(contains_business_keywords);
                CREATE INDEX IF NOT EXISTS idx_messages_sentiment ON messages(sentiment_preliminary);
                CREATE INDEX IF NOT EXISTS idx_chat_participants_user ON chat_participants(user_id);
                CREATE INDEX IF NOT EXISTS idx_chat_participants_chat ON chat_participants(chat_id);
            """)
            
        logger.info("✅ Comprehensive message database initialized")

    def load_telegram_data(self, data_file: str = "data/telegram_extraction_20250709_224424.json"):
        """Load all Telegram data for processing"""
        try:
            logger.info(f"📱 Loading complete Telegram data from {data_file}...")
            
            with open(data_file, 'r') as f:
                self.telegram_data = json.load(f)
            
            contacts = self.telegram_data.get('contacts', {})
            messages = self.telegram_data.get('messages', [])
            chats = self.telegram_data.get('chats', {})
            groups = self.telegram_data.get('groups', {})
            
            logger.info(f"📊 Loaded: {len(contacts)} contacts, {len(messages)} messages, {len(chats)} chats, {len(groups)} groups")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading Telegram data: {e}")
            return False

    def process_all_data(self):
        """Process all data into comprehensive database"""
        logger.info("🔄 Processing all data into comprehensive database...")
        
        try:
            # Process contacts first
            self._process_contacts()
            
            # Process chat metadata
            self._process_chat_metadata()
            
            # Process all messages with rich analytics
            self._process_messages_with_analytics()
            
            # Generate chat participants analysis
            self._analyze_chat_participants()
            
            # Generate conversation threads
            self._analyze_conversation_threads()
            
            # Generate comprehensive analytics
            self._generate_chat_analytics()
            
            logger.info("✅ All data processed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing data: {e}")
            return False

    def _process_contacts(self):
        """Process and enrich contact information"""
        logger.info("👥 Processing contact information...")
        
        contacts = self.telegram_data.get('contacts', {})
        messages = self.telegram_data.get('messages', [])
        
        # Calculate message counts per user
        user_message_counts = Counter()
        user_chat_counts = defaultdict(set)
        user_response_times = defaultdict(list)
        
        for msg in messages:
            user_id = msg.get('from_user_id')
            if user_id:
                user_message_counts[user_id] += 1
                user_chat_counts[user_id].add(msg.get('chat_id'))
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for user_id_str, contact_data in contacts.items():
                user_id = int(user_id_str)
                
                # Calculate activity and communication patterns
                total_messages = user_message_counts.get(user_id, 0)
                total_chats = len(user_chat_counts.get(user_id, set()))
                
                # Determine activity level
                if total_messages > 100:
                    activity_level = 'very_active'
                elif total_messages > 50:
                    activity_level = 'active'  
                elif total_messages > 10:
                    activity_level = 'moderate'
                else:
                    activity_level = 'occasional'
                
                cursor.execute("""
                    INSERT OR REPLACE INTO contacts_enriched (
                        user_id, username, first_name, last_name, phone,
                        is_verified, is_premium, is_bot, total_chats, total_messages,
                        activity_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    contact_data.get('username'),
                    contact_data.get('first_name'),
                    contact_data.get('last_name'), 
                    contact_data.get('phone'),
                    contact_data.get('is_verified', False),
                    contact_data.get('is_premium', False),
                    contact_data.get('is_bot', False),
                    total_chats,
                    total_messages,
                    activity_level
                ))
            
            conn.commit()
            logger.info(f"✅ Processed {len(contacts)} contacts")

    def _process_chat_metadata(self):
        """Process chat and group metadata"""
        logger.info("💬 Processing chat metadata...")
        
        chats = self.telegram_data.get('chats', {})
        groups = self.telegram_data.get('groups', {})
        messages = self.telegram_data.get('messages', [])
        
        # Calculate message statistics per chat
        chat_message_counts = Counter()
        chat_dates = defaultdict(list)
        chat_participants = defaultdict(set)
        
        for msg in messages:
            chat_id = msg.get('chat_id')
            if chat_id:
                chat_message_counts[chat_id] += 1
                chat_dates[chat_id].append(msg.get('date'))
                if msg.get('from_user_id'):
                    chat_participants[chat_id].add(msg.get('from_user_id'))
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Process individual chats
            for chat_id_str, chat_data in chats.items():
                chat_id = int(chat_id_str)
                
                dates = chat_dates.get(chat_id, [])
                first_date = min(dates) if dates else None
                last_date = max(dates) if dates else None
                
                cursor.execute("""
                    INSERT OR REPLACE INTO chats (
                        chat_id, chat_type, title, username, participant_count,
                        total_messages, first_message_date, last_message_date,
                        is_pinned, unread_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    chat_data.get('chat_type', 'private'),
                    chat_data.get('title'),
                    chat_data.get('username'),
                    len(chat_participants.get(chat_id, set())),
                    chat_message_counts.get(chat_id, 0),
                    first_date,
                    last_date,
                    chat_data.get('is_pinned', False),
                    chat_data.get('unread_count', 0)
                ))
            
            # Process groups
            for group_id_str, group_data in groups.items():
                group_id = int(group_id_str)
                
                dates = chat_dates.get(group_id, [])
                first_date = min(dates) if dates else None
                last_date = max(dates) if dates else None
                
                cursor.execute("""
                    INSERT OR REPLACE INTO chats (
                        chat_id, chat_type, title, username, participant_count,
                        total_messages, first_message_date, last_message_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    group_id,
                    'group',
                    group_data.get('title'),
                    None,
                    group_data.get('participants_count', len(chat_participants.get(group_id, set()))),
                    chat_message_counts.get(group_id, 0),
                    first_date,
                    last_date
                ))
            
            conn.commit()
            logger.info(f"✅ Processed {len(chats)} chats and {len(groups)} groups")

    def _process_messages_with_analytics(self):
        """Process all messages with rich analytical data"""
        logger.info("📝 Processing all messages with rich analytics...")
        
        messages = self.telegram_data.get('messages', [])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Process messages in batches
            batch_size = 1000
            processed = 0
            
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                batch_data = []
                
                for msg in batch:
                    enriched_msg = self._enrich_message(msg)
                    batch_data.append(enriched_msg)
                
                # Insert batch
                cursor.executemany("""
                    INSERT OR REPLACE INTO messages (
                        message_id, chat_id, from_user_id, date, text, message_type,
                        is_reply, is_forwarded, views, edit_date, contains_business_keywords,
                        is_question, sentiment_preliminary, word_count, has_contact_info,
                        message_length_category, time_of_day, day_of_week,
                        contains_media, contains_links, content_category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch_data)
                
                processed += len(batch)
                if processed % 2000 == 0:
                    logger.info(f"📊 Processed {processed}/{len(messages)} messages...")
            
            conn.commit()
            logger.info(f"✅ Processed all {len(messages)} messages with rich analytics")

    def _enrich_message(self, msg: Dict) -> Tuple:
        """Enrich a single message with analytical data"""
        # Extract datetime for analysis
        date_str = msg.get('date', '')
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            hour = date_obj.hour
            day_of_week = date_obj.strftime('%A')
            
            # Determine time of day
            if 6 <= hour < 12:
                time_of_day = 'morning'
            elif 12 <= hour < 18:
                time_of_day = 'afternoon'
            elif 18 <= hour < 22:
                time_of_day = 'evening'
            else:
                time_of_day = 'night'
        except:
            time_of_day = 'unknown'
            day_of_week = 'unknown'
        
        # Message length category
        word_count = msg.get('word_count', 0)
        if word_count < 5:
            length_category = 'short'
        elif word_count < 20:
            length_category = 'medium'
        else:
            length_category = 'long'
        
        # Content analysis
        text = msg.get('text', '').lower()
        contains_media = msg.get('message_type') != 'text'
        contains_links = 'http' in text or 'www.' in text or '.com' in text
        
        # Content categorization
        business_keywords = ['business', 'deal', 'money', 'investment', 'opportunity', 'meeting']
        technical_keywords = ['code', 'development', 'api', 'database', 'programming']
        
        if any(keyword in text for keyword in business_keywords):
            content_category = 'business'
        elif any(keyword in text for keyword in technical_keywords):
            content_category = 'technical'
        elif msg.get('contains_business_keywords'):
            content_category = 'business'
        else:
            content_category = 'casual'
        
        return (
            msg.get('message_id'),
            msg.get('chat_id'),
            msg.get('from_user_id'),
            msg.get('date'),
            msg.get('text', ''),
            msg.get('message_type', 'text'),
            msg.get('is_reply', False),
            msg.get('is_forwarded', False),
            msg.get('views'),
            msg.get('edit_date'),
            msg.get('contains_business_keywords', False),
            msg.get('is_question', False),
            msg.get('sentiment_preliminary', 'neutral'),
            word_count,
            msg.get('has_contact_info', False),
            length_category,
            time_of_day,
            day_of_week,
            contains_media,
            contains_links,
            content_category
        )

    def _analyze_chat_participants(self):
        """Analyze participants in each chat"""
        logger.info("👥 Analyzing chat participants...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all unique chat-user combinations
            cursor.execute("""
                SELECT chat_id, from_user_id, COUNT(*) as message_count,
                       MIN(date) as first_message, MAX(date) as last_message,
                       AVG(word_count) as avg_length
                FROM messages 
                WHERE from_user_id IS NOT NULL
                GROUP BY chat_id, from_user_id
            """)
            
            participants = cursor.fetchall()
            
            for chat_id, user_id, msg_count, first_msg, last_msg, avg_length in participants:
                # Get contact info
                cursor.execute("""
                    SELECT username, first_name, last_name, phone
                    FROM contacts_enriched WHERE user_id = ?
                """, (user_id,))
                
                contact_info = cursor.fetchone()
                username, first_name, last_name, phone = contact_info if contact_info else (None, None, None, None)
                
                # Determine engagement level
                if msg_count > 50:
                    engagement_level = 'high'
                elif msg_count > 10:
                    engagement_level = 'medium'
                else:
                    engagement_level = 'low'
                
                cursor.execute("""
                    INSERT OR REPLACE INTO chat_participants (
                        chat_id, user_id, username, first_name, last_name, phone,
                        message_count, first_message_date, last_message_date,
                        avg_message_length, engagement_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id, user_id, username, first_name, last_name, phone,
                    msg_count, first_msg, last_msg, avg_length or 0, engagement_level
                ))
            
            conn.commit()
            logger.info(f"✅ Analyzed {len(participants)} chat participants")

    def _analyze_conversation_threads(self):
        """Analyze conversation threads and topics"""
        logger.info("🧵 Analyzing conversation threads...")
        
        # This is a simplified version - could be enhanced with more sophisticated threading
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Group messages by chat and look for conversation patterns
            cursor.execute("""
                SELECT chat_id, COUNT(*) as total_messages,
                       MIN(message_id) as first_msg, MAX(message_id) as last_msg,
                       COUNT(DISTINCT from_user_id) as participant_count
                FROM messages
                GROUP BY chat_id
            """)
            
            chat_summaries = cursor.fetchall()
            
            thread_id = 1
            for chat_id, total_msgs, first_msg, last_msg, participants in chat_summaries:
                if total_msgs > 5:  # Only create threads for substantial conversations
                    cursor.execute("""
                        INSERT INTO conversation_threads (
                            thread_id, chat_id, start_message_id, end_message_id,
                            participant_count, message_count, thread_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        thread_id, chat_id, first_msg, last_msg,
                        participants, total_msgs, 'discussion'
                    ))
                    thread_id += 1
            
            conn.commit()
            logger.info(f"✅ Created {thread_id - 1} conversation threads")

    def _generate_chat_analytics(self):
        """Generate comprehensive chat analytics"""
        logger.info("📊 Generating comprehensive chat analytics...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all chats
            cursor.execute("SELECT chat_id FROM chats")
            chat_ids = [row[0] for row in cursor.fetchall()]
            
            for chat_id in chat_ids:
                # Daily message patterns
                cursor.execute("""
                    SELECT DATE(date) as day, COUNT(*) as count
                    FROM messages WHERE chat_id = ?
                    GROUP BY DATE(date)
                    ORDER BY day
                """, (chat_id,))
                daily_stats = dict(cursor.fetchall())
                
                # Hourly activity pattern
                cursor.execute("""
                    SELECT time_of_day, COUNT(*) as count
                    FROM messages WHERE chat_id = ?
                    GROUP BY time_of_day
                """, (chat_id,))
                hourly_pattern = dict(cursor.fetchall())
                
                # Sentiment distribution
                cursor.execute("""
                    SELECT sentiment_preliminary, COUNT(*) as count
                    FROM messages WHERE chat_id = ?
                    GROUP BY sentiment_preliminary
                """, (chat_id,))
                sentiment_dist = dict(cursor.fetchall())
                
                # Top participants
                cursor.execute("""
                    SELECT from_user_id, COUNT(*) as msg_count
                    FROM messages WHERE chat_id = ? AND from_user_id IS NOT NULL
                    GROUP BY from_user_id
                    ORDER BY msg_count DESC
                    LIMIT 5
                """, (chat_id,))
                top_participants = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO chat_analytics (
                        chat_id, daily_message_stats, hourly_activity_pattern,
                        sentiment_trends, conversation_starters
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    json.dumps(daily_stats),
                    json.dumps(hourly_pattern),
                    json.dumps(sentiment_dist),
                    json.dumps(top_participants)
                ))
            
            conn.commit()
            logger.info(f"✅ Generated analytics for {len(chat_ids)} chats")

    def export_comprehensive_data(self):
        """Export comprehensive data for analysis"""
        logger.info("📊 Exporting comprehensive data...")
        
        export_dir = Path("exports/comprehensive_analysis")
        export_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with sqlite3.connect(self.db_path) as conn:
            # Export chat summary
            chats_df = pd.read_sql_query("""
                SELECT c.*, ca.daily_message_stats, ca.sentiment_trends
                FROM chats c
                LEFT JOIN chat_analytics ca ON c.chat_id = ca.chat_id
                ORDER BY c.total_messages DESC
            """, conn)
            chats_df.to_csv(export_dir / f"chat_summary_{timestamp}.csv", index=False)
            
            # Export top conversations
            top_conversations_df = pd.read_sql_query("""
                SELECT c.chat_id, c.title, c.chat_type, c.total_messages,
                       c.participant_count, c.business_relevance_score
                FROM chats c
                WHERE c.total_messages > 10
                ORDER BY c.total_messages DESC
                LIMIT 50
            """, conn)
            top_conversations_df.to_csv(export_dir / f"top_conversations_{timestamp}.csv", index=False)
            
            # Export message analytics
            message_analytics_df = pd.read_sql_query("""
                SELECT chat_id, message_type, sentiment_preliminary,
                       content_category, time_of_day, day_of_week,
                       COUNT(*) as count, AVG(word_count) as avg_length
                FROM messages
                GROUP BY chat_id, message_type, sentiment_preliminary, 
                         content_category, time_of_day, day_of_week
            """, conn)
            message_analytics_df.to_csv(export_dir / f"message_analytics_{timestamp}.csv", index=False)
            
            # Export participant analysis
            participants_df = pd.read_sql_query("""
                SELECT cp.*, ce.activity_level, ce.total_chats, ce.total_messages as user_total_messages
                FROM chat_participants cp
                LEFT JOIN contacts_enriched ce ON cp.user_id = ce.user_id
                ORDER BY cp.message_count DESC
            """, conn)
            participants_df.to_csv(export_dir / f"participants_analysis_{timestamp}.csv", index=False)
        
        logger.info(f"✅ Exported comprehensive data to {export_dir}")

    def get_database_summary(self):
        """Get summary statistics of the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM chats")
            total_chats = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM contacts_enriched")
            total_contacts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chat_participants")
            total_participants = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM conversation_threads")
            total_threads = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(total_messages) FROM chats WHERE total_messages > 0")
            avg_messages_per_chat = cursor.fetchone()[0] or 0
            
            return {
                'total_chats': total_chats,
                'total_messages': total_messages,
                'total_contacts': total_contacts,
                'total_participants': total_participants,
                'total_threads': total_threads,
                'avg_messages_per_chat': round(avg_messages_per_chat, 2)
            }

async def main():
    """Main function to create comprehensive message database"""
    print("🚀 COMPREHENSIVE MESSAGE DATABASE SYSTEM")
    print("=" * 60)
    print("📱 Processing ALL 10,028 Telegram messages")
    print("💬 Organizing by chat and group chat")
    print("📊 Adding rich analytical metadata")
    print("🔍 Creating comprehensive database for analysis")
    print()
    
    # Initialize system
    db = ComprehensiveMessageDatabase()
    
    # Load data
    print("📱 Step 1: Loading Telegram data...")
    if not db.load_telegram_data():
        print("❌ Failed to load Telegram data")
        return
    
    # Process all data
    print("🔄 Step 2: Processing all data with rich analytics...")
    if not db.process_all_data():
        print("❌ Failed to process data")
        return
    
    # Export data
    print("📊 Step 3: Exporting comprehensive data...")
    db.export_comprehensive_data()
    
    # Show summary
    summary = db.get_database_summary()
    print("\n🎉 COMPREHENSIVE MESSAGE DATABASE COMPLETE!")
    print(f"📊 Database Summary:")
    print(f"   💬 Total Chats: {summary['total_chats']:,}")
    print(f"   📝 Total Messages: {summary['total_messages']:,}")
    print(f"   👥 Total Contacts: {summary['total_contacts']:,}")
    print(f"   🤝 Chat Participants: {summary['total_participants']:,}")
    print(f"   🧵 Conversation Threads: {summary['total_threads']:,}")
    print(f"   📈 Avg Messages/Chat: {summary['avg_messages_per_chat']}")
    print()
    print(f"📁 Database: data/comprehensive_message_database.db")
    print(f"📊 Exports: exports/comprehensive_analysis/")
    print("\n✅ Ready for comprehensive analysis!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 