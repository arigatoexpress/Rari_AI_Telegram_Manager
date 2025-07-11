#!/usr/bin/env python3
"""
BD Lead Consolidation System
===========================
Consolidates and organizes the comprehensive message database specifically 
for Business Development and lead follow-up activities.

Features:
- Lead identification and scoring from comprehensive database
- BD-focused contact prioritization
- Follow-up recommendations and timing
- Conversation history analysis for BD context
- Export for CRM and BD workflows
- Actionable insights for business development
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bd_consolidation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BDLead:
    """Business Development Lead with actionable insights"""
    contact_id: str
    user_id: int
    name: str
    username: str
    phone: str
    
    # BD Scoring
    bd_score: float  # 0-100
    lead_quality: str  # 'hot', 'warm', 'cold'
    estimated_value: float
    
    # Engagement Data
    total_messages: int
    last_interaction: str
    response_rate: float
    avg_response_time: float
    
    # Business Context
    business_keywords_found: List[str]
    conversation_themes: List[str]
    pain_points: List[str]
    opportunities: List[str]
    decision_maker_indicators: List[str]
    
    # Follow-up Strategy
    next_action: str
    follow_up_priority: str  # 'immediate', 'this_week', 'this_month', 'low'
    best_contact_time: str
    conversation_context: str
    
    # Relationship Data
    relationship_strength: str  # 'strong', 'moderate', 'weak'
    interaction_frequency: str  # 'daily', 'weekly', 'monthly', 'rare'
    mutual_connections: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            'contact_id': self.contact_id,
            'user_id': self.user_id,
            'name': self.name,
            'username': self.username,
            'phone': self.phone,
            'bd_score': self.bd_score,
            'lead_quality': self.lead_quality,
            'estimated_value': self.estimated_value,
            'total_messages': self.total_messages,
            'last_interaction': self.last_interaction,
            'response_rate': self.response_rate,
            'avg_response_time': self.avg_response_time,
            'business_keywords': ', '.join(self.business_keywords_found),
            'conversation_themes': ', '.join(self.conversation_themes),
            'pain_points': ', '.join(self.pain_points),
            'opportunities': ', '.join(self.opportunities),
            'decision_maker_indicators': ', '.join(self.decision_maker_indicators),
            'next_action': self.next_action,
            'follow_up_priority': self.follow_up_priority,
            'best_contact_time': self.best_contact_time,
            'conversation_context': self.conversation_context,
            'relationship_strength': self.relationship_strength,
            'interaction_frequency': self.interaction_frequency,
            'mutual_connections': ', '.join(self.mutual_connections)
        }

class BDConsolidationSystem:
    """BD-focused consolidation of comprehensive message database"""
    
    def __init__(self):
        self.comprehensive_db = Path("data/comprehensive_message_database.db")
        self.bd_db = Path("data/bd_consolidated_leads.db")
        self.bd_db.parent.mkdir(exist_ok=True)
        
        # BD-specific keywords and indicators
        self.business_keywords = {
            'high_value': ['investment', 'investor', 'funding', 'capital', 'venture', 'deal', 'partnership'],
            'opportunity': ['opportunity', 'business', 'collaboration', 'project', 'contract', 'proposal'],
            'decision_maker': ['founder', 'ceo', 'director', 'manager', 'decision', 'budget', 'authority'],
            'pain_points': ['problem', 'challenge', 'issue', 'struggling', 'need', 'solution', 'help'],
            'timing': ['urgent', 'asap', 'deadline', 'soon', 'immediately', 'timeline', 'schedule'],
            'financial': ['budget', 'cost', 'price', 'revenue', 'profit', 'roi', 'value', 'money']
        }
        
        self.conversation_themes = {
            'crypto_defi': ['defi', 'crypto', 'blockchain', 'token', 'protocol', 'yield', 'liquidity'],
            'tech_development': ['development', 'coding', 'api', 'platform', 'software', 'technical'],
            'marketing': ['marketing', 'brand', 'campaign', 'content', 'social', 'promotion'],
            'events': ['event', 'conference', 'meetup', 'summit', 'networking', 'speaking'],
            'education': ['learning', 'course', 'training', 'workshop', 'education', 'teach']
        }
        
        self._init_bd_database()
        
    def _init_bd_database(self):
        """Initialize BD consolidation database"""
        with sqlite3.connect(self.bd_db) as conn:
            conn.executescript("""
                -- Consolidated BD leads
                CREATE TABLE IF NOT EXISTS bd_leads (
                    lead_id TEXT PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    name TEXT,
                    username TEXT,
                    phone TEXT,
                    bd_score REAL,
                    lead_quality TEXT,
                    estimated_value REAL,
                    total_messages INTEGER,
                    last_interaction TEXT,
                    response_rate REAL,
                    avg_response_time REAL,
                    business_keywords TEXT, -- JSON array
                    conversation_themes TEXT, -- JSON array
                    pain_points TEXT, -- JSON array
                    opportunities TEXT, -- JSON array
                    decision_maker_indicators TEXT, -- JSON array
                    next_action TEXT,
                    follow_up_priority TEXT,
                    best_contact_time TEXT,
                    conversation_context TEXT,
                    relationship_strength TEXT,
                    interaction_frequency TEXT,
                    mutual_connections TEXT, -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- BD conversation history
                CREATE TABLE IF NOT EXISTS bd_conversations (
                    conversation_id TEXT PRIMARY KEY,
                    lead_id TEXT,
                    chat_id INTEGER,
                    chat_title TEXT,
                    message_count INTEGER,
                    first_message_date TEXT,
                    last_message_date TEXT,
                    business_relevance_score REAL,
                    key_topics TEXT, -- JSON array
                    sentiment_trend TEXT,
                    action_items TEXT, -- JSON array
                    follow_up_needed BOOLEAN DEFAULT FALSE,
                    
                    FOREIGN KEY (lead_id) REFERENCES bd_leads (lead_id)
                );
                
                -- BD opportunities identified
                CREATE TABLE IF NOT EXISTS bd_opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    lead_id TEXT,
                    opportunity_type TEXT,
                    description TEXT,
                    estimated_value REAL,
                    probability REAL,
                    timeline TEXT,
                    requirements TEXT,
                    next_steps TEXT,
                    status TEXT DEFAULT 'identified',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (lead_id) REFERENCES bd_leads (lead_id)
                );
                
                -- BD follow-up actions
                CREATE TABLE IF NOT EXISTS bd_follow_ups (
                    follow_up_id TEXT PRIMARY KEY,
                    lead_id TEXT,
                    action_type TEXT,
                    description TEXT,
                    priority TEXT,
                    due_date TEXT,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (lead_id) REFERENCES bd_leads (lead_id)
                );
                
                -- Create indexes
                CREATE INDEX IF NOT EXISTS idx_bd_leads_score ON bd_leads(bd_score);
                CREATE INDEX IF NOT EXISTS idx_bd_leads_quality ON bd_leads(lead_quality);
                CREATE INDEX IF NOT EXISTS idx_bd_leads_priority ON bd_leads(follow_up_priority);
                CREATE INDEX IF NOT EXISTS idx_bd_conversations_lead ON bd_conversations(lead_id);
                CREATE INDEX IF NOT EXISTS idx_bd_opportunities_lead ON bd_opportunities(lead_id);
                CREATE INDEX IF NOT EXISTS idx_bd_follow_ups_lead ON bd_follow_ups(lead_id);
                CREATE INDEX IF NOT EXISTS idx_bd_follow_ups_priority ON bd_follow_ups(priority);
            """)
            
        logger.info("✅ BD consolidation database initialized")

    def consolidate_for_bd(self):
        """Consolidate comprehensive database for BD purposes"""
        logger.info("🎯 Starting BD consolidation process...")
        
        try:
            # Analyze all contacts for BD potential
            bd_leads = self._analyze_contacts_for_bd()
            
            # Store BD leads
            self._store_bd_leads(bd_leads)
            
            # Analyze conversations for BD context
            self._analyze_conversations_for_bd()
            
            # Identify opportunities
            self._identify_opportunities()
            
            # Generate follow-up actions
            self._generate_follow_up_actions()
            
            logger.info("✅ BD consolidation complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ BD consolidation failed: {e}")
            return False

    def _analyze_contacts_for_bd(self) -> List[BDLead]:
        """Analyze all contacts for BD potential"""
        logger.info("🔍 Analyzing contacts for BD potential...")
        
        bd_leads = []
        
        with sqlite3.connect(self.comprehensive_db) as conn:
            cursor = conn.cursor()
            
            # Get all contacts with significant interactions
            cursor.execute("""
                SELECT ce.user_id, ce.username, ce.first_name, ce.last_name, ce.phone,
                       ce.total_messages, ce.activity_level,
                       GROUP_CONCAT(DISTINCT cp.chat_id) as chat_ids,
                       AVG(cp.message_count) as avg_chat_messages,
                       MAX(cp.last_message_date) as last_interaction
                FROM contacts_enriched ce
                LEFT JOIN chat_participants cp ON ce.user_id = cp.user_id
                WHERE ce.total_messages > 0
                GROUP BY ce.user_id
                ORDER BY ce.total_messages DESC
            """)
            
            contacts = cursor.fetchall()
            
            for contact in contacts:
                user_id, username, first_name, last_name, phone, total_messages, activity_level, chat_ids, avg_chat_messages, last_interaction = contact
                
                # Calculate BD score
                bd_score = self._calculate_bd_score(cursor, user_id, total_messages, activity_level, chat_ids)
                
                # Determine lead quality
                if bd_score >= 70:
                    lead_quality = 'hot'
                elif bd_score >= 40:
                    lead_quality = 'warm'
                else:
                    lead_quality = 'cold'
                
                # Skip very low-quality leads
                if bd_score < 20:
                    continue
                
                # Get business context
                business_context = self._get_business_context(cursor, user_id)
                
                # Create BD Lead
                name = f"{first_name or ''} {last_name or ''}".strip() or f"@{username}" or f"User_{user_id}"
                
                bd_lead = BDLead(
                    contact_id=f"lead_{user_id}",
                    user_id=user_id,
                    name=name,
                    username=username or '',
                    phone=phone or '',
                    bd_score=bd_score,
                    lead_quality=lead_quality,
                    estimated_value=self._estimate_lead_value(bd_score, business_context),
                    total_messages=total_messages,
                    last_interaction=last_interaction or '',
                    response_rate=self._calculate_response_rate(cursor, user_id),
                    avg_response_time=self._calculate_avg_response_time(cursor, user_id),
                    business_keywords_found=business_context.get('keywords', []),
                    conversation_themes=business_context.get('themes', []),
                    pain_points=business_context.get('pain_points', []),
                    opportunities=business_context.get('opportunities', []),
                    decision_maker_indicators=business_context.get('decision_makers', []),
                    next_action=self._determine_next_action(bd_score, business_context, last_interaction),
                    follow_up_priority=self._determine_follow_up_priority(bd_score, last_interaction),
                    best_contact_time=self._determine_best_contact_time(cursor, user_id),
                    conversation_context=business_context.get('context', ''),
                    relationship_strength=self._assess_relationship_strength(bd_score, total_messages),
                    interaction_frequency=self._calculate_interaction_frequency(cursor, user_id),
                    mutual_connections=business_context.get('mutual_connections', [])
                )
                
                bd_leads.append(bd_lead)
        
        logger.info(f"🎯 Identified {len(bd_leads)} potential BD leads")
        return bd_leads

    def _calculate_bd_score(self, cursor, user_id: int, total_messages: int, activity_level: str, chat_ids: str) -> float:
        """Calculate BD score (0-100) for a contact"""
        score = 0.0
        
        # Base score from message volume
        if total_messages > 100:
            score += 20
        elif total_messages > 50:
            score += 15
        elif total_messages > 10:
            score += 10
        else:
            score += 5
        
        # Activity level bonus
        activity_bonuses = {'very_active': 15, 'active': 10, 'moderate': 5, 'occasional': 0}
        score += activity_bonuses.get(activity_level, 0)
        
        # Business keyword analysis
        cursor.execute("""
            SELECT COUNT(*) as business_messages,
                   AVG(CASE WHEN sentiment_preliminary = 'positive' THEN 1 ELSE 0 END) as positive_ratio
            FROM messages
            WHERE from_user_id = ? AND contains_business_keywords = 1
        """, (user_id,))
        
        business_data = cursor.fetchone()
        if business_data:
            business_messages, positive_ratio = business_data
            score += min(business_messages * 2, 25)  # Up to 25 points for business messages
            score += (positive_ratio or 0) * 10  # Up to 10 points for positive sentiment
        
        # Recent activity bonus
        cursor.execute("""
            SELECT COUNT(*) as recent_messages
            FROM messages
            WHERE from_user_id = ? AND date > datetime('now', '-30 days')
        """, (user_id,))
        
        recent_activity = cursor.fetchone()[0]
        if recent_activity > 0:
            score += min(recent_activity * 1.5, 15)  # Up to 15 points for recent activity
        
        # Multiple chat participation bonus
        if chat_ids:
            unique_chats = len(chat_ids.split(',')) if chat_ids else 0
            score += min(unique_chats * 3, 15)  # Up to 15 points for multi-chat presence
        
        return min(score, 100.0)

    def _get_business_context(self, cursor, user_id: int) -> Dict[str, Any]:
        """Get business context for a contact"""
        context = {
            'keywords': [],
            'themes': [],
            'pain_points': [],
            'opportunities': [],
            'decision_makers': [],
            'context': '',
            'mutual_connections': []
        }
        
        # Get all messages from this user
        cursor.execute("""
            SELECT text, sentiment_preliminary, contains_business_keywords
            FROM messages
            WHERE from_user_id = ? AND text IS NOT NULL
            ORDER BY date DESC
            LIMIT 100
        """, (user_id,))
        
        messages = cursor.fetchall()
        
        # Analyze message content
        all_text = []
        for text, sentiment, has_business_keywords in messages:
            if text:
                all_text.append(text.lower())
        
        full_text = ' '.join(all_text)
        
        # Extract business keywords
        for category, keywords in self.business_keywords.items():
            found_keywords = [kw for kw in keywords if kw in full_text]
            if found_keywords:
                if category == 'high_value':
                    context['keywords'].extend(found_keywords)
                elif category == 'pain_points':
                    context['pain_points'].extend(found_keywords)
                elif category == 'opportunity':
                    context['opportunities'].extend(found_keywords)
                elif category == 'decision_maker':
                    context['decision_makers'].extend(found_keywords)
        
        # Extract conversation themes
        for theme, keywords in self.conversation_themes.items():
            if any(kw in full_text for kw in keywords):
                context['themes'].append(theme)
        
        # Generate context summary
        context['context'] = self._generate_context_summary(messages[:10])  # Last 10 messages
        
        return context

    def _generate_context_summary(self, recent_messages: List[Tuple]) -> str:
        """Generate a context summary from recent messages"""
        if not recent_messages:
            return "No recent activity"
        
        business_messages = [msg[0] for msg in recent_messages if msg[2]]  # Has business keywords
        
        if business_messages:
            return f"Recent business discussions. Last message topics: {', '.join(business_messages[:3])}"
        else:
            return f"Recent casual conversations. {len(recent_messages)} messages in history."

    def _estimate_lead_value(self, bd_score: float, business_context: Dict) -> float:
        """Estimate potential value of a lead"""
        base_value = bd_score * 100  # Base value from BD score
        
        # Multiply by business context factors
        if 'investment' in business_context.get('keywords', []):
            base_value *= 3
        elif 'funding' in business_context.get('keywords', []):
            base_value *= 2.5
        elif 'partnership' in business_context.get('keywords', []):
            base_value *= 2
        elif 'business' in business_context.get('keywords', []):
            base_value *= 1.5
        
        # Theme multipliers
        if 'crypto_defi' in business_context.get('themes', []):
            base_value *= 1.5
        elif 'tech_development' in business_context.get('themes', []):
            base_value *= 1.3
        
        return min(base_value, 50000)  # Cap at $50k

    def _determine_next_action(self, bd_score: float, business_context: Dict, last_interaction: str) -> str:
        """Determine the next action for a lead"""
        if bd_score >= 70:
            return "Schedule immediate call/meeting"
        elif bd_score >= 50:
            return "Send personalized business proposal"
        elif bd_score >= 30:
            return "Re-engage with valuable content"
        else:
            return "Monitor for business opportunities"

    def _determine_follow_up_priority(self, bd_score: float, last_interaction: str) -> str:
        """Determine follow-up priority"""
        try:
            if last_interaction:
                last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                days_since = (datetime.now() - last_date).days
                
                if bd_score >= 70:
                    return "immediate"
                elif bd_score >= 50 and days_since <= 7:
                    return "this_week"
                elif bd_score >= 30 and days_since <= 30:
                    return "this_month"
                else:
                    return "low"
            else:
                if bd_score >= 70:
                    return "immediate"
                elif bd_score >= 40:
                    return "this_week"
                else:
                    return "low"
        except:
            return "low"

    def _determine_best_contact_time(self, cursor, user_id: int) -> str:
        """Determine best time to contact based on activity patterns"""
        cursor.execute("""
            SELECT time_of_day, COUNT(*) as count
            FROM messages
            WHERE from_user_id = ?
            GROUP BY time_of_day
            ORDER BY count DESC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        return result[0] if result else "afternoon"

    def _calculate_response_rate(self, cursor, user_id: int) -> float:
        """Calculate response rate for a contact"""
        # This is a simplified calculation
        cursor.execute("""
            SELECT COUNT(*) as total_messages,
                   SUM(CASE WHEN is_reply = 1 THEN 1 ELSE 0 END) as replies
            FROM messages
            WHERE from_user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if result and result[0] > 0:
            return (result[1] or 0) / result[0] * 100
        return 0.0

    def _calculate_avg_response_time(self, cursor, user_id: int) -> float:
        """Calculate average response time in minutes"""
        # Simplified calculation - would need more complex logic for actual response times
        return 60.0  # Default to 1 hour

    def _assess_relationship_strength(self, bd_score: float, total_messages: int) -> str:
        """Assess relationship strength"""
        if bd_score >= 70 and total_messages > 100:
            return "strong"
        elif bd_score >= 40 and total_messages > 20:
            return "moderate"
        else:
            return "weak"

    def _calculate_interaction_frequency(self, cursor, user_id: int) -> str:
        """Calculate interaction frequency"""
        cursor.execute("""
            SELECT COUNT(*) as recent_messages
            FROM messages
            WHERE from_user_id = ? AND date > datetime('now', '-7 days')
        """, (user_id,))
        
        recent = cursor.fetchone()[0]
        
        if recent > 7:
            return "daily"
        elif recent > 0:
            return "weekly"
        else:
            cursor.execute("""
                SELECT COUNT(*) as monthly_messages
                FROM messages
                WHERE from_user_id = ? AND date > datetime('now', '-30 days')
            """, (user_id,))
            
            monthly = cursor.fetchone()[0]
            if monthly > 0:
                return "monthly"
            else:
                return "rare"

    def _store_bd_leads(self, bd_leads: List[BDLead]):
        """Store BD leads in database"""
        logger.info(f"💾 Storing {len(bd_leads)} BD leads...")
        
        with sqlite3.connect(self.bd_db) as conn:
            cursor = conn.cursor()
            
            for lead in bd_leads:
                cursor.execute("""
                    INSERT OR REPLACE INTO bd_leads (
                        lead_id, user_id, name, username, phone, bd_score, lead_quality,
                        estimated_value, total_messages, last_interaction, response_rate,
                        avg_response_time, business_keywords, conversation_themes,
                        pain_points, opportunities, decision_maker_indicators,
                        next_action, follow_up_priority, best_contact_time,
                        conversation_context, relationship_strength, interaction_frequency,
                        mutual_connections
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead.contact_id, lead.user_id, lead.name, lead.username, lead.phone,
                    lead.bd_score, lead.lead_quality, lead.estimated_value, lead.total_messages,
                    lead.last_interaction, lead.response_rate, lead.avg_response_time,
                    json.dumps(lead.business_keywords_found), json.dumps(lead.conversation_themes),
                    json.dumps(lead.pain_points), json.dumps(lead.opportunities),
                    json.dumps(lead.decision_maker_indicators), lead.next_action,
                    lead.follow_up_priority, lead.best_contact_time, lead.conversation_context,
                    lead.relationship_strength, lead.interaction_frequency,
                    json.dumps(lead.mutual_connections)
                ))
            
            conn.commit()
            logger.info(f"✅ Stored {len(bd_leads)} BD leads")

    def _analyze_conversations_for_bd(self):
        """Analyze conversations for BD context"""
        logger.info("💬 Analyzing conversations for BD context...")
        
        with sqlite3.connect(self.comprehensive_db) as conn:
            cursor = conn.cursor()
            
            # Get all significant conversations
            cursor.execute("""
                SELECT c.chat_id, c.title, c.total_messages, c.business_relevance_score,
                       c.first_message_date, c.last_message_date
                FROM chats c
                WHERE c.total_messages > 10
                ORDER BY c.business_relevance_score DESC, c.total_messages DESC
            """)
            
            conversations = cursor.fetchall()
            
        with sqlite3.connect(self.bd_db) as bd_conn:
            bd_cursor = bd_conn.cursor()
            
            # Get all BD lead user IDs first
            bd_cursor.execute("SELECT user_id FROM bd_leads")
            bd_user_ids = {row[0] for row in bd_cursor.fetchall()}
            
            for chat_id, title, total_messages, business_score, first_date, last_date in conversations:
                # Find participants in this chat who are BD leads
                with sqlite3.connect(self.comprehensive_db) as comp_conn:
                    comp_cursor = comp_conn.cursor()
                    comp_cursor.execute("""
                        SELECT DISTINCT user_id
                        FROM chat_participants
                        WHERE chat_id = ?
                    """, (chat_id,))
                    
                    chat_participants = comp_cursor.fetchall()
                
                # Filter for BD leads
                bd_participants = [(user_id,) for (user_id,) in chat_participants if user_id in bd_user_ids]
                
                for (user_id,) in bd_participants:
                    conversation_id = f"conv_{chat_id}_{user_id}"
                    
                    bd_cursor.execute("""
                        INSERT OR REPLACE INTO bd_conversations (
                            conversation_id, lead_id, chat_id, chat_title,
                            message_count, first_message_date, last_message_date,
                            business_relevance_score, follow_up_needed
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        conversation_id, f"lead_{user_id}", chat_id, title,
                        total_messages, first_date, last_date,
                        business_score or 0, business_score > 50
                    ))
            
            bd_conn.commit()
            logger.info(f"✅ Analyzed {len(conversations)} conversations for BD context")

    def _identify_opportunities(self):
        """Identify specific opportunities from BD leads"""
        logger.info("🎯 Identifying specific opportunities...")
        
        with sqlite3.connect(self.bd_db) as conn:
            cursor = conn.cursor()
            
            # Get high-quality leads
            cursor.execute("""
                SELECT lead_id, user_id, name, bd_score, business_keywords, opportunities
                FROM bd_leads
                WHERE bd_score > 40
                ORDER BY bd_score DESC
            """)
            
            leads = cursor.fetchall()
            
            opportunity_id = 1
            for lead_id, user_id, name, bd_score, business_keywords, opportunities in leads:
                keywords = json.loads(business_keywords or '[]')
                opps = json.loads(opportunities or '[]')
                
                # Create opportunities based on keywords and context
                if any(kw in keywords for kw in ['investment', 'funding', 'capital']):
                    cursor.execute("""
                        INSERT INTO bd_opportunities (
                            opportunity_id, lead_id, opportunity_type, description,
                            estimated_value, probability, timeline, next_steps
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"opp_{opportunity_id}", lead_id, "Investment",
                        f"Potential investment opportunity with {name}",
                        bd_score * 200, bd_score / 100, "2-6 months",
                        "Schedule investment discussion call"
                    ))
                    opportunity_id += 1
                
                if any(kw in keywords for kw in ['partnership', 'collaboration']):
                    cursor.execute("""
                        INSERT INTO bd_opportunities (
                            opportunity_id, lead_id, opportunity_type, description,
                            estimated_value, probability, timeline, next_steps
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"opp_{opportunity_id}", lead_id, "Partnership",
                        f"Strategic partnership opportunity with {name}",
                        bd_score * 150, bd_score / 100, "1-3 months",
                        "Send partnership proposal"
                    ))
                    opportunity_id += 1
            
            conn.commit()
            logger.info(f"✅ Identified {opportunity_id - 1} specific opportunities")

    def _generate_follow_up_actions(self):
        """Generate specific follow-up actions for each lead"""
        logger.info("📋 Generating follow-up actions...")
        
        with sqlite3.connect(self.bd_db) as conn:
            cursor = conn.cursor()
            
            # Get all leads that need follow-up
            cursor.execute("""
                SELECT lead_id, name, bd_score, follow_up_priority, next_action, last_interaction
                FROM bd_leads
                WHERE follow_up_priority IN ('immediate', 'this_week', 'this_month')
                ORDER BY bd_score DESC
            """)
            
            leads = cursor.fetchall()
            
            follow_up_id = 1
            for lead_id, name, bd_score, priority, next_action, last_interaction in leads:
                # Calculate due date based on priority
                if priority == 'immediate':
                    due_date = datetime.now() + timedelta(days=1)
                elif priority == 'this_week':
                    due_date = datetime.now() + timedelta(days=7)
                else:  # this_month
                    due_date = datetime.now() + timedelta(days=30)
                
                cursor.execute("""
                    INSERT INTO bd_follow_ups (
                        follow_up_id, lead_id, action_type, description,
                        priority, due_date, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"followup_{follow_up_id}", lead_id, "Outreach",
                    f"{next_action} for {name}",
                    priority, due_date.isoformat(),
                    f"BD Score: {bd_score}/100. Last interaction: {last_interaction}"
                ))
                follow_up_id += 1
            
            conn.commit()
            logger.info(f"✅ Generated {follow_up_id - 1} follow-up actions")

    def export_bd_dashboard(self):
        """Export BD dashboard data"""
        logger.info("📊 Exporting BD dashboard...")
        
        export_dir = Path("exports/bd_dashboard")
        export_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with sqlite3.connect(self.bd_db) as conn:
            # Export prioritized leads
            leads_df = pd.read_sql_query("""
                SELECT name, username, phone, bd_score, lead_quality, estimated_value,
                       total_messages, last_interaction, follow_up_priority,
                       next_action, relationship_strength, business_keywords,
                       conversation_themes, opportunities, conversation_context
                FROM bd_leads
                ORDER BY bd_score DESC
            """, conn)
            leads_df.to_csv(export_dir / f"bd_leads_prioritized_{timestamp}.csv", index=False)
            
            # Export hot leads for immediate action
            hot_leads_df = pd.read_sql_query("""
                SELECT name, username, phone, bd_score, estimated_value,
                       next_action, best_contact_time, conversation_context
                FROM bd_leads
                WHERE lead_quality = 'hot'
                ORDER BY bd_score DESC
            """, conn)
            hot_leads_df.to_csv(export_dir / f"hot_leads_immediate_action_{timestamp}.csv", index=False)
            
            # Export follow-up actions
            follow_ups_df = pd.read_sql_query("""
                SELECT fu.description, fu.priority, fu.due_date, fu.status,
                       bl.name, bl.username, bl.phone, bl.bd_score
                FROM bd_follow_ups fu
                JOIN bd_leads bl ON fu.lead_id = bl.lead_id
                ORDER BY fu.priority, fu.due_date
            """, conn)
            follow_ups_df.to_csv(export_dir / f"follow_up_actions_{timestamp}.csv", index=False)
            
            # Export opportunities
            opportunities_df = pd.read_sql_query("""
                SELECT o.opportunity_type, o.description, o.estimated_value,
                       o.probability, o.timeline, o.next_steps,
                       bl.name, bl.username, bl.phone, bl.bd_score
                FROM bd_opportunities o
                JOIN bd_leads bl ON o.lead_id = bl.lead_id
                ORDER BY o.estimated_value DESC
            """, conn)
            opportunities_df.to_csv(export_dir / f"bd_opportunities_{timestamp}.csv", index=False)
            
            # Export conversation summaries
            conversations_df = pd.read_sql_query("""
                SELECT c.chat_title, c.message_count, c.business_relevance_score,
                       c.first_message_date, c.last_message_date, c.follow_up_needed,
                       bl.name, bl.username, bl.bd_score
                FROM bd_conversations c
                JOIN bd_leads bl ON c.lead_id = bl.lead_id
                WHERE c.business_relevance_score > 30
                ORDER BY c.business_relevance_score DESC
            """, conn)
            conversations_df.to_csv(export_dir / f"bd_conversations_{timestamp}.csv", index=False)
        
        logger.info(f"✅ BD dashboard exported to {export_dir}")

    def get_bd_summary(self):
        """Get BD summary statistics"""
        with sqlite3.connect(self.bd_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM bd_leads")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bd_leads WHERE lead_quality = 'hot'")
            hot_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bd_leads WHERE lead_quality = 'warm'")
            warm_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bd_leads WHERE follow_up_priority = 'immediate'")
            immediate_actions = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(estimated_value) FROM bd_leads")
            total_pipeline_value = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM bd_opportunities")
            total_opportunities = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bd_follow_ups WHERE status = 'pending'")
            pending_follow_ups = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(bd_score) FROM bd_leads")
            avg_lead_score = cursor.fetchone()[0] or 0
            
            return {
                'total_leads': total_leads,
                'hot_leads': hot_leads,
                'warm_leads': warm_leads,
                'immediate_actions': immediate_actions,
                'total_pipeline_value': total_pipeline_value,
                'total_opportunities': total_opportunities,
                'pending_follow_ups': pending_follow_ups,
                'avg_lead_score': round(avg_lead_score, 2)
            }

