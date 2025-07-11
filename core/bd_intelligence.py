#!/usr/bin/env python3
"""
BD Intelligence System
=====================
Advanced business development intelligence using ChatGPT API for:
- Conversation analysis and sentiment tracking
- Natural BD strategy recommendations
- Meeting booking optimization
- Deal closing techniques
- KPI tracking and insights
"""

import asyncio
import logging
import json
import openai
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
from enum import Enum
import re

logger = logging.getLogger(__name__)

class BDStage(Enum):
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"

class ConversationTone(Enum):
    COLD = "cold"
    NEUTRAL = "neutral"
    WARM = "warm"
    HOT = "hot"
    HOSTILE = "hostile"

class NextAction(Enum):
    FOLLOW_UP = "follow_up"
    SEND_INFO = "send_info"
    SCHEDULE_CALL = "schedule_call"
    SEND_PROPOSAL = "send_proposal"
    CLOSE_DEAL = "close_deal"
    NURTURE = "nurture"
    QUALIFICATION = "qualification"

@dataclass
class ConversationInsight:
    conversation_id: str
    contact_name: str
    bd_stage: str
    sentiment_score: float  # -1 to 1
    interest_level: int  # 0-100
    pain_points: List[str]
    objections: List[str]
    buying_signals: List[str]
    next_best_action: str
    recommended_message: str
    urgency_score: int  # 0-100
    meeting_readiness: int  # 0-100
    key_topics: List[str]
    conversation_summary: str
    bd_opportunities: List[str]
    timestamp: str

@dataclass
class BDKPIs:
    date: str
    total_conversations: int
    new_leads: int
    qualified_leads: int
    meetings_booked: int
    deals_closed: int
    pipeline_value: float
    conversion_rate: float
    response_rate: float
    avg_sentiment: float
    top_pain_points: List[str]
    successful_techniques: List[str]
    areas_for_improvement: List[str]

class BDIntelligence:
    """Advanced BD Intelligence using ChatGPT API"""
    
    def __init__(self, openai_api_key: str, lead_db=None):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.lead_db = lead_db
        self.bd_context = self._load_bd_context()
        self.conversation_cache = {}
        logger.info("🧠 BD Intelligence System initialized")
    
    def _load_bd_context(self) -> Dict[str, Any]:
        """Load business development context and strategies"""
        return {
            "company_stage": "Pre-Series A startup raising $1.6M at $20M valuation, launching at $25M",
            "target_market": "DeFi, Web3, Crypto protocols and infrastructure",
            "value_proposition": "Next-generation blockchain infrastructure solution",
            "pain_points_we_solve": [
                "Scalability issues in current blockchain networks",
                "High transaction costs and slow settlement times",
                "Complex integration with existing DeFi protocols",
                "Lack of institutional-grade security and compliance"
            ],
            "ideal_customers": [
                "DeFi protocols looking to scale",
                "Crypto exchanges needing infrastructure",
                "Institutional investors seeking Web3 exposure",
                "Enterprise clients adopting blockchain"
            ],
            "competitive_advantages": [
                "30x faster transaction processing",
                "90% lower costs than existing solutions",
                "Seamless integration with major protocols",
                "Enterprise-grade security and compliance"
            ],
            "current_traction": [
                "Processing $10M+ in monthly volume",
                "Partnerships with 3 major DeFi protocols", 
                "25+ enterprise clients in pipeline",
                "Growing 40% month-over-month"
            ]
        }
    
    async def analyze_conversation(self, messages: List[Dict], contact_info: Dict = None) -> ConversationInsight:
        """Analyze conversation for BD insights and recommendations"""
        try:
            if not messages:
                return None
            
            # Prepare conversation text
            conversation_text = self._format_conversation(messages)
            contact_name = self._extract_contact_name(contact_info, messages)
            
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(conversation_text, contact_name, contact_info)
            
            # Get ChatGPT analysis
            response = await self._call_chatgpt(prompt, max_tokens=1500)
            
            if not response:
                return None
            
            # Parse structured response
            insight = self._parse_analysis_response(response, contact_name, conversation_text)
            
            # Store in cache
            conversation_id = f"{contact_name}_{datetime.now().strftime('%Y%m%d')}"
            self.conversation_cache[conversation_id] = insight
            
            logger.info(f"🧠 Analyzed conversation with {contact_name}: {insight.bd_stage} stage, {insight.interest_level}% interest")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Error analyzing conversation: {e}")
            return None
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format messages into readable conversation"""
        conversation = []
        for msg in messages[-20:]:  # Last 20 messages for context
            sender = "You" if msg.get('is_outbound') else msg.get('first_name', 'Contact')
            text = msg.get('message_text', '').strip()
            timestamp = msg.get('timestamp', '')[:10]  # Date only
            
            if text:
                conversation.append(f"[{timestamp}] {sender}: {text}")
        
        return "\n".join(conversation)
    
    def _extract_contact_name(self, contact_info: Dict, messages: List[Dict]) -> str:
        """Extract contact name from available data"""
        if contact_info:
            name = f"{contact_info.get('first_name', '')} {contact_info.get('last_name', '')}".strip()
            if name:
                return name
            return contact_info.get('username', 'Unknown Contact')
        
        # Fallback to message data
        for msg in messages:
            if not msg.get('is_outbound'):
                name = f"{msg.get('first_name', '')} {msg.get('last_name', '')}".strip()
                if name:
                    return name
                return msg.get('username', 'Unknown Contact')
        
        return "Unknown Contact"
    
    def _build_analysis_prompt(self, conversation: str, contact_name: str, contact_info: Dict = None) -> str:
        """Build comprehensive analysis prompt for ChatGPT"""
        
        org_context = ""
        if contact_info and contact_info.get('organization_name'):
            org_context = f"Contact works at: {contact_info['organization_name']}"
            if contact_info.get('organization_type'):
                org_context += f" ({contact_info['organization_type']})"
        
        prompt = f"""
