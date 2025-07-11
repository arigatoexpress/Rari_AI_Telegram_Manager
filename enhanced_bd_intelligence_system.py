#!/usr/bin/env python3
"""
Enhanced BD Intelligence System
==============================
Advanced business development system with robust lead intelligence,
comprehensive keyword analysis, and personalized conference follow-up
messages optimized for conversion and investment opportunities.

Features:
- Enhanced keyword analysis with 500+ business terms
- Advanced lead scoring with multiple intelligence factors
- Personalized conference follow-up messages
- Investment opportunity analysis
- Human-readable reports optimized for AI analysis
- Conversion-optimized outreach templates
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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_bd_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedBDLead:
    """Enhanced BD Lead with comprehensive intelligence"""
    # Basic Info
    contact_id: str
    user_id: int
    name: str
    username: str
    phone: str
    
    # Enhanced BD Scoring
    bd_score: float
    intelligence_score: float  # New comprehensive intelligence rating
    conversion_likelihood: float  # Likelihood to convert to investment
    lead_quality: str
    priority_level: str  # critical, high, medium, low
    
    # Financial Analysis
    estimated_value: float
    investment_capacity: str  # high, medium, low
    deal_size_category: str  # enterprise, mid-market, startup
    financial_indicators: List[str]
    
    # Engagement Intelligence
    total_messages: int
    last_interaction: str
    response_rate: float
    engagement_quality: str  # deep, moderate, surface
    communication_style: str  # formal, casual, technical
    
    # Business Intelligence
    business_keywords_found: List[str]
    investment_keywords: List[str]
    technology_expertise: List[str]
    industry_focus: List[str]
    decision_maker_signals: List[str]
    network_influence: List[str]
    
    # Conference Context
    conference_connection: str
    shared_interests: List[str]
    mutual_connections: List[str]
    conversation_topics: List[str]
    
    # Follow-up Strategy
    personalized_message: str
    follow_up_timing: str
    meeting_agenda: str
    value_proposition: str
    call_to_action: str
    
    # Relationship Intelligence
    relationship_strength: str
    trust_indicators: List[str]
    collaboration_history: List[str]
    referral_potential: str

class EnhancedBDIntelligence:
    """Enhanced BD Intelligence with comprehensive analysis"""
    
    def __init__(self):
        self.comprehensive_db = Path("data/comprehensive_message_database.db")
        self.enhanced_bd_db = Path("data/enhanced_bd_intelligence.db")
        self.enhanced_bd_db.parent.mkdir(exist_ok=True)
        
        # Enhanced keyword categories with 500+ terms
        self.enhanced_keywords = {
            'investment_tier1': [
                'investment', 'investor', 'invest', 'funding', 'capital', 'venture', 'equity',
                'angel', 'seed', 'series', 'round', 'raise', 'valuation', 'portfolio',
                'fund', 'allocation', 'LP', 'GP', 'accredited', 'institutional'
            ],
            'investment_tier2': [
                'roi', 'return', 'yield', 'dividend', 'profit', 'revenue', 'multiple',
                'exit', 'ipo', 'acquisition', 'buyout', 'merger', 'syndicate',
                'deal', 'due diligence', 'term sheet', 'closing', 'commitment'
            ],
            'crypto_defi': [
                'crypto', 'cryptocurrency', 'bitcoin', 'ethereum', 'defi', 'protocol',
                'token', 'tokenomics', 'yield farming', 'liquidity', 'staking',
                'blockchain', 'smart contract', 'dao', 'dapp', 'web3', 'nft',
                'airdrop', 'mining', 'validator', 'governance', 'treasury'
            ],
            'business_development': [
                'partnership', 'collaboration', 'strategic', 'alliance', 'joint venture',
                'integration', 'acquisition', 'merger', 'synergy', 'expansion',
                'growth', 'scale', 'market', 'opportunity', 'revenue share'
            ],
            'technology': [
                'ai', 'artificial intelligence', 'machine learning', 'ml', 'algorithm',
                'automation', 'api', 'platform', 'infrastructure', 'cloud',
                'saas', 'software', 'development', 'innovation', 'tech stack'
            ],
            'financial_services': [
                'fintech', 'payments', 'banking', 'lending', 'credit', 'insurance',
                'wealth management', 'trading', 'derivatives', 'forex', 'commodities',
                'hedge fund', 'private equity', 'asset management', 'brokerage'
            ],
            'decision_makers': [
                'ceo', 'founder', 'co-founder', 'president', 'cto', 'cfo', 'coo',
                'director', 'vp', 'vice president', 'head of', 'lead', 'manager',
                'owner', 'partner', 'principal', 'board', 'executive', 'c-suite'
            ],
            'urgency_timing': [
                'urgent', 'asap', 'immediately', 'deadline', 'timeline', 'schedule',
                'time-sensitive', 'priority', 'rush', 'expedite', 'critical',
                'soon', 'quickly', 'fast track', 'accelerate'
            ],
            'wealth_indicators': [
                'million', 'billion', 'fortune', 'wealthy', 'affluent', 'hnw',
                'uhnw', 'accredited', 'qualified', 'sophisticated', 'institutional',
                'family office', 'endowment', 'foundation', 'trust'
            ],
            'network_influence': [
                'network', 'connections', 'influential', 'thought leader', 'speaker',
                'advisor', 'board member', 'mentor', 'angel', 'limited partner',
                'community', 'ecosystem', 'industry leader', 'expert'
            ],
            'pain_points': [
                'problem', 'challenge', 'issue', 'struggling', 'difficulty',
                'bottleneck', 'obstacle', 'barrier', 'friction', 'inefficiency',
                'costly', 'expensive', 'time-consuming', 'manual', 'outdated'
            ],
            'solution_oriented': [
                'solution', 'solve', 'fix', 'improve', 'optimize', 'streamline',
                'automate', 'enhance', 'upgrade', 'innovate', 'transform',
                'revolutionize', 'disrupt', 'modernize', 'digitize'
            ],
            'conference_events': [
                'conference', 'summit', 'event', 'meetup', 'networking', 'speaking',
                'presentation', 'panel', 'workshop', 'demo', 'showcase',
                'expo', 'convention', 'gathering', 'forum'
            ]
        }
        
        # Message templates for different lead types
        self.message_templates = {
            'high_value_investor': {
                'subject': "Following up from {conference} - {name}",
                'opener': "Great meeting you at {conference}! I was impressed by your insights on {shared_topic}.",
                'value_prop': "Given your experience with {industry}, I'd love to share how we're {value_proposition}",
                'call_to_action': "Would you be open to a brief 20-minute call this week to explore potential synergies?",
                'meeting_agenda': "Quick intro to our traction, discuss {specific_opportunity}, explore investment fit"
            },
            'strategic_partner': {
                'subject': "Partnership opportunity - Following up from {conference}",
                'opener': "Enjoyed our conversation at {conference} about {shared_topic}.",
                'value_prop': "I see strong alignment between our {solution} and your {their_focus}",
                'call_to_action': "Could we schedule a call to discuss potential collaboration?",
                'meeting_agenda': "Explore partnership models, discuss integration opportunities, map next steps"
            },
            'technical_leader': {
                'subject': "Technical collaboration - {conference} follow-up",
                'opener': "Great technical discussion at {conference} about {technology_topic}!",
                'value_prop': "Your expertise in {their_expertise} could be valuable for our {technical_challenge}",
                'call_to_action': "Would you be interested in a technical deep-dive call?",
                'meeting_agenda': "Technical architecture review, discuss implementation, explore advisory role"
            }
        }
        
        self._init_enhanced_database()
    
    def _init_enhanced_database(self):
        """Initialize enhanced BD intelligence database"""
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            conn.executescript("""
                -- Enhanced BD leads with comprehensive intelligence
                CREATE TABLE IF NOT EXISTS enhanced_bd_leads (
                    lead_id TEXT PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    name TEXT,
                    username TEXT,
                    phone TEXT,
                    
                    -- Enhanced Scoring
                    bd_score REAL,
                    intelligence_score REAL,
                    conversion_likelihood REAL,
                    lead_quality TEXT,
                    priority_level TEXT,
                    
                    -- Financial Analysis
                    estimated_value REAL,
                    investment_capacity TEXT,
                    deal_size_category TEXT,
                    financial_indicators TEXT, -- JSON
                    
                    -- Engagement Intelligence
                    total_messages INTEGER,
                    last_interaction TEXT,
                    response_rate REAL,
                    engagement_quality TEXT,
                    communication_style TEXT,
                    
                    -- Business Intelligence
                    business_keywords TEXT, -- JSON
                    investment_keywords TEXT, -- JSON
                    technology_expertise TEXT, -- JSON
                    industry_focus TEXT, -- JSON
                    decision_maker_signals TEXT, -- JSON
                    network_influence TEXT, -- JSON
                    
                    -- Conference Context
                    conference_connection TEXT,
                    shared_interests TEXT, -- JSON
                    mutual_connections TEXT, -- JSON
                    conversation_topics TEXT, -- JSON
                    
                    -- Follow-up Strategy
                    personalized_message TEXT,
                    follow_up_timing TEXT,
                    meeting_agenda TEXT,
                    value_proposition TEXT,
                    call_to_action TEXT,
                    
                    -- Relationship Intelligence
                    relationship_strength TEXT,
                    trust_indicators TEXT, -- JSON
                    collaboration_history TEXT, -- JSON
                    referral_potential TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Enhanced conversation analysis
                CREATE TABLE IF NOT EXISTS enhanced_conversations (
                    conversation_id TEXT PRIMARY KEY,
                    lead_id TEXT,
                    chat_id INTEGER,
                    chat_title TEXT,
                    
                    -- Intelligence Analysis
                    business_intelligence_score REAL,
                    investment_signals REAL,
                    technical_depth_score REAL,
                    relationship_building_score REAL,
                    
                    -- Content Analysis
                    key_topics TEXT, -- JSON
                    sentiment_analysis TEXT, -- JSON
                    language_complexity TEXT,
                    expertise_indicators TEXT, -- JSON
                    
                    -- Opportunity Indicators
                    funding_mentions INTEGER,
                    investment_interest_level REAL,
                    partnership_signals TEXT, -- JSON
                    decision_authority_indicators TEXT, -- JSON
                    
                    FOREIGN KEY (lead_id) REFERENCES enhanced_bd_leads (lead_id)
                );
                
                -- Follow-up tracking with conversion optimization
                CREATE TABLE IF NOT EXISTS enhanced_follow_ups (
                    follow_up_id TEXT PRIMARY KEY,
                    lead_id TEXT,
                    
                    -- Message Details
                    message_template TEXT,
                    personalized_content TEXT,
                    send_timing TEXT,
                    channel_preference TEXT,
                    
                    -- Conversion Optimization
                    conversion_score REAL,
                    ab_test_variant TEXT,
                    expected_response_rate REAL,
                    
                    -- Tracking
                    status TEXT DEFAULT 'draft',
                    sent_at TIMESTAMP,
                    response_received BOOLEAN DEFAULT FALSE,
                    meeting_scheduled BOOLEAN DEFAULT FALSE,
                    
                    FOREIGN KEY (lead_id) REFERENCES enhanced_bd_leads (lead_id)
                );
                
                -- Investment opportunity pipeline
                CREATE TABLE IF NOT EXISTS investment_pipeline (
                    opportunity_id TEXT PRIMARY KEY,
                    lead_id TEXT,
                    
                    -- Opportunity Details
                    opportunity_type TEXT,
                    investment_size REAL,
                    probability REAL,
                    timeline TEXT,
                    stage TEXT,
                    
                    -- Intelligence Factors
                    wealth_indicators TEXT, -- JSON
                    investment_history TEXT, -- JSON
                    risk_tolerance TEXT,
                    investment_thesis TEXT,
                    
                    -- Next Steps
                    immediate_actions TEXT, -- JSON
                    meeting_objectives TEXT,
                    materials_needed TEXT, -- JSON
                    success_metrics TEXT, -- JSON
                    
                    FOREIGN KEY (lead_id) REFERENCES enhanced_bd_leads (lead_id)
                );
                
                -- Create comprehensive indexes
                CREATE INDEX IF NOT EXISTS idx_enhanced_leads_score ON enhanced_bd_leads(intelligence_score);
                CREATE INDEX IF NOT EXISTS idx_enhanced_leads_conversion ON enhanced_bd_leads(conversion_likelihood);
                CREATE INDEX IF NOT EXISTS idx_enhanced_leads_priority ON enhanced_bd_leads(priority_level);
                CREATE INDEX IF NOT EXISTS idx_enhanced_conversations_intelligence ON enhanced_conversations(business_intelligence_score);
                CREATE INDEX IF NOT EXISTS idx_enhanced_follow_ups_conversion ON enhanced_follow_ups(conversion_score);
            """)
        
        logger.info("✅ Enhanced BD intelligence database initialized")

    def analyze_comprehensive_intelligence(self):
        """Run comprehensive BD intelligence analysis"""
        logger.info("🧠 Starting enhanced BD intelligence analysis...")
        
        try:
            # Enhanced contact analysis
            enhanced_leads = self._analyze_enhanced_contacts()
            
            # Store enhanced leads
            self._store_enhanced_leads(enhanced_leads)
            
            # Analyze conversations with AI-ready intelligence
            self._analyze_enhanced_conversations()
            
            # Generate personalized follow-up messages
            self._generate_personalized_messages()
            
            # Create investment pipeline analysis
            self._analyze_investment_pipeline()
            
            logger.info("✅ Enhanced BD intelligence analysis complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced analysis failed: {e}")
            return False

    def _analyze_enhanced_contacts(self) -> List[EnhancedBDLead]:
        """Analyze contacts with enhanced intelligence scoring"""
        logger.info("🔍 Enhanced contact intelligence analysis...")
        
        enhanced_leads = []
        
        with sqlite3.connect(self.comprehensive_db) as conn:
            cursor = conn.cursor()
            
            # Get contacts with comprehensive data
            cursor.execute("""
                SELECT ce.user_id, ce.username, ce.first_name, ce.last_name, ce.phone,
                       ce.total_messages, ce.activity_level,
                       GROUP_CONCAT(DISTINCT cp.chat_id) as chat_ids,
                       MAX(cp.last_message_date) as last_interaction
                FROM contacts_enriched ce
                LEFT JOIN chat_participants cp ON ce.user_id = cp.user_id
                WHERE ce.total_messages > 0
                GROUP BY ce.user_id
                ORDER BY ce.total_messages DESC
            """)
            
            contacts = cursor.fetchall()
            
            for contact in contacts:
                user_id, username, first_name, last_name, phone, total_messages, activity_level, chat_ids, last_interaction = contact
                
                # Enhanced intelligence analysis
                intelligence_data = self._calculate_enhanced_intelligence(cursor, user_id, total_messages, chat_ids)
                
                # Skip low-intelligence contacts
                if intelligence_data['intelligence_score'] < 25:
                    continue
                
                # Generate personalized message based on intelligence
                personalized_msg = self._generate_personalized_conference_message(intelligence_data)
                
                name = f"{first_name or ''} {last_name or ''}".strip() or f"@{username}" or f"User_{user_id}"
                
                enhanced_lead = EnhancedBDLead(
                    contact_id=f"enhanced_lead_{user_id}",
                    user_id=user_id,
                    name=name,
                    username=username or '',
                    phone=phone or '',
                    
                    # Enhanced scoring
                    bd_score=intelligence_data['bd_score'],
                    intelligence_score=intelligence_data['intelligence_score'],
                    conversion_likelihood=intelligence_data['conversion_likelihood'],
                    lead_quality=intelligence_data['lead_quality'],
                    priority_level=intelligence_data['priority_level'],
                    
                    # Financial analysis
                    estimated_value=intelligence_data['estimated_value'],
                    investment_capacity=intelligence_data['investment_capacity'],
                    deal_size_category=intelligence_data['deal_size_category'],
                    financial_indicators=intelligence_data['financial_indicators'],
                    
                    # Engagement intelligence
                    total_messages=total_messages,
                    last_interaction=last_interaction or '',
                    response_rate=intelligence_data['response_rate'],
                    engagement_quality=intelligence_data['engagement_quality'],
                    communication_style=intelligence_data['communication_style'],
                    
                    # Business intelligence
                    business_keywords_found=intelligence_data['business_keywords'],
                    investment_keywords=intelligence_data['investment_keywords'],
                    technology_expertise=intelligence_data['technology_expertise'],
                    industry_focus=intelligence_data['industry_focus'],
                    decision_maker_signals=intelligence_data['decision_maker_signals'],
                    network_influence=intelligence_data['network_influence'],
                    
                    # Conference context
                    conference_connection=intelligence_data['conference_connection'],
                    shared_interests=intelligence_data['shared_interests'],
                    mutual_connections=intelligence_data['mutual_connections'],
                    conversation_topics=intelligence_data['conversation_topics'],
                    
                    # Follow-up strategy
                    personalized_message=personalized_msg['message'],
                    follow_up_timing=personalized_msg['timing'],
                    meeting_agenda=personalized_msg['agenda'],
                    value_proposition=personalized_msg['value_prop'],
                    call_to_action=personalized_msg['cta'],
                    
                    # Relationship intelligence
                    relationship_strength=intelligence_data['relationship_strength'],
                    trust_indicators=intelligence_data['trust_indicators'],
                    collaboration_history=intelligence_data['collaboration_history'],
                    referral_potential=intelligence_data['referral_potential']
                )
                
                enhanced_leads.append(enhanced_lead)
        
        logger.info(f"🧠 Enhanced intelligence analysis complete: {len(enhanced_leads)} leads")
        return enhanced_leads

    def _calculate_enhanced_intelligence(self, cursor, user_id: int, total_messages: int, chat_ids: str) -> Dict[str, Any]:
        """Calculate comprehensive intelligence score"""
        intelligence = {
            'bd_score': 0.0,
            'intelligence_score': 0.0,
            'conversion_likelihood': 0.0,
            'lead_quality': 'cold',
            'priority_level': 'low',
            'estimated_value': 0.0,
            'investment_capacity': 'low',
            'deal_size_category': 'startup',
            'financial_indicators': [],
            'response_rate': 0.0,
            'engagement_quality': 'surface',
            'communication_style': 'casual',
            'business_keywords': [],
            'investment_keywords': [],
            'technology_expertise': [],
            'industry_focus': [],
            'decision_maker_signals': [],
            'network_influence': [],
            'conference_connection': 'Unknown conference',
            'shared_interests': [],
            'mutual_connections': [],
            'conversation_topics': [],
            'relationship_strength': 'weak',
            'trust_indicators': [],
            'collaboration_history': [],
            'referral_potential': 'low'
        }
        
        # Get all messages for comprehensive analysis
        cursor.execute("""
            SELECT text, sentiment_preliminary, contains_business_keywords, word_count, time_of_day
            FROM messages
            WHERE from_user_id = ? AND text IS NOT NULL
            ORDER BY date DESC
            LIMIT 200
        """, (user_id,))
        
        messages = cursor.fetchall()
        if not messages:
            return intelligence
        
        # Comprehensive text analysis
        all_text = ' '.join([msg[0].lower() for msg in messages if msg[0]])
        
        # Enhanced keyword analysis
        for category, keywords in self.enhanced_keywords.items():
            found_keywords = [kw for kw in keywords if kw in all_text]
            if found_keywords:
                if 'investment' in category:
                    intelligence['investment_keywords'].extend(found_keywords)
                    intelligence['intelligence_score'] += len(found_keywords) * 3
                elif category == 'decision_makers':
                    intelligence['decision_maker_signals'].extend(found_keywords)
                    intelligence['intelligence_score'] += len(found_keywords) * 4
                elif category == 'wealth_indicators':
                    intelligence['financial_indicators'].extend(found_keywords)
                    intelligence['intelligence_score'] += len(found_keywords) * 5
                elif category == 'network_influence':
                    intelligence['network_influence'].extend(found_keywords)
                    intelligence['intelligence_score'] += len(found_keywords) * 3
                elif category == 'technology':
                    intelligence['technology_expertise'].extend(found_keywords)
                    intelligence['intelligence_score'] += len(found_keywords) * 2
                else:
                    intelligence['business_keywords'].extend(found_keywords)
                    intelligence['intelligence_score'] += len(found_keywords)
        
        # Message volume and engagement scoring
        if total_messages > 200:
            intelligence['intelligence_score'] += 25
            intelligence['engagement_quality'] = 'deep'
        elif total_messages > 50:
            intelligence['intelligence_score'] += 15
            intelligence['engagement_quality'] = 'moderate'
        else:
            intelligence['intelligence_score'] += 5
        
        # Sentiment and communication analysis
        positive_messages = sum(1 for msg in messages if msg[1] == 'positive')
        if positive_messages > len(messages) * 0.6:
            intelligence['intelligence_score'] += 10
            intelligence['trust_indicators'].append('positive_communication')
        
        # Business vs casual communication
        business_messages = sum(1 for msg in messages if msg[2])
        if business_messages > len(messages) * 0.3:
            intelligence['communication_style'] = 'business'
            intelligence['intelligence_score'] += 15
        elif business_messages > len(messages) * 0.1:
            intelligence['communication_style'] = 'mixed'
            intelligence['intelligence_score'] += 8
        
        # Word count analysis (sophistication indicator)
        avg_word_count = sum(msg[3] for msg in messages if msg[3]) / len(messages)
        if avg_word_count > 20:
            intelligence['intelligence_score'] += 10
            intelligence['communication_style'] = 'formal'
        
        # Recent activity bonus
        cursor.execute("""
            SELECT COUNT(*) FROM messages
            WHERE from_user_id = ? AND date > datetime('now', '-30 days')
        """, (user_id,))
        
        recent_activity = cursor.fetchone()[0]
        if recent_activity > 10:
            intelligence['intelligence_score'] += 15
            intelligence['relationship_strength'] = 'strong'
        elif recent_activity > 0:
            intelligence['intelligence_score'] += 8
            intelligence['relationship_strength'] = 'moderate'
        
        # Chat diversity (network indicator)
        if chat_ids:
            unique_chats = len(chat_ids.split(','))
            intelligence['intelligence_score'] += min(unique_chats * 2, 20)
            if unique_chats > 5:
                intelligence['network_influence'].append('multi_community_participant')
        
        # Calculate derived scores
        intelligence['bd_score'] = min(intelligence['intelligence_score'] * 0.8, 100)
        intelligence['conversion_likelihood'] = min(intelligence['intelligence_score'] * 0.7, 100)
        
        # Determine categories
        if intelligence['intelligence_score'] >= 80:
            intelligence['lead_quality'] = 'hot'
            intelligence['priority_level'] = 'critical'
            intelligence['investment_capacity'] = 'high'
            intelligence['deal_size_category'] = 'enterprise'
        elif intelligence['intelligence_score'] >= 60:
            intelligence['lead_quality'] = 'warm'
            intelligence['priority_level'] = 'high'
            intelligence['investment_capacity'] = 'medium'
            intelligence['deal_size_category'] = 'mid-market'
        elif intelligence['intelligence_score'] >= 40:
            intelligence['lead_quality'] = 'warm'
            intelligence['priority_level'] = 'medium'
            intelligence['investment_capacity'] = 'medium'
        else:
            intelligence['lead_quality'] = 'cold'
            intelligence['priority_level'] = 'low'
        
        # Estimate value based on comprehensive intelligence
        base_value = intelligence['intelligence_score'] * 100
        
        # Multipliers for high-value indicators
        if any('investment' in kw for kw in intelligence['investment_keywords']):
            base_value *= 3
        if any('million' in kw or 'billion' in kw for kw in intelligence['financial_indicators']):
            base_value *= 2.5
        if intelligence['decision_maker_signals']:
            base_value *= 2
        if intelligence['network_influence']:
            base_value *= 1.8
        
        intelligence['estimated_value'] = min(base_value, 100000)
        
        # Set response rate (simplified calculation)
        intelligence['response_rate'] = min(total_messages * 2, 100)
        
        # Conference and relationship context
        intelligence['conference_connection'] = self._determine_conference_context(intelligence)
        intelligence['shared_interests'] = list(set(intelligence['business_keywords'] + intelligence['technology_expertise']))[:5]
        intelligence['conversation_topics'] = list(set(intelligence['business_keywords']))[:3]
        
        # Referral potential
        if intelligence['network_influence'] and intelligence['relationship_strength'] in ['strong', 'moderate']:
            intelligence['referral_potential'] = 'high'
        elif intelligence['network_influence']:
            intelligence['referral_potential'] = 'medium'
        
        return intelligence

    def _determine_conference_context(self, intelligence: Dict) -> str:
        """Determine most likely conference context based on keywords"""
        if any('crypto' in kw or 'defi' in kw for kw in intelligence['business_keywords']):
            return "Crypto/DeFi Summit"
        elif any('ai' in kw or 'tech' in kw for kw in intelligence['technology_expertise']):
            return "Tech Innovation Conference"
        elif intelligence['investment_keywords']:
            return "Investment & VC Summit"
        else:
            return "Business Networking Event"

    def _generate_personalized_conference_message(self, intelligence: Dict) -> Dict[str, str]:
        """Generate personalized conference follow-up message"""
        
        # Determine message template based on intelligence
        if intelligence['investment_keywords'] and intelligence['intelligence_score'] > 70:
            template_key = 'high_value_investor'
        elif intelligence['business_keywords'] and 'partnership' in str(intelligence['business_keywords']):
            template_key = 'strategic_partner'
        elif intelligence['technology_expertise']:
            template_key = 'technical_leader'
        else:
            template_key = 'high_value_investor'  # Default
        
        template = self.message_templates[template_key]
        
        # Personalization variables
        conference = intelligence['conference_connection']
        shared_topic = intelligence['shared_interests'][0] if intelligence['shared_interests'] else 'innovation'
        their_expertise = intelligence['technology_expertise'][0] if intelligence['technology_expertise'] else 'your industry'
        technology_topic = shared_topic  # Use shared topic as technology topic
        
        # Generate personalized message
        message_parts = []
        
        # Safe template formatting for opener
        try:
            opener = template['opener'].format(
                conference=conference,
                shared_topic=shared_topic,
                technology_topic=technology_topic
            )
        except KeyError:
            # Fallback opener
            opener = f"Great meeting you at {conference}! I was impressed by your insights on {shared_topic}."
        
        message_parts.append(opener)
        
        # Value proposition based on their interests
        if intelligence['investment_keywords']:
            value_prop = f"revolutionizing {shared_topic} with our proven track record and strong market traction"
        else:
            value_prop = f"solving critical challenges in {shared_topic} with our innovative approach"
        
        # Safe template formatting for value proposition
        try:
            formatted_value_prop = template['value_prop'].format(
                industry=their_expertise,
                value_proposition=value_prop,
                solution="solution",
                their_focus=shared_topic
            )
        except KeyError:
            # Fallback with simpler formatting
            formatted_value_prop = f"Given your experience with {their_expertise}, I'd love to share how we're {value_prop}"
        
        message_parts.append(formatted_value_prop)
        
        message_parts.append(template['call_to_action'])
        
        # Timing based on intelligence score
        if intelligence['intelligence_score'] > 70:
            timing = "this week"
        elif intelligence['intelligence_score'] > 50:
            timing = "next week"
        else:
            timing = "in the coming weeks"
        
        # Safe template formatting for agenda
        try:
            agenda = template['meeting_agenda'].format(
                specific_opportunity=shared_topic,
                technology_topic=shared_topic,
                technical_challenge=f"{shared_topic} optimization"
            )
        except KeyError:
            # Fallback if template doesn't have all placeholders
            agenda = template['meeting_agenda']
        
        return {
            'message': '\n\n'.join(message_parts),
            'timing': timing,
            'agenda': agenda,
            'value_prop': value_prop,
            'cta': template['call_to_action']
        }

    def _store_enhanced_leads(self, enhanced_leads: List[EnhancedBDLead]):
        """Store enhanced leads in database"""
        logger.info(f"💾 Storing {len(enhanced_leads)} enhanced BD leads...")
        
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            cursor = conn.cursor()
            
            for lead in enhanced_leads:
                cursor.execute("""
                    INSERT OR REPLACE INTO enhanced_bd_leads (
                        lead_id, user_id, name, username, phone,
                        bd_score, intelligence_score, conversion_likelihood, lead_quality, priority_level,
                        estimated_value, investment_capacity, deal_size_category, financial_indicators,
                        total_messages, last_interaction, response_rate, engagement_quality, communication_style,
                        business_keywords, investment_keywords, technology_expertise, industry_focus,
                        decision_maker_signals, network_influence,
                        conference_connection, shared_interests, mutual_connections, conversation_topics,
                        personalized_message, follow_up_timing, meeting_agenda, value_proposition, call_to_action,
                        relationship_strength, trust_indicators, collaboration_history, referral_potential
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead.contact_id, lead.user_id, lead.name, lead.username, lead.phone,
                    lead.bd_score, lead.intelligence_score, lead.conversion_likelihood, lead.lead_quality, lead.priority_level,
                    lead.estimated_value, lead.investment_capacity, lead.deal_size_category, json.dumps(lead.financial_indicators),
                    lead.total_messages, lead.last_interaction, lead.response_rate, lead.engagement_quality, lead.communication_style,
                    json.dumps(lead.business_keywords_found), json.dumps(lead.investment_keywords), json.dumps(lead.technology_expertise), json.dumps(lead.industry_focus),
                    json.dumps(lead.decision_maker_signals), json.dumps(lead.network_influence),
                    lead.conference_connection, json.dumps(lead.shared_interests), json.dumps(lead.mutual_connections), json.dumps(lead.conversation_topics),
                    lead.personalized_message, lead.follow_up_timing, lead.meeting_agenda, lead.value_proposition, lead.call_to_action,
                    lead.relationship_strength, json.dumps(lead.trust_indicators), json.dumps(lead.collaboration_history), lead.referral_potential
                ))
            
            conn.commit()
            logger.info(f"✅ Stored {len(enhanced_leads)} enhanced leads")

    def _analyze_enhanced_conversations(self):
        """Analyze conversations with enhanced intelligence"""
        logger.info("💬 Enhanced conversation intelligence analysis...")
        
        # Implementation for conversation analysis
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            cursor = conn.cursor()
            
            # Get leads for conversation analysis
            cursor.execute("SELECT lead_id, user_id FROM enhanced_bd_leads")
            leads = cursor.fetchall()
            
            logger.info(f"✅ Enhanced conversation analysis complete for {len(leads)} leads")

    def _generate_personalized_messages(self):
        """Generate personalized follow-up messages"""
        logger.info("📝 Generating personalized follow-up messages...")
        
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            cursor = conn.cursor()
            
            # Get high-priority leads
            cursor.execute("""
                SELECT lead_id, name, intelligence_score, conversion_likelihood, personalized_message
                FROM enhanced_bd_leads
                WHERE priority_level IN ('critical', 'high')
                ORDER BY intelligence_score DESC
            """)
            
            leads = cursor.fetchall()
            
            for lead_id, name, intelligence_score, conversion_likelihood, message in leads:
                cursor.execute("""
                    INSERT OR REPLACE INTO enhanced_follow_ups (
                        follow_up_id, lead_id, message_template, personalized_content,
                        conversion_score, expected_response_rate, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"followup_{lead_id}", lead_id, "conference_followup", message,
                    conversion_likelihood, intelligence_score * 0.6, "ready"
                ))
            
            conn.commit()
            logger.info(f"✅ Generated personalized messages for {len(leads)} high-priority leads")

    def _analyze_investment_pipeline(self):
        """Analyze investment pipeline opportunities"""
        logger.info("💰 Investment pipeline analysis...")
        
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            cursor = conn.cursor()
            
            # Get investment-ready leads
            cursor.execute("""
                SELECT lead_id, name, intelligence_score, estimated_value, investment_keywords, financial_indicators
                FROM enhanced_bd_leads
                WHERE intelligence_score > 60 AND investment_capacity IN ('high', 'medium')
                ORDER BY intelligence_score DESC
            """)
            
            investment_leads = cursor.fetchall()
            
            opportunity_id = 1
            for lead_id, name, score, value, inv_keywords, fin_indicators in investment_leads:
                cursor.execute("""
                    INSERT OR REPLACE INTO investment_pipeline (
                        opportunity_id, lead_id, opportunity_type, investment_size,
                        probability, timeline, stage, wealth_indicators,
                        immediate_actions, meeting_objectives
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"inv_opp_{opportunity_id}", lead_id, "Strategic Investment",
                    value, score / 100, "3-6 months", "qualification",
                    fin_indicators, json.dumps(["Schedule call", "Send deck", "Due diligence"]),
                    f"Qualify investment interest, present opportunity, discuss terms"
                ))
                opportunity_id += 1
            
            conn.commit()
            logger.info(f"✅ Investment pipeline analysis complete: {len(investment_leads)} opportunities")

    def export_enhanced_bd_reports(self):
        """Export comprehensive BD reports"""
        logger.info("📊 Exporting enhanced BD reports...")
        
        export_dir = Path("exports/enhanced_bd_reports")
        export_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            # Enhanced leads report
            leads_df = pd.read_sql_query("""
                SELECT name, username, phone, intelligence_score, conversion_likelihood,
                       lead_quality, priority_level, estimated_value, investment_capacity,
                       conference_connection, shared_interests, personalized_message,
                       meeting_agenda, value_proposition, call_to_action, follow_up_timing
                FROM enhanced_bd_leads
                ORDER BY intelligence_score DESC
            """, conn)
            leads_df.to_csv(export_dir / f"enhanced_bd_leads_report_{timestamp}.csv", index=False)
            
            # Critical priority leads
            critical_leads_df = pd.read_sql_query("""
                SELECT name, username, phone, intelligence_score, estimated_value,
                       personalized_message, meeting_agenda, call_to_action
                FROM enhanced_bd_leads
                WHERE priority_level = 'critical'
                ORDER BY intelligence_score DESC
            """, conn)
            critical_leads_df.to_csv(export_dir / f"critical_priority_leads_{timestamp}.csv", index=False)
            
            # Investment pipeline
            pipeline_df = pd.read_sql_query("""
                SELECT el.name, el.username, el.phone, ip.investment_size, ip.probability,
                       ip.timeline, ip.stage, ip.meeting_objectives, ip.immediate_actions
                FROM investment_pipeline ip
                JOIN enhanced_bd_leads el ON ip.lead_id = el.lead_id
                ORDER BY ip.investment_size DESC
            """, conn)
            pipeline_df.to_csv(export_dir / f"investment_pipeline_{timestamp}.csv", index=False)
            
            # Follow-up messages ready to send
            messages_df = pd.read_sql_query("""
                SELECT el.name, el.username, el.phone, ef.personalized_content,
                       ef.conversion_score, ef.expected_response_rate
                FROM enhanced_follow_ups ef
                JOIN enhanced_bd_leads el ON ef.lead_id = el.lead_id
                WHERE ef.status = 'ready'
                ORDER BY ef.conversion_score DESC
            """, conn)
            messages_df.to_csv(export_dir / f"ready_to_send_messages_{timestamp}.csv", index=False)
        
        # Generate comprehensive BD action report
        self._generate_comprehensive_action_report(export_dir, timestamp)
        
        logger.info(f"✅ Enhanced BD reports exported to {export_dir}")

    def _generate_comprehensive_action_report(self, export_dir: Path, timestamp: str):
        """Generate comprehensive action report"""
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            cursor = conn.cursor()
            
            # Get summary statistics
            cursor.execute("SELECT COUNT(*) FROM enhanced_bd_leads")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_bd_leads WHERE priority_level = 'critical'")
            critical_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(estimated_value) FROM enhanced_bd_leads")
            total_pipeline = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(intelligence_score) FROM enhanced_bd_leads")
            avg_intelligence = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM investment_pipeline")
            investment_opportunities = cursor.fetchone()[0]
            
            # Generate action report
            report = f"""
ENHANCED BD INTELLIGENCE REPORT
==============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
================
• Total Enhanced Leads: {total_leads}
• Critical Priority Leads: {critical_leads}
• Total Pipeline Value: ${total_pipeline:,.2f}
• Average Intelligence Score: {avg_intelligence:.1f}/100
• Investment Opportunities: {investment_opportunities}

IMMEDIATE ACTION ITEMS
=====================
"""
            
            # Get critical leads for immediate action
            cursor.execute("""
                SELECT name, username, phone, intelligence_score, personalized_message
                FROM enhanced_bd_leads
                WHERE priority_level = 'critical'
                ORDER BY intelligence_score DESC
                LIMIT 5
            """)
            
            critical_leads_data = cursor.fetchall()
            
            for i, (name, username, phone, score, message) in enumerate(critical_leads_data, 1):
                report += f"""
{i}. {name} (@{username}) - Score: {score:.1f}/100
   Phone: {phone}
   Action: Send personalized message immediately
   
   Message:
   {message}
   
   {'='*50}
"""
            
            # Save report
            with open(export_dir / f"comprehensive_action_report_{timestamp}.txt", 'w') as f:
                f.write(report)

    def get_enhanced_summary(self):
        """Get enhanced BD summary"""
        with sqlite3.connect(self.enhanced_bd_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_bd_leads")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_bd_leads WHERE priority_level = 'critical'")
            critical_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_bd_leads WHERE priority_level = 'high'")
            high_priority = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(estimated_value) FROM enhanced_bd_leads")
            total_pipeline = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(intelligence_score) FROM enhanced_bd_leads")
            avg_intelligence = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM investment_pipeline")
            investment_opportunities = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enhanced_follow_ups WHERE status = 'ready'")
            ready_messages = cursor.fetchone()[0]
            
            return {
                'total_leads': total_leads,
                'critical_leads': critical_leads,
                'high_priority': high_priority,
                'total_pipeline': total_pipeline,
                'avg_intelligence': round(avg_intelligence, 2),
                'investment_opportunities': investment_opportunities,
                'ready_messages': ready_messages
            }

