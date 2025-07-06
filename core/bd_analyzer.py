#!/usr/bin/env python3
"""
Business Development AI Analyzer
================================
Advanced ChatGPT-powered analysis for investor relations, LP engagement, and community building.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class ContactType(Enum):
    INVESTOR = "investor"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    COMMUNITY = "community"
    PARTNER = "partner"
    UNKNOWN = "unknown"

class EngagementLevel(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    UNRESPONSIVE = "unresponsive"

@dataclass
class ContactRating:
    contact_id: str
    contact_name: str
    contact_type: ContactType
    engagement_level: EngagementLevel
    investment_potential: float  # 0-10 scale
    response_rate: float  # 0-1 scale
    last_interaction: datetime
    total_messages: int
    sentiment_score: float  # -1 to 1
    key_interests: List[str]
    follow_up_priority: int  # 1-5 scale
    notes: str

@dataclass
class FollowUpRecommendation:
    contact_id: str
    contact_name: str
    priority: int
    recommended_action: str
    suggested_message: str
    timing: str
    reasoning: str
    context_summary: str

@dataclass
class DailyBriefing:
    date: datetime
    total_contacts: int
    hot_leads: List[ContactRating]
    follow_ups_needed: List[FollowUpRecommendation]
    new_opportunities: List[str]
    market_insights: List[str]
    action_items: List[str]
    performance_metrics: Dict[str, Any]

class BusinessDevelopmentAnalyzer:
    """Advanced AI analyzer for business development activities"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.client = None
        self.project_context = self._load_project_context()
        self._initialize_openai()
        
        logger.info("✅ Business Development Analyzer initialized")
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("⚠️ OpenAI API key not found")
            return
        
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info("✅ OpenAI client initialized")
    
    def _load_project_context(self) -> str:
        """Load project context for AI analysis"""
        return """
        PROJECT CONTEXT:
        We are building a DeFi protocol focused on liquidity provision and yield farming.
        
        TARGET AUDIENCES:
        1. INVESTORS: VCs, angels, institutional investors looking for DeFi opportunities
        2. LIQUIDITY PROVIDERS: Individuals/institutions wanting to provide liquidity for yields
        3. COMMUNITIES: DeFi communities, DAOs, crypto communities interested in partnerships
        
        GOALS:
        - Raise investment funding for protocol development
        - Attract liquidity providers to our LP program
        - Build community partnerships and integrations
        - Generate awareness and adoption
        
        KEY METRICS:
        - Total Value Locked (TVL)
        - Number of liquidity providers
        - Investment commitments
        - Community partnerships
        - User adoption and engagement
        """
    
    async def analyze_contact(self, chat_id: str, messages: List[Dict]) -> ContactRating:
        """Analyze a single contact for business development potential"""
        if not self.client or not messages:
            return self._create_default_rating(chat_id, "Unknown", messages)
        
        try:
            # Prepare conversation context
            conversation = self._format_conversation(messages)
            
            prompt = f"""
            {self.project_context}
            
            ANALYZE THIS TELEGRAM CONVERSATION:
            {conversation}
            
            Provide a comprehensive business development analysis in JSON format:
            {{
                "contact_type": "investor|liquidity_provider|community|partner|unknown",
                "engagement_level": "hot|warm|cold|unresponsive",
                "investment_potential": 0-10,
                "sentiment_score": -1 to 1,
                "key_interests": ["list", "of", "interests"],
                "follow_up_priority": 1-5,
                "analysis_notes": "detailed analysis",
                "recommended_next_steps": "specific recommendations"
            }}
            
            Focus on:
            - Investment interest and capacity
            - Liquidity provision potential
            - Community partnership opportunities
            - Engagement quality and responsiveness
            - Technical understanding of DeFi
            - Network and influence level
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business development analyst specializing in DeFi and crypto investments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return ContactRating(
                contact_id=chat_id,
                contact_name=messages[0].get('chat_title', 'Unknown'),
                contact_type=ContactType(analysis.get('contact_type', 'unknown')),
                engagement_level=EngagementLevel(analysis.get('engagement_level', 'cold')),
                investment_potential=analysis.get('investment_potential', 0),
                response_rate=self._calculate_response_rate(messages),
                last_interaction=datetime.fromisoformat(messages[-1]['timestamp']),
                total_messages=len(messages),
                sentiment_score=analysis.get('sentiment_score', 0),
                key_interests=analysis.get('key_interests', []),
                follow_up_priority=analysis.get('follow_up_priority', 3),
                notes=analysis.get('analysis_notes', '')
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing contact {chat_id}: {e}")
            return self._create_default_rating(chat_id, messages[0].get('chat_title', 'Unknown'), messages)
    
    async def generate_follow_up_recommendations(self, contact_rating: ContactRating, messages: List[Dict]) -> FollowUpRecommendation:
        """Generate specific follow-up recommendations for a contact"""
        if not self.client:
            return self._create_default_recommendation(contact_rating)
        
        try:
            conversation = self._format_conversation(messages[-10:])  # Last 10 messages for context
            
            prompt = f"""
            {self.project_context}
            
            CONTACT PROFILE:
            - Name: {contact_rating.contact_name}
            - Type: {contact_rating.contact_type.value}
            - Engagement: {contact_rating.engagement_level.value}
            - Investment Potential: {contact_rating.investment_potential}/10
            - Key Interests: {', '.join(contact_rating.key_interests)}
            - Last Interaction: {contact_rating.last_interaction}
            
            RECENT CONVERSATION:
            {conversation}
            
            Generate a specific follow-up recommendation in JSON format:
            {{
                "priority": 1-5,
                "recommended_action": "specific action to take",
                "suggested_message": "exact message to send",
                "timing": "when to send (e.g., 'immediately', 'in 2 days', 'next week')",
                "reasoning": "why this approach",
                "context_summary": "key context from conversation"
            }}
            
            Tailor the message for:
            - Their specific interests and concerns
            - Their level of technical understanding
            - Their potential role (investor/LP/community)
            - The conversation history and tone
            - Current market conditions and opportunities
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business development expert creating personalized outreach for DeFi projects."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            recommendation = json.loads(response.choices[0].message.content)
            
            return FollowUpRecommendation(
                contact_id=contact_rating.contact_id,
                contact_name=contact_rating.contact_name,
                priority=recommendation.get('priority', 3),
                recommended_action=recommendation.get('recommended_action', ''),
                suggested_message=recommendation.get('suggested_message', ''),
                timing=recommendation.get('timing', 'within a week'),
                reasoning=recommendation.get('reasoning', ''),
                context_summary=recommendation.get('context_summary', '')
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendation for {contact_rating.contact_id}: {e}")
            return self._create_default_recommendation(contact_rating)
    
    async def generate_daily_briefing(self, contact_ratings: List[ContactRating], follow_ups: List[FollowUpRecommendation]) -> DailyBriefing:
        """Generate comprehensive daily briefing"""
        if not self.client:
            return self._create_default_briefing(contact_ratings, follow_ups)
        
        try:
            # Prepare summary data
            hot_leads = [c for c in contact_ratings if c.engagement_level == EngagementLevel.HOT]
            high_priority_followups = [f for f in follow_ups if f.priority >= 4]
            
            summary_data = {
                "total_contacts": len(contact_ratings),
                "hot_leads_count": len(hot_leads),
                "high_priority_followups": len(high_priority_followups),
                "contact_breakdown": self._get_contact_breakdown(contact_ratings),
                "engagement_metrics": self._get_engagement_metrics(contact_ratings)
            }
            
            prompt = f"""
            {self.project_context}
            
            DAILY METRICS:
            {json.dumps(summary_data, indent=2)}
            
            HOT LEADS:
            {self._format_contact_summaries(hot_leads)}
            
            HIGH PRIORITY FOLLOW-UPS:
            {self._format_followup_summaries(high_priority_followups)}
            
            Generate a comprehensive daily briefing in JSON format:
            {{
                "new_opportunities": ["list of new opportunities identified"],
                "market_insights": ["key market insights from conversations"],
                "action_items": ["specific actions to take today"],
                "performance_metrics": {{
                    "pipeline_health": "assessment of overall pipeline",
                    "conversion_trends": "trends in lead conversion",
                    "engagement_quality": "quality of recent engagements"
                }},
                "strategic_recommendations": ["high-level strategic recommendations"]
            }}
            
            Focus on:
            - Immediate actions needed today
            - Emerging opportunities and trends
            - Pipeline health and conversion potential
            - Strategic insights from conversation patterns
            - Market sentiment and timing considerations
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior business development strategist providing executive briefings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            briefing_data = json.loads(response.choices[0].message.content)
            
            return DailyBriefing(
                date=datetime.now(),
                total_contacts=len(contact_ratings),
                hot_leads=hot_leads,
                follow_ups_needed=high_priority_followups,
                new_opportunities=briefing_data.get('new_opportunities', []),
                market_insights=briefing_data.get('market_insights', []),
                action_items=briefing_data.get('action_items', []),
                performance_metrics=briefing_data.get('performance_metrics', {})
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating daily briefing: {e}")
            return self._create_default_briefing(contact_ratings, follow_ups)
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format messages for AI analysis"""
        formatted = []
        for msg in messages[-20:]:  # Last 20 messages
            timestamp = msg.get('timestamp', '')
            sender = msg.get('first_name', 'Unknown')
            text = msg.get('message_text', '')
            formatted.append(f"[{timestamp}] {sender}: {text}")
        return '\n'.join(formatted)
    
    def _calculate_response_rate(self, messages: List[Dict]) -> float:
        """Calculate response rate for the contact"""
        if len(messages) < 2:
            return 0.0
        
        user_messages = 0
        contact_responses = 0
        
        for i, msg in enumerate(messages):
            if msg.get('user_id') == int(os.getenv('USER_ID', 0)):
                user_messages += 1
                # Check if there's a response within reasonable time
                if i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    if next_msg.get('user_id') != int(os.getenv('USER_ID', 0)):
                        contact_responses += 1
        
        return contact_responses / user_messages if user_messages > 0 else 0.0
    
    def _get_contact_breakdown(self, ratings: List[ContactRating]) -> Dict[str, int]:
        """Get breakdown of contacts by type"""
        breakdown = {}
        for rating in ratings:
            contact_type = rating.contact_type.value
            breakdown[contact_type] = breakdown.get(contact_type, 0) + 1
        return breakdown
    
    def _get_engagement_metrics(self, ratings: List[ContactRating]) -> Dict[str, float]:
        """Calculate engagement metrics"""
        if not ratings:
            return {}
        
        avg_investment_potential = sum(r.investment_potential for r in ratings) / len(ratings)
        avg_response_rate = sum(r.response_rate for r in ratings) / len(ratings)
        avg_sentiment = sum(r.sentiment_score for r in ratings) / len(ratings)
        
        return {
            "avg_investment_potential": avg_investment_potential,
            "avg_response_rate": avg_response_rate,
            "avg_sentiment": avg_sentiment
        }
    
    def _format_contact_summaries(self, contacts: List[ContactRating]) -> str:
        """Format contact summaries for briefing"""
        summaries = []
        for contact in contacts:
            summary = f"- {contact.contact_name} ({contact.contact_type.value}): {contact.investment_potential}/10 potential"
            summaries.append(summary)
        return '\n'.join(summaries)
    
    def _format_followup_summaries(self, followups: List[FollowUpRecommendation]) -> str:
        """Format follow-up summaries for briefing"""
        summaries = []
        for followup in followups:
            summary = f"- {followup.contact_name}: {followup.recommended_action} (Priority {followup.priority})"
            summaries.append(summary)
        return '\n'.join(summaries)
    
    def _create_default_rating(self, chat_id: str, name: str, messages: List[Dict]) -> ContactRating:
        """Create default rating when AI analysis fails"""
        return ContactRating(
            contact_id=chat_id,
            contact_name=name,
            contact_type=ContactType.UNKNOWN,
            engagement_level=EngagementLevel.COLD,
            investment_potential=5.0,
            response_rate=self._calculate_response_rate(messages),
            last_interaction=datetime.fromisoformat(messages[-1]['timestamp']) if messages else datetime.now(),
            total_messages=len(messages),
            sentiment_score=0.0,
            key_interests=[],
            follow_up_priority=3,
            notes="Analysis unavailable - AI service not accessible"
        )
    
    def _create_default_recommendation(self, contact_rating: ContactRating) -> FollowUpRecommendation:
        """Create default recommendation when AI analysis fails"""
        return FollowUpRecommendation(
            contact_id=contact_rating.contact_id,
            contact_name=contact_rating.contact_name,
            priority=3,
            recommended_action="Follow up on previous conversation",
            suggested_message="Hi! Following up on our previous discussion. Would love to continue the conversation.",
            timing="within a week",
            reasoning="Default follow-up recommendation",
            context_summary="AI analysis unavailable"
        )
    
    def _create_default_briefing(self, ratings: List[ContactRating], followups: List[FollowUpRecommendation]) -> DailyBriefing:
        """Create default briefing when AI analysis fails"""
        hot_leads = [r for r in ratings if r.engagement_level == EngagementLevel.HOT]
        
        return DailyBriefing(
            date=datetime.now(),
            total_contacts=len(ratings),
            hot_leads=hot_leads,
            follow_ups_needed=followups,
            new_opportunities=["Review conversations manually for opportunities"],
            market_insights=["AI analysis unavailable - manual review needed"],
            action_items=["Check AI service connectivity", "Review high-priority contacts"],
            performance_metrics={"status": "AI analysis unavailable"}
        ) 