You are an expert business development analyst specializing in Web3/DeFi sales and relationship building. 

BUSINESS CONTEXT:
{json.dumps(self.bd_context, indent=2)}

CONVERSATION TO ANALYZE:
Contact: {contact_name}
{org_context}

Conversation History:
{conversation}

ANALYSIS REQUEST:
Analyze this conversation for business development insights. Provide a comprehensive analysis in JSON format with these exact fields:

{{
    "bd_stage": "awareness|interest|consideration|intent|evaluation|purchase",
    "sentiment_score": -1.0 to 1.0,
    "interest_level": 0-100,
    "pain_points": ["specific pain point 1", "pain point 2"],
    "objections": ["objection 1", "objection 2"],
    "buying_signals": ["signal 1", "signal 2"],
    "next_best_action": "follow_up|send_info|schedule_call|send_proposal|close_deal|nurture|qualification",
    "recommended_message": "Natural, personalized message recommendation (2-3 sentences max)",
    "urgency_score": 0-100,
    "meeting_readiness": 0-100,
    "key_topics": ["topic 1", "topic 2"],
    "conversation_summary": "Brief summary of conversation progression",
    "bd_opportunities": ["opportunity 1", "opportunity 2"]
}}

ANALYSIS GUIDELINES:
- Focus on natural, consultative sales approach
- Identify genuine pain points and business needs
- Recommend personalized, value-driven next steps
- Avoid pushy or robotic language
- Consider the fundraising context ($1.6M raise, $20M valuation)
- Look for partnership, investment, and customer opportunities
- Rate urgency based on time-sensitive language and buying signals
- Assess meeting readiness based on engagement level and expressed interest

Respond ONLY with valid JSON, no additional text.
"""
        return prompt
    
    async def _call_chatgpt(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call ChatGPT API with error handling"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business development analyst. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ ChatGPT API error: {e}")
            return None
    
    def _parse_analysis_response(self, response: str, contact_name: str, conversation_text: str) -> ConversationInsight:
        """Parse ChatGPT response into ConversationInsight"""
        try:
            # Clean response and parse JSON
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:-3]
            
            data = json.loads(cleaned_response)
            
            return ConversationInsight(
                conversation_id=f"{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                contact_name=contact_name,
                bd_stage=data.get('bd_stage', 'awareness'),
                sentiment_score=float(data.get('sentiment_score', 0)),
                interest_level=int(data.get('interest_level', 0)),
                pain_points=data.get('pain_points', []),
                objections=data.get('objections', []),
                buying_signals=data.get('buying_signals', []),
                next_best_action=data.get('next_best_action', 'follow_up'),
                recommended_message=data.get('recommended_message', ''),
                urgency_score=int(data.get('urgency_score', 0)),
                meeting_readiness=int(data.get('meeting_readiness', 0)),
                key_topics=data.get('key_topics', []),
                conversation_summary=data.get('conversation_summary', ''),
                bd_opportunities=data.get('bd_opportunities', []),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing analysis response: {e}")
            # Return fallback insight
            return ConversationInsight(
                conversation_id=f"{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                contact_name=contact_name,
                bd_stage="awareness",
                sentiment_score=0.0,
                interest_level=50,
                pain_points=[],
                objections=[],
                buying_signals=[],
                next_best_action="follow_up",
                recommended_message="Thanks for the conversation! Would love to continue our discussion.",
                urgency_score=25,
                meeting_readiness=25,
                key_topics=[],
                conversation_summary="Conversation analysis failed",
                bd_opportunities=[],
                timestamp=datetime.now().isoformat()
            )
    
    async def generate_personalized_message(self, insight: ConversationInsight, message_type: str = "follow_up") -> str:
        """Generate natural, personalized BD message"""
        try:
            prompt = f"""