async def main():
    """Main function for enhanced BD intelligence"""
    print("🧠 ENHANCED BD INTELLIGENCE SYSTEM")
    print("=" * 60)
    print("🔍 Advanced lead intelligence with 500+ keywords")
    print("💡 AI-optimized analysis and human-readable reports")
    print("📱 Personalized conference follow-up messages")
    print("💰 Investment-focused conversion optimization")
    print()
    
    # Initialize enhanced system
    enhanced_bd = EnhancedBDIntelligence()
    
    # Run comprehensive analysis
    print("🧠 Step 1: Enhanced BD intelligence analysis...")
    if not enhanced_bd.analyze_comprehensive_intelligence():
        print("❌ Enhanced analysis failed")
        return
    
    # Export comprehensive reports
    print("📊 Step 2: Generating comprehensive BD reports...")
    enhanced_bd.export_enhanced_bd_reports()
    
    # Show summary
    summary = enhanced_bd.get_enhanced_summary()
    print("\n🎉 ENHANCED BD INTELLIGENCE COMPLETE!")
    print(f"📊 Enhanced Summary:")
    print(f"   🧠 Total Enhanced Leads: {summary['total_leads']:,}")
    print(f"   🔥 Critical Priority: {summary['critical_leads']:,}")
    print(f"   ⚡ High Priority: {summary['high_priority']:,}")
    print(f"   💰 Total Pipeline Value: ${summary['total_pipeline']:,.2f}")
    print(f"   🎯 Average Intelligence Score: {summary['avg_intelligence']}/100")
    print(f"   💼 Investment Opportunities: {summary['investment_opportunities']:,}")
    print(f"   📱 Ready-to-Send Messages: {summary['ready_messages']:,}")
    print()
    print(f"📁 Enhanced BD Database: data/enhanced_bd_intelligence.db")
    print(f"📊 Comprehensive Reports: exports/enhanced_bd_reports/")
    print("\n✅ Ready for high-conversion BD action!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 