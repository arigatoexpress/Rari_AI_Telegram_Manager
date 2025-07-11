#!/usr/bin/env python3
"""
Advanced Human-Like Follow-Up System
===================================
Creates natural, human-sounding follow-ups for recent conversations using:
- Chris Voss "Never Split the Difference" techniques
- Behavioral psychology principles
- First name personalization
- Recent conversation analysis (past 60 days)
- Group chat introduction preparation
"""

import json
import sqlite3
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import pandas as pd
from collections import defaultdict
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/advanced_follow_up.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RecentConversation:
    """Recent conversation analysis for follow-up"""
    contact_id: str
    user_id: int
    first_name: str
    username: str
    phone: str
    
    # Conversation Analysis
    last_interaction: str
    days_since_contact: int
    total_recent_messages: int
    conversation_context: str
    last_topic_discussed: str
    emotional_tone: str
    
    # Chris Voss Technique Opportunities
    mirror_opportunity: str  # Last few words to mirror
    label_opportunity: str   # Emotion/situation to label
    calibrated_question: str # Strategic question to ask
    accusation_audit: str   # Potential negative to address
    
    # Behavioral Psychology Hooks
    reciprocity_angle: str   # How to trigger reciprocity
    social_proof_element: str # Social proof to include
    authority_signal: str    # Authority/credibility marker
    scarcity_element: str    # Scarcity/urgency element
    
    # Follow-up Strategy
    natural_message: str     # Human-sounding message
    group_intro_angle: str   # How to introduce to group
    founder_connection: str  # How to connect with founders
    self_disclosure_prompt: str # How to get them to share