You are an expert business development professional specializing in Web3/DeFi. Generate a natural, personalized message.

BUSINESS CONTEXT:
{json.dumps(self.bd_context, indent=2)}

CONVERSATION INSIGHT:
Contact: {insight.contact_name}
BD Stage: {insight.bd_stage}
Interest Level: {insight.interest_level}%
Pain Points: {', '.join(insight.pain_points)}
Key Topics: {', '.join(insight.key_topics)}
Buying Signals: {', '.join(insight.buying_signals)}
Conversation Summary: {insight.conversation_summary}

MESSAGE TYPE: {message_type}

REQUIREMENTS:
- Natural, conversational tone (not robotic)
- Personalized based on conversation context
- Value-focused, not pushy
- 2-3 sentences maximum
- Include subtle call-to-action if appropriate
- Reference specific pain points or interests mentioned
- Professional but approachable

Generate a message that feels genuine and continues the relationship naturally.
"""
            
            response = await self._call_chatgpt(prompt, max_tokens=200)
            
            if response:
                # Clean up the response
                message = response.strip().strip('"').strip("'")
                return message
            else:
                return insight.recommended_message
                
        except Exception as e:
            logger.error(f"❌ Error generating personalized message: {e}")
            return insight.recommended_message
    
    async def analyze_bd_performance(self, days: int = 7) -> BDKPIs:
        """Analyze BD performance and KPIs"""
        try:
            if not self.lead_db:
                logger.warning("No lead database available for KPI analysis")
                return None
            
            # Get recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # This would integrate with your lead database
            # For now, return sample KPIs structure
            return BDKPIs(
                date=datetime.now().strftime('%Y-%m-%d'),
                total_conversations=len(self.conversation_cache),
                new_leads=0,  # Would calculate from lead_db
                qualified_leads=0,
                meetings_booked=0,
                deals_closed=0,
                pipeline_value=0.0,
                conversion_rate=0.0,
                response_rate=0.0,
                avg_sentiment=0.0,
                top_pain_points=[],
                successful_techniques=[],
                areas_for_improvement=[]
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing BD performance: {e}")
            return None
    
    async def get_daily_bd_brief(self) -> Dict[str, Any]:
        """Generate daily BD briefing with actionable insights"""
        try:
            # Analyze recent conversations
            hot_conversations = []
            follow_up_needed = []
            
            for conv_id, insight in self.conversation_cache.items():
                if insight.urgency_score > 70:
                    hot_conversations.append(insight)
                elif insight.next_best_action in ['follow_up', 'schedule_call']:
                    follow_up_needed.append(insight)
            
            # Generate recommendations using ChatGPT
            brief_prompt = f"""
Based on recent BD conversations, generate a daily briefing with strategic recommendations.

BUSINESS CONTEXT:
{json.dumps(self.bd_context, indent=2)}

HIGH-PRIORITY CONVERSATIONS:
{json.dumps([asdict(conv) for conv in hot_conversations[:5]], indent=2)}

ANALYSIS REQUEST:
Generate a daily BD briefing in JSON format:

{{
    "priority_actions": ["action 1", "action 2", "action 3"],
    "hot_opportunities": ["opportunity 1", "opportunity 2"],
    "follow_up_recommendations": ["recommendation 1", "recommendation 2"],
    "market_insights": ["insight 1", "insight 2"],
    "strategic_focus": "What to focus on today",
    "success_metrics": ["metric 1", "metric 2"],
    "improvement_areas": ["area 1", "area 2"]
}}