async def main():
    """Main function to run BD consolidation"""
    print("🎯 BD LEAD CONSOLIDATION SYSTEM")
    print("=" * 60)
    print("📊 Consolidating comprehensive database for BD")
    print("🎯 Identifying and prioritizing leads")
    print("📋 Generating follow-up actions")
    print("💼 Creating BD dashboard")
    print()
    
    # Initialize system
    bd_system = BDConsolidationSystem()
    
    # Run consolidation
    print("🔄 Step 1: Consolidating data for BD purposes...")
    if not bd_system.consolidate_for_bd():
        print("❌ BD consolidation failed")
        return
    
    # Export dashboard
    print("📊 Step 2: Exporting BD dashboard...")
    bd_system.export_bd_dashboard()
    
    # Show summary
    summary = bd_system.get_bd_summary()
    print("\n🎉 BD CONSOLIDATION COMPLETE!")
    print(f"📊 BD Summary:")
    print(f"   🎯 Total Leads: {summary['total_leads']:,}")
    print(f"   🔥 Hot Leads: {summary['hot_leads']:,}")
    print(f"   🌡️  Warm Leads: {summary['warm_leads']:,}")
    print(f"   ⚡ Immediate Actions: {summary['immediate_actions']:,}")
    print(f"   💰 Total Pipeline Value: ${summary['total_pipeline_value']:,.2f}")
    print(f"   🎯 Opportunities: {summary['total_opportunities']:,}")
    print(f"   📋 Pending Follow-ups: {summary['pending_follow_ups']:,}")
    print(f"   📈 Average Lead Score: {summary['avg_lead_score']}/100")
    print()
    print(f"📁 BD Database: data/bd_consolidated_leads.db")
    print(f"📊 BD Dashboard: exports/bd_dashboard/")
    print("\n✅ Ready for BD action!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 