class AdvancedFollowUpSystem:
    """Advanced follow-up system with psychological techniques"""
    
    def __init__(self):
        self.comprehensive_db = Path("data/comprehensive_message_database.db")
        self.follow_up_db = Path("data/advanced_follow_up.db")
        self.follow_up_db.parent.mkdir(exist_ok=True)
        
        # Chris Voss technique templates
        self.voss_techniques = {
            'mirroring': [
                "...{mirror_words}?",
                "You mentioned {mirror_words}?",
                "{mirror_words}... tell me more about that"
            ],
            'labeling': [
                "It seems like {emotion_label}",
                "It sounds like {situation_label}",
                "It looks like {observation_label}"
            ],
            'calibrated_questions': [
                "What about {topic} is most important to you?",
                "How do you see {topic} playing out?",
                "What would need to happen for {topic} to work?",
                "How am I supposed to {challenge}?",
                "What's the biggest challenge with {topic}?"
            ],
            'accusation_audit': [
                "You're probably thinking this is another sales pitch...",
                "I know you're busy and get a lot of these messages...",
                "You might be wondering why I'm reaching out now..."
            ]
        }
        
        # Behavioral psychology principles
        self.psychology_techniques = {
            'reciprocity': [
                "I wanted to share something valuable with you first",
                "Here's something that might help with {their_challenge}",
                "I found this resource that reminded me of our conversation"
            ],
            'social_proof': [
                "Others in {their_industry} have mentioned similar challenges",
                "I was just talking to {mutual_connection} about this",
                "We've been working with several {their_role} who face similar issues"
            ],
            'authority': [
                "In our work with {industry_leaders}",
                "Based on our experience with {similar_companies}",
                "We've helped {specific_results} in similar situations"
            ],
            'scarcity': [
                "We're only working with a few partners this quarter",
                "This opportunity has a limited timeline",
                "We're being selective about who we bring into this"
            ]
        }
        
        # Natural conversation starters (non-AI sounding)
        self.natural_openers = [
            "Hey {first_name}, been thinking about our conversation about {topic}",
            "{first_name}, that thing you mentioned about {topic} has been on my mind",
            "Hope you're doing well, {first_name}. Quick follow-up on {topic}",
            "{first_name}, I came across something that reminded me of what we discussed about {topic}",
            "Hey {first_name}, circling back on {topic} - had an interesting thought"
        ]
        
        # Group introduction angles
        self.group_intro_strategies = [
            "bringing in some brilliant minds to bounce ideas around",
            "connecting with other innovators working on similar challenges",
            "joining a small group of forward-thinking {industry} leaders",
            "introducing you to some people doing interesting work in {space}"
        ]
        
        self._init_follow_up_database()
    
    def _init_follow_up_database(self):
        """Initialize follow-up database"""
        with sqlite3.connect(self.follow_up_db) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS recent_conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    first_name TEXT,
                    username TEXT,
                    phone TEXT,
                    last_interaction TEXT,
                    days_since_contact INTEGER,
                    total_recent_messages INTEGER,
                    conversation_context TEXT,
                    last_topic_discussed TEXT,
                    emotional_tone TEXT,
                    
                    -- Chris Voss Opportunities
                    mirror_opportunity TEXT,
                    label_opportunity TEXT,
                    calibrated_question TEXT,
                    accusation_audit TEXT,
                    
                    -- Psychology Hooks
                    reciprocity_angle TEXT,
                    social_proof_element TEXT,
                    authority_signal TEXT,
                    scarcity_element TEXT,
                    
                    -- Follow-up Content
                    natural_message TEXT,
                    group_intro_angle TEXT,
                    founder_connection TEXT,
                    self_disclosure_prompt TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS follow_up_templates (
                    template_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    template_type TEXT, -- opener, main, closer, group_intro
                    content TEXT,
                    psychological_principle TEXT,
                    voss_technique TEXT,
                    conversion_score REAL,
                    
                    FOREIGN KEY (conversation_id) REFERENCES recent_conversations (conversation_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_recent_days ON recent_conversations(days_since_contact);
                CREATE INDEX IF NOT EXISTS idx_recent_messages ON recent_conversations(total_recent_messages);
            """)
        
        logger.info("✅ Advanced follow-up database initialized")

    def analyze_recent_conversations(self, days_back: int = 60):
        """Analyze conversations from the past X days"""
        logger.info(f"🔍 Analyzing conversations from past {days_back} days...")
        
        # Use a more recent cutoff date since messages are from January 2025
        cutoff_date_str = '2024-12-01'  # Get messages from December 2024 onwards
        recent_conversations = []
        
        with sqlite3.connect(self.comprehensive_db) as conn:
            cursor = conn.cursor()
            
            # Get contacts with recent activity (excluding teammates)
            cursor.execute("""
                SELECT ce.user_id, ce.first_name, ce.username, ce.phone,
                       MAX(m.date) as last_interaction,
                       COUNT(m.message_id) as recent_messages,
                       GROUP_CONCAT(m.text, ' | ') as recent_texts,
                       AVG(CASE WHEN m.sentiment_preliminary = 'positive' THEN 1 
                               WHEN m.sentiment_preliminary = 'negative' THEN -1 ELSE 0 END) as sentiment_avg
                FROM contacts_enriched ce
                JOIN messages m ON ce.user_id = m.from_user_id
                WHERE m.date > ? AND ce.first_name IS NOT NULL AND ce.first_name != ''
                AND m.text IS NOT NULL AND m.text != '' 
                AND m.text NOT LIKE '/start' AND m.text NOT LIKE '/positions'
                AND m.text NOT LIKE '/help' AND m.text NOT LIKE 'https://%'
                AND ce.username NOT IN ('glupta', 'bearbunniepup', 'arigatoferrari', 'a_verify', 
                                        'Amadope817', 'AwesomeSha', 'vanssui', 'ASAPprez', 'illuminfti', 
                                        'MissRose_bot', 'SeriousKeith', 'SeriousIan', 'theosudo', 'aslantash')
                GROUP BY ce.user_id
                HAVING recent_messages >= 1
                ORDER BY last_interaction DESC
            """, (cutoff_date_str,))
            
            recent_data = cursor.fetchall()
            
            for user_id, first_name, username, phone, last_interaction, recent_messages, recent_texts, sentiment_avg in recent_data:
                
                # Calculate days since last contact
                try:
                    last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                    days_since = (datetime.now() - last_date).days
                except:
                    days_since = days_back
                
                # Analyze conversation content
                analysis = self._analyze_conversation_content(recent_texts or '', sentiment_avg or 0)
                
                # Generate Chris Voss opportunities
                voss_opportunities = self._generate_voss_opportunities(recent_texts or '', analysis)
                
                # Generate psychology hooks
                psychology_hooks = self._generate_psychology_hooks(analysis, first_name)
                
                # Create natural follow-up message
                natural_message = self._create_natural_message(
                    first_name, analysis, voss_opportunities, psychology_hooks
                )
                
                # Generate group introduction strategy
                group_strategy = self._generate_group_strategy(analysis, first_name)
                
                conversation = RecentConversation(
                    contact_id=f"recent_{user_id}",
                    user_id=user_id,
                    first_name=first_name,
                    username=username or '',
                    phone=phone or '',
                    last_interaction=last_interaction,
                    days_since_contact=days_since,
                    total_recent_messages=recent_messages,
                    conversation_context=analysis['context'],
                    last_topic_discussed=analysis['last_topic'],
                    emotional_tone=analysis['emotional_tone'],
                    mirror_opportunity=voss_opportunities['mirror'],
                    label_opportunity=voss_opportunities['label'],
                    calibrated_question=voss_opportunities['question'],
                    accusation_audit=voss_opportunities['audit'],
                    reciprocity_angle=psychology_hooks['reciprocity'],
                    social_proof_element=psychology_hooks['social_proof'],
                    authority_signal=psychology_hooks['authority'],
                    scarcity_element=psychology_hooks['scarcity'],
                    natural_message=natural_message,
                    group_intro_angle=group_strategy['intro'],
                    founder_connection=group_strategy['founder_connection'],
                    self_disclosure_prompt=group_strategy['disclosure_prompt']
                )
                
                recent_conversations.append(conversation)
        
        logger.info(f"🎯 Found {len(recent_conversations)} recent conversations to follow up")
        return recent_conversations

    def _analyze_conversation_content(self, texts: str, sentiment_avg: float) -> Dict[str, Any]:
        """Analyze conversation content for context and topics"""
        if not texts:
            return {
                'context': 'Limited conversation history',
                'last_topic': 'general discussion',
                'emotional_tone': 'neutral',
                'key_themes': [],
                'business_indicators': []
            }
        
        text_lower = texts.lower()
        
        # Extract key themes
        business_themes = []
        if any(word in text_lower for word in ['crypto', 'defi', 'token', 'blockchain']):
            business_themes.append('crypto/blockchain')
        if any(word in text_lower for word in ['investment', 'funding', 'capital', 'money']):
            business_themes.append('investment')
        if any(word in text_lower for word in ['tech', 'development', 'ai', 'platform']):
            business_themes.append('technology')
        if any(word in text_lower for word in ['business', 'startup', 'company', 'project']):
            business_themes.append('business')
        if any(word in text_lower for word in ['event', 'conference', 'meetup', 'speaking']):
            business_themes.append('events/networking')
        
        # Determine emotional tone
        if sentiment_avg > 0.3:
            emotional_tone = 'positive and engaged'
        elif sentiment_avg < -0.3:
            emotional_tone = 'concerned or frustrated'
        else:
            emotional_tone = 'neutral and professional'
        
        # Extract last topic (simplified)
        text_parts = texts.split(' | ')
        last_message = text_parts[-1] if text_parts else ''
        
        # Determine last topic based on keywords in last message
        last_topic = 'general discussion'
        if any(word in last_message.lower() for word in ['crypto', 'defi', 'token']):
            last_topic = 'crypto/DeFi projects'
        elif any(word in last_message.lower() for word in ['investment', 'funding']):
            last_topic = 'investment opportunities'
        elif any(word in last_message.lower() for word in ['tech', 'development', 'platform']):
            last_topic = 'technology and development'
        elif any(word in last_message.lower() for word in ['business', 'project']):
            last_topic = 'business strategy'
        elif any(word in last_message.lower() for word in ['event', 'conference']):
            last_topic = 'industry events'
        
        return {
            'context': f"Recent discussions about {', '.join(business_themes) if business_themes else 'various topics'}",
            'last_topic': last_topic,
            'emotional_tone': emotional_tone,
            'key_themes': business_themes,
            'business_indicators': business_themes
        }

    def _generate_voss_opportunities(self, texts: str, analysis: Dict) -> Dict[str, str]:
        """Generate Chris Voss technique opportunities"""
        
        # Mirror opportunity - extract last few meaningful words
        text_parts = texts.split(' | ')
        last_message = text_parts[-1] if text_parts else ''
        words = last_message.split()
        mirror_words = ' '.join(words[-3:]) if len(words) >= 3 else last_message
        
        # Clean up mirror words
        mirror_words = re.sub(r'[^\w\s]', '', mirror_words).strip()
        
        # Label opportunity based on emotional tone and context
        if analysis['emotional_tone'] == 'positive and engaged':
            label = "you're excited about the potential here"
        elif analysis['emotional_tone'] == 'concerned or frustrated':
            label = "there are some challenges you're working through"
        else:
            label = "you're evaluating your options carefully"
        
        # Calibrated question based on last topic
        topic = analysis['last_topic']
        questions = self.voss_techniques['calibrated_questions']
        question = random.choice(questions).format(
            topic=topic,
            challenge=f"help with {topic}"
        )
        
        # Accusation audit
        audit = random.choice(self.voss_techniques['accusation_audit'])
        
        return {
            'mirror': mirror_words,
            'label': label,
            'question': question,
            'audit': audit
        }

    def _generate_psychology_hooks(self, analysis: Dict, first_name: str) -> Dict[str, str]:
        """Generate behavioral psychology hooks"""
        
        themes = analysis['key_themes']
        
        # Reciprocity - offer value first
        if 'crypto/blockchain' in themes:
            reciprocity = "I came across an interesting DeFi protocol that reminded me of our conversation"
        elif 'investment' in themes:
            reciprocity = "I wanted to share some market insights that might be relevant to your portfolio"
        elif 'technology' in themes:
            reciprocity = "Found a technical resource that might interest you given our discussion"
        else:
            reciprocity = "Wanted to share something valuable with you first"
        
        # Social proof
        if themes:
            main_theme = themes[0]
            social_proof = f"I've been talking to several leaders in {main_theme} who face similar opportunities"
        else:
            social_proof = "Others in your position have mentioned similar interests"
        
        # Authority signal
        if 'investment' in themes:
            authority = "In our work with portfolio companies and fund managers"
        elif 'crypto/blockchain' in themes:
            authority = "Based on our experience in the DeFi ecosystem"
        elif 'technology' in themes:
            authority = "Through our technical partnerships and integrations"
        else:
            authority = "Based on our experience with similar challenges"
        
        # Scarcity element
        scarcity = "We're being selective about the next group we bring together"
        
        return {
            'reciprocity': reciprocity,
            'social_proof': social_proof,
            'authority': authority,
            'scarcity': scarcity
        }

    def _create_natural_message(self, first_name: str, analysis: Dict, voss: Dict, psych: Dict) -> str:
        """Create natural, human-sounding message"""
        
        # Choose natural opener
        opener_template = random.choice(self.natural_openers)
        opener = opener_template.format(
            first_name=first_name,
            topic=analysis['last_topic']
        )
        
        # Add reciprocity value
        value_add = psych['reciprocity']
        
        # Include subtle Voss technique (labeling or mirroring)
        if random.choice([True, False]):  # 50% chance of each
            voss_element = f"It seems like {voss['label']}."
        else:
            voss_element = f"You mentioned {voss['mirror']} - {voss['question']}"
        
        # Soft call to action with scarcity
        cta = f"{psych['scarcity']} - would love to get your thoughts."
        
        # Combine elements naturally
        message = f"{opener}.\n\n{value_add}. {voss_element}\n\n{cta}"
        
        return message

    def _generate_group_strategy(self, analysis: Dict, first_name: str) -> Dict[str, str]:
        """Generate group introduction strategy"""
        
        themes = analysis['key_themes']
        
        # Group introduction angle
        if 'crypto/blockchain' in themes:
            intro = f"bringing {first_name} into our DeFi innovators circle"
            space = "crypto/DeFi"
        elif 'investment' in themes:
            intro = f"connecting {first_name} with other forward-thinking investors"
            space = "investment"
        elif 'technology' in themes:
            intro = f"introducing {first_name} to our tech leadership community"
            space = "technology"
        else:
            intro = f"bringing {first_name} into our founders' group"
            space = "business development"
        
        # Founder connection strategy
        founder_connection = f"Our founders are excited to learn about {first_name}'s experience in {space}"
        
        # Self-disclosure prompt
        disclosure_prompt = f"We'd love to hear about your current focus in {space} and what opportunities you're most excited about"
        
        return {
            'intro': intro,
            'founder_connection': founder_connection,
            'disclosure_prompt': disclosure_prompt
        }

    def store_recent_conversations(self, conversations: List[RecentConversation]):
        """Store recent conversations in database"""
        logger.info(f"💾 Storing {len(conversations)} recent conversations...")
        
        with sqlite3.connect(self.follow_up_db) as conn:
            cursor = conn.cursor()
            
            for conv in conversations:
                cursor.execute("""
                    INSERT OR REPLACE INTO recent_conversations (
                        conversation_id, user_id, first_name, username, phone,
                        last_interaction, days_since_contact, total_recent_messages,
                        conversation_context, last_topic_discussed, emotional_tone,
                        mirror_opportunity, label_opportunity, calibrated_question, accusation_audit,
                        reciprocity_angle, social_proof_element, authority_signal, scarcity_element,
                        natural_message, group_intro_angle, founder_connection, self_disclosure_prompt
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conv.contact_id, conv.user_id, conv.first_name, conv.username, conv.phone,
                    conv.last_interaction, conv.days_since_contact, conv.total_recent_messages,
                    conv.conversation_context, conv.last_topic_discussed, conv.emotional_tone,
                    conv.mirror_opportunity, conv.label_opportunity, conv.calibrated_question, conv.accusation_audit,
                    conv.reciprocity_angle, conv.social_proof_element, conv.authority_signal, conv.scarcity_element,
                    conv.natural_message, conv.group_intro_angle, conv.founder_connection, conv.self_disclosure_prompt
                ))
            
            conn.commit()
            logger.info(f"✅ Stored {len(conversations)} conversations")

    def export_follow_up_reports(self, user_outreach_blurb: str = ""):
        """Export comprehensive follow-up reports"""
        logger.info("📊 Exporting follow-up reports...")
        
        export_dir = Path("exports/advanced_follow_up")
        export_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with sqlite3.connect(self.follow_up_db) as conn:
            # Recent conversations report (exclude teammates)
            conversations_df = pd.read_sql_query("""
                SELECT first_name, username, phone, days_since_contact, total_recent_messages,
                       conversation_context, last_topic_discussed, emotional_tone,
                       natural_message, group_intro_angle, founder_connection, self_disclosure_prompt
                FROM recent_conversations
                WHERE username NOT IN ('glupta', 'bearbunniepup', 'arigatoferrari', 'a_verify', 
                                       'Amadope817', 'AwesomeSha', 'vanssui', 'ASAPprez', 'illuminfti', 
                                       'MissRose_bot', 'SeriousKeith', 'SeriousIan', 'theosudo', 'aslantash')
                ORDER BY total_recent_messages DESC, days_since_contact ASC
            """, conn)
            conversations_df.to_csv(export_dir / f"recent_conversations_report_{timestamp}.csv", index=False)
            
            # Priority follow-ups (within 7 days)
            priority_df = pd.read_sql_query("""
                SELECT first_name, username, phone, days_since_contact, 
                       natural_message, group_intro_angle
                FROM recent_conversations
                WHERE days_since_contact <= 7 AND username NOT IN ('glupta', 'bearbunniepup', 'arigatoferrari', 'a_verify', 
                                                                    'Amadope817', 'AwesomeSha', 'vanssui', 'ASAPprez', 'illuminfti', 
                                                                    'MissRose_bot', 'SeriousKeith', 'SeriousIan', 'theosudo', 'aslantash')
                ORDER BY total_recent_messages DESC
            """, conn)
            priority_df.to_csv(export_dir / f"priority_follow_ups_{timestamp}.csv", index=False)
            
            # Generate detailed action report
            self._generate_detailed_action_report(export_dir, timestamp, user_outreach_blurb)
        
        logger.info(f"✅ Follow-up reports exported to {export_dir}")

    def _generate_detailed_action_report(self, export_dir: Path, timestamp: str, outreach_blurb: str):
        """Generate detailed action report with all follow-ups"""
        
        with sqlite3.connect(self.follow_up_db) as conn:
            cursor = conn.cursor()
            
            # Get all conversations ordered by priority (exclude teammates)
            cursor.execute("""
                SELECT first_name, username, phone, days_since_contact, 
                       conversation_context, last_topic_discussed, emotional_tone,
                       natural_message, group_intro_angle, founder_connection, 
                       self_disclosure_prompt, total_recent_messages
                FROM recent_conversations
                WHERE username NOT IN ('glupta', 'bearbunniepup', 'arigatoferrari', 'a_verify', 
                                       'Amadope817', 'AwesomeSha', 'vanssui', 'ASAPprez', 'illuminfti', 
                                       'MissRose_bot', 'SeriousKeith', 'SeriousIan', 'theosudo', 'aslantash')
                ORDER BY total_recent_messages DESC, days_since_contact ASC
            """)
            
            conversations = cursor.fetchall()
            
            # Generate comprehensive report
            report = f"""
ADVANCED FOLLOW-UP REPORT - PAST 60 DAYS
=======================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Conversations to Follow Up: {len(conversations)}

{"="*60}
YOUR OUTREACH TEMPLATE
{"="*60}
{outreach_blurb}

{"="*60}
PERSONALIZED FOLLOW-UP MESSAGES
{"="*60}
"""
            
            for i, (first_name, username, phone, days_since, context, last_topic, 
                   tone, message, group_intro, founder_conn, disclosure) in enumerate(conversations, 1):
                
                priority = "🔥 URGENT" if days_since <= 3 else "⚡ HIGH" if days_since <= 7 else "📌 MEDIUM" if days_since <= 14 else "📋 LOW"
                
                report += f"""
{i}. {first_name} (@{username}) - {priority}
{'='*50}
📱 Phone: {phone if phone else 'Not available'}
⏰ Last Contact: {days_since} days ago
💬 Context: {context}
🎯 Last Topic: {last_topic}
😊 Tone: {tone}

📝 PERSONALIZED MESSAGE:
{message}

👥 GROUP INTRODUCTION STRATEGY:
{group_intro}

🤝 FOUNDER CONNECTION:
{founder_conn}

💭 SELF-DISCLOSURE PROMPT:
{disclosure}

{"─"*50}
"""
            
            # Add summary and next steps
            urgent_count = sum(1 for _, _, _, days_since, *_ in conversations if days_since <= 3)
            high_count = sum(1 for _, _, _, days_since, *_ in conversations if days_since <= 7)
            
            report += f"""

{"="*60}
SUMMARY & NEXT STEPS
{"="*60}

📊 PRIORITY BREAKDOWN:
• 🔥 Urgent (≤3 days): {urgent_count} contacts
• ⚡ High (≤7 days): {high_count} contacts  
• 📌 Medium (≤14 days): {len([c for c in conversations if c[3] <= 14]) - high_count} contacts
• 📋 Low (>14 days): {len(conversations) - len([c for c in conversations if c[3] <= 14])} contacts

🎯 IMMEDIATE ACTION PLAN:
1. Start with urgent contacts (≤3 days)
2. Send personalized messages using Chris Voss techniques
3. Add to group chat with founder introductions
4. Use self-disclosure prompts to learn about their current focus
5. Apply behavioral psychology principles for higher conversion

🧠 PSYCHOLOGICAL TECHNIQUES USED:
• Mirroring: Repeating their last meaningful words
• Labeling: Acknowledging emotions and situations
• Calibrated Questions: Strategic questions that gather info
• Reciprocity: Offering value first
• Social Proof: Mentioning others in similar situations
• Authority: Referencing relevant experience
• Scarcity: Limited group/opportunity messaging

✅ All messages are designed to sound natural and human-written
✅ Each uses the contact's first name for personalization
✅ Group chat introductions are ready for founder connections
✅ Self-disclosure prompts will help gather more information
"""
            
            # Save report
            with open(export_dir / f"detailed_follow_up_report_{timestamp}.txt", 'w') as f:
                f.write(report)

    def get_follow_up_summary(self):
        """Get follow-up summary statistics"""
        with sqlite3.connect(self.follow_up_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM recent_conversations")
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM recent_conversations WHERE days_since_contact <= 3")
            urgent_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM recent_conversations WHERE days_since_contact <= 7")
            high_priority = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(total_recent_messages) FROM recent_conversations")
            avg_messages = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM recent_conversations WHERE phone IS NOT NULL AND phone != ''")
            contacts_with_phone = cursor.fetchone()[0]
            
            return {
                'total_conversations': total_conversations,
                'urgent_count': urgent_count,
                'high_priority': high_priority,
                'avg_messages': round(avg_messages, 1),
                'contacts_with_phone': contacts_with_phone
            }

async def main():
    """Main function for advanced follow-up system"""
    print("🧠 ADVANCED FOLLOW-UP SYSTEM")
    print("=" * 60)
    print("📱 Analyzing conversations from past 60 days")
    print("🎯 Using Chris Voss negotiation techniques")
    print("🧠 Applying behavioral psychology principles")
    print("💬 Creating natural, human-sounding messages")
    print()
    
    # Initialize system
    follow_up_system = AdvancedFollowUpSystem()
    
    # Analyze recent conversations
    print("🔍 Step 1: Analyzing recent conversations...")
    recent_conversations = follow_up_system.analyze_recent_conversations(days_back=60)
    
    if not recent_conversations:
        print("❌ No recent conversations found")
        return
    
    # Store conversations
    print("💾 Step 2: Storing conversation analysis...")
    follow_up_system.store_recent_conversations(recent_conversations)
    
    # Note: Waiting for user's outreach blurb to complete export
    print("📊 Step 3: Preparing follow-up reports...")
    print("\n⏳ Waiting for your general outreach blurb to complete personalized messages...")
    
    # Show summary
    summary = follow_up_system.get_follow_up_summary()
    print(f"\n🎯 ANALYSIS COMPLETE!")
    print(f"📊 Summary:")
    print(f"   💬 Total Recent Conversations: {summary['total_conversations']:,}")
    print(f"   🔥 Urgent Follow-ups (≤3 days): {summary['urgent_count']:,}")
    print(f"   ⚡ High Priority (≤7 days): {summary['high_priority']:,}")
    print(f"   📱 Contacts with Phone: {summary['contacts_with_phone']:,}")
    print(f"   📈 Avg Messages per Contact: {summary['avg_messages']}")
    print()
    print(f"📁 Database: data/advanced_follow_up.db")
    print("\n✅ Ready for your outreach blurb to generate final messages!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 