Focus on actionable insights for a startup raising $1.6M.
"""
            
            response = await self._call_chatgpt(brief_prompt, max_tokens=800)
            
            if response:
                try:
                    brief_data = json.loads(response.strip())
                    brief_data['total_conversations'] = len(self.conversation_cache)
                    brief_data['hot_conversations'] = len(hot_conversations)
                    brief_data['follow_ups_needed'] = len(follow_up_needed)
                    brief_data['timestamp'] = datetime.now().isoformat()
                    return brief_data
                except json.JSONDecodeError:
                    pass
            
            # Fallback briefing
            return {
                "priority_actions": ["Review hot leads", "Send follow-up messages", "Update pipeline"],
                "hot_opportunities": [f"{conv.contact_name} - {conv.bd_stage}" for conv in hot_conversations[:3]],
                "follow_up_recommendations": ["Focus on warm leads", "Schedule calls with high-interest contacts"],
                "market_insights": ["DeFi market showing strong interest", "Infrastructure solutions in demand"],
                "strategic_focus": "Convert warm leads to meetings and advance pipeline",
                "success_metrics": ["Response rate", "Meeting bookings", "Pipeline progression"],
                "improvement_areas": ["Personalization", "Value demonstration"],
                "total_conversations": len(self.conversation_cache),
                "hot_conversations": len(hot_conversations),
                "follow_ups_needed": len(follow_up_needed),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating daily brief: {e}")
            return {}
    
    def get_conversation_insights(self, contact_name: str = None) -> List[ConversationInsight]:
        """Get conversation insights for specific contact or all"""
        if contact_name:
            return [insight for insight in self.conversation_cache.values() 
                   if contact_name.lower() in insight.contact_name.lower()]
        return list(self.conversation_cache.values())
    
    def export_bd_intelligence(self) -> Dict[str, Any]:
        """Export all BD intelligence data"""
        return {
            "conversations": [asdict(insight) for insight in self.conversation_cache.values()],
            "bd_context": self.bd_context,
            "export_timestamp": datetime.now().isoformat(),
            "total_analyzed": len(self.conversation_cache)
        }


class BDMessageGenerator:
    """Generate natural BD messages for different scenarios"""
    
    def __init__(self, bd_intelligence: BDIntelligence):
        self.bd_intel = bd_intelligence
    
    async def generate_follow_up(self, insight: ConversationInsight) -> str:
        """Generate natural follow-up message"""
        return await self.bd_intel.generate_personalized_message(insight, "follow_up")
    
    async def generate_meeting_request(self, insight: ConversationInsight) -> str:
        """Generate natural meeting booking message"""
        return await self.bd_intel.generate_personalized_message(insight, "meeting_request")
    
    async def generate_value_prop(self, insight: ConversationInsight) -> str:
        """Generate value proposition message"""
        return await self.bd_intel.generate_personalized_message(insight, "value_proposition")
    
    async def generate_objection_response(self, insight: ConversationInsight) -> str:
        """Generate natural objection handling response"""
        return await self.bd_intel.generate_personalized_message(insight, "objection_response")


# Utility functions
def extract_meeting_signals(text: str) -> List[str]:
    """Extract meeting-related signals from text"""
    meeting_patterns = [
        r"(?i)\b(call|meeting|chat|discuss|talk|demo|presentation)\b",
        r"(?i)\b(schedule|book|arrange|set up|plan)\b",
        r"(?i)\b(available|free|time|calendar|when)\b",
        r"(?i)\b(next week|tomorrow|this week|soon)\b"
    ]
    
    signals = []
    for pattern in meeting_patterns:
        if re.search(pattern, text):
            signals.append(pattern.split('|')[1].strip('()'))
    
    return signals

def extract_pain_points(text: str) -> List[str]:
    """Extract pain points from conversation text"""
    pain_patterns = [
        r"(?i)\b(problem|issue|challenge|difficulty|struggle|pain|frustrat)\w*",
        r"(?i)\b(slow|expensive|complex|difficult|hard|inefficient)\b",
        r"(?i)\b(need|want|looking for|seeking|require)\b"
    ]
    
    pain_points = []
    for pattern in pain_patterns:
        matches = re.findall(pattern, text)
        pain_points.extend(matches)
    
    return list(set(pain_points))

def calculate_urgency_score(text: str, buying_signals: List[str]) -> int:
    """Calculate urgency score based on text analysis"""
    urgency_keywords = ['urgent', 'asap', 'quickly', 'soon', 'deadline', 'timeline', 'immediately']
    time_keywords = ['this week', 'next week', 'by friday', 'end of month']
    
    score = 0
    text_lower = text.lower()
    
    # Check urgency keywords
    for keyword in urgency_keywords:
        if keyword in text_lower:
            score += 20
    
    # Check time-sensitive keywords
    for keyword in time_keywords:
        if keyword in text_lower:
            score += 15
    
    # Buying signals boost urgency
    score += len(buying_signals) * 10
    
    return min(score, 100) 