#!/usr/bin/env python3
"""
AI Deal Analyzer - Advanced Business Development Intelligence
===========================================================
Intelligent analysis of conversations to identify:
- Deal stages and progression
- Hot leads and opportunities
- Relationship mapping
- Action items and follow-ups
- Deal closing strategies
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import openai

logger = logging.getLogger(__name__)

class DealStage(Enum):
    """Deal progression stages"""
    COLD_LEAD = "cold_lead"
    INITIAL_CONTACT = "initial_contact"
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    FOLLOW_UP = "follow_up"

class OpportunityType(Enum):
    """Types of business opportunities"""
    INVESTMENT = "investment"
    PARTNERSHIP = "partnership"
    ADVISORY = "advisory"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    REFERRAL = "referral"
    SPEAKING = "speaking"
    MEDIA = "media"

class UrgencyLevel(Enum):
    """Action urgency levels"""
    CRITICAL = "critical"  # < 24 hours
    HIGH = "high"         # 1-3 days
    MEDIUM = "medium"     # 1 week
    LOW = "low"          # 1+ weeks

@dataclass
class DealOpportunity:
    """Comprehensive deal opportunity tracking"""
    id: str
    contact_name: str
    contact_username: str
    opportunity_type: OpportunityType
    deal_stage: DealStage
    estimated_value: float
    probability: float  # 0-100%
    urgency: UrgencyLevel
    
    # Context and details
    description: str
    key_interests: List[str]
    pain_points: List[str]
    full_sail_fit_score: int  # 0-100
    
    # Conversation analysis
    last_interaction: datetime
    conversation_sentiment: float  # -1 to 1
    engagement_level: str  # high, medium, low
    response_rate: float  # 0-1
    
    # Action items
    next_action: str
    action_deadline: datetime
    recommended_approach: str
    talking_points: List[str]
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: List[str] = field(default_factory=list)

@dataclass
class RelationshipMapping:
    """Intelligent relationship and network mapping"""
    contact_id: str
    contact_name: str
    relationship_strength: float  # 0-100
    influence_level: str  # high, medium, low
    network_connections: List[str]
    introduction_potential: float  # 0-100
    mutual_connections: List[str]
    referral_likelihood: float  # 0-100

@dataclass
class ActionItem:
    """Intelligent action recommendations"""
    id: str
    contact_name: str
    action_type: str  # follow_up, proposal, meeting, call
    description: str
    urgency: UrgencyLevel
    deadline: datetime
    context: str
    success_probability: float
    recommended_message: str

class AIDealAnalyzer:
    """Advanced AI-powered deal analysis and BD intelligence"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = None
        if openai_api_key:
            openai.api_key = openai_api_key
            self.client = openai
        
        # Full Sail context for intelligent analysis
        self.full_sail_context = """
        Full Sail Innovation Summary:
        - ve(4,4) model: Revolutionary beyond traditional AMM/voting/staking
        - 86% ROE improvement (14% → 86%)
        - 8 core solutions: No massive airdrop, concentrated liquidity, strategic bootstrapping, 
          elastic emissions, insurance fund, POL gauge, oSAIL options, liquidity locking
        - Target: Sui blockchain with Foundation backing
        - Incubated by Aftermath Finance
        
        Ideal prospects: DeFi protocols, VCs, institutional investors, Sui ecosystem players
        """
        
        self.deal_keywords = {
            'investment': ['invest', 'funding', 'capital', 'round', 'valuation', 'equity', 'token sale'],
            'partnership': ['partner', 'collaborate', 'integration', 'joint', 'alliance', 'cooperation'],
            'advisory': ['advisor', 'guidance', 'mentor', 'consultation', 'expertise', 'board'],
            'customer': ['customer', 'client', 'user', 'adoption', 'implementation', 'onboard'],
            'vendor': ['vendor', 'service', 'provider', 'supply', 'outsource', 'contract'],
            'referral': ['introduce', 'connect', 'referral', 'recommend', 'know someone', 'network']
        }
        
        self.urgency_indicators = {
            'critical': ['urgent', 'asap', 'immediately', 'deadline', 'time sensitive', 'closing soon'],
            'high': ['soon', 'this week', 'priority', 'important', 'quick', 'fast track'],
            'medium': ['next week', 'upcoming', 'planning', 'considering', 'exploring'],
            'low': ['future', 'eventually', 'someday', 'long term', 'down the road']
        }
        
        self.deal_stage_indicators = {
            DealStage.INITIAL_CONTACT: ['hello', 'introduction', 'nice to meet', 'heard about'],
            DealStage.DISCOVERY: ['tell me about', 'how does', 'what is', 'explain', 'understand'],
            DealStage.QUALIFICATION: ['budget', 'timeline', 'decision maker', 'requirements', 'criteria'],
            DealStage.PROPOSAL: ['proposal', 'quote', 'terms', 'offer', 'deal structure'],
            DealStage.NEGOTIATION: ['negotiate', 'adjust', 'terms', 'price', 'conditions', 'modify'],
            DealStage.CLOSING: ['sign', 'agreement', 'contract', 'close', 'finalize', 'commit'],
            DealStage.FOLLOW_UP: ['follow up', 'check in', 'update', 'status', 'progress']
        }

    async def analyze_conversation_for_deals(self, messages: List[Dict]) -> List[DealOpportunity]:
        """Analyze conversation messages to identify and track deal opportunities"""
        try:
            if not messages:
                return []
            
            logger.info(f"🔍 Analyzing {len(messages)} messages for deal opportunities...")
            
            # Group messages by contact
            contact_conversations = self._group_messages_by_contact(messages)
            
            opportunities = []
            
            for contact_id, contact_messages in contact_conversations.items():
                if len(contact_messages) < 2:  # Skip minimal conversations
                    continue
                
                # Analyze this contact's conversation
                if self.client:
                    opportunity = await self._analyze_contact_conversation(contact_id, contact_messages)
                else:
                    # Fallback analysis without OpenAI
                    opportunity = self._analyze_contact_conversation_fallback(contact_id, contact_messages)
                
                if opportunity and opportunity.probability > 20:  # Only track viable opportunities
                    opportunities.append(opportunity)
            
            logger.info(f"✅ Identified {len(opportunities)} deal opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Error analyzing conversations for deals: {e}")
            return []

    async def _analyze_contact_conversation(self, contact_id: str, messages: List[Dict]) -> Optional[DealOpportunity]:
        """Deep analysis of individual contact conversation"""
        try:
            # Extract conversation context
            conversation_text = self._format_conversation_for_analysis(messages)
            latest_message = max(messages, key=lambda x: x.get('timestamp', ''))
            
            contact_name = latest_message.get('first_name', 'Unknown')
            contact_username = latest_message.get('username', '')
            
            # AI-powered conversation analysis
            analysis_prompt = f"""
            Analyze this business conversation for deal opportunities and relationship insights:
            
            FULL SAIL CONTEXT:
            {self.full_sail_context}
            
            CONVERSATION:
            {conversation_text}
            
            Provide detailed JSON analysis:
            {{
                "opportunity_detected": true/false,
                "opportunity_type": "investment/partnership/advisory/customer/vendor/referral",
                "deal_stage": "initial_contact/discovery/qualification/proposal/negotiation/closing/follow_up",
                "estimated_value": 0-1000000,
                "probability": 0-100,
                "urgency": "critical/high/medium/low",
                "description": "Brief opportunity description",
                "key_interests": ["interest1", "interest2"],
                "pain_points": ["pain1", "pain2"],
                "full_sail_fit_score": 0-100,
                "conversation_sentiment": -1.0 to 1.0,
                "engagement_level": "high/medium/low",
                "next_action": "Specific next step to take",
                "action_deadline_days": 1-30,
                "recommended_approach": "How to approach this contact",
                "talking_points": ["point1", "point2", "point3"],
                "relationship_strength": 0-100,
                "influence_level": "high/medium/low",
                "referral_potential": 0-100,
                "context_clues": ["clue1", "clue2"],
                "deal_signals": ["signal1", "signal2"]
            }}
            
            Focus on:
            1. Identifying genuine business opportunities
            2. Full Sail ve(4,4) model fit and interest
            3. Decision-making authority and budget
            4. Timeline and urgency indicators
            5. Relationship building opportunities
            6. Network and referral potential
            """
            
            response = await self._call_openai_analysis(analysis_prompt)
            analysis = json.loads(response)
            
            if not analysis.get('opportunity_detected', False):
                return None
            
            # Create deal opportunity
            opportunity = DealOpportunity(
                id=f"deal_{contact_id}_{int(datetime.now().timestamp())}",
                contact_name=contact_name,
                contact_username=contact_username,
                opportunity_type=OpportunityType(analysis.get('opportunity_type', 'partnership')),
                deal_stage=DealStage(analysis.get('deal_stage', 'initial_contact')),
                estimated_value=float(analysis.get('estimated_value', 0)),
                probability=float(analysis.get('probability', 50)),
                urgency=UrgencyLevel(analysis.get('urgency', 'medium')),
                description=analysis.get('description', ''),
                key_interests=analysis.get('key_interests', []),
                pain_points=analysis.get('pain_points', []),
                full_sail_fit_score=int(analysis.get('full_sail_fit_score', 50)),
                last_interaction=datetime.fromisoformat(latest_message.get('timestamp', datetime.now().isoformat())),
                conversation_sentiment=float(analysis.get('conversation_sentiment', 0)),
                engagement_level=analysis.get('engagement_level', 'medium'),
                response_rate=self._calculate_response_rate(messages),
                next_action=analysis.get('next_action', 'Follow up'),
                action_deadline=datetime.now() + timedelta(days=analysis.get('action_deadline_days', 7)),
                recommended_approach=analysis.get('recommended_approach', ''),
                talking_points=analysis.get('talking_points', [])
            )
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Error analyzing contact conversation: {e}")
            return None

    def _analyze_contact_conversation_fallback(self, contact_id: str, messages: List[Dict]) -> Optional[DealOpportunity]:
        """Fallback analysis without OpenAI API"""
        try:
            # Extract conversation context
            conversation_text = self._format_conversation_for_analysis(messages)
            latest_message = max(messages, key=lambda x: x.get('timestamp', ''))
            
            contact_name = latest_message.get('first_name', 'Unknown')
            contact_username = latest_message.get('username', '')
            
            # Rule-based analysis
            analysis = self._rule_based_analysis(conversation_text, messages)
            
            if not analysis.get('opportunity_detected', False):
                return None
            
            # Create deal opportunity
            opportunity = DealOpportunity(
                id=f"deal_{contact_id}_{int(datetime.now().timestamp())}",
                contact_name=contact_name,
                contact_username=contact_username,
                opportunity_type=OpportunityType(analysis.get('opportunity_type', 'partnership')),
                deal_stage=DealStage(analysis.get('deal_stage', 'initial_contact')),
                estimated_value=float(analysis.get('estimated_value', 0)),
                probability=float(analysis.get('probability', 50)),
                urgency=UrgencyLevel(analysis.get('urgency', 'medium')),
                description=analysis.get('description', ''),
                key_interests=analysis.get('key_interests', []),
                pain_points=analysis.get('pain_points', []),
                full_sail_fit_score=int(analysis.get('full_sail_fit_score', 50)),
                last_interaction=datetime.fromisoformat(latest_message.get('timestamp', datetime.now().isoformat())),
                conversation_sentiment=float(analysis.get('conversation_sentiment', 0)),
                engagement_level=analysis.get('engagement_level', 'medium'),
                response_rate=self._calculate_response_rate(messages),
                next_action=analysis.get('next_action', 'Follow up'),
                action_deadline=datetime.now() + timedelta(days=analysis.get('action_deadline_days', 7)),
                recommended_approach=analysis.get('recommended_approach', ''),
                talking_points=analysis.get('talking_points', [])
            )
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Error in fallback analysis: {e}")
            return None

    def _rule_based_analysis(self, conversation_text: str, messages: List[Dict]) -> Dict[str, Any]:
        """Rule-based analysis when AI is not available"""
        try:
            text_lower = conversation_text.lower()
            
            # Detect opportunity type
            opportunity_type = 'partnership'  # default
            opportunity_detected = False
            
            for opp_type, keywords in self.deal_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    opportunity_type = opp_type
                    opportunity_detected = True
                    break
            
            # Detect urgency
            urgency = 'medium'  # default
            for urgency_level, indicators in self.urgency_indicators.items():
                if any(indicator in text_lower for indicator in indicators):
                    urgency = urgency_level
                    break
            
            # Detect deal stage
            deal_stage = 'initial_contact'  # default
            for stage, indicators in self.deal_stage_indicators.items():
                if any(indicator in text_lower for indicator in indicators):
                    deal_stage = stage.value
                    break
            
            # Calculate Full Sail fit score
            full_sail_score = self._calculate_full_sail_fit(text_lower)
            
            # Estimate probability based on keywords and engagement
            probability = 30  # base probability
            
            # Boost for investment keywords
            if any(keyword in text_lower for keyword in ['invest', 'funding', 'capital', 'round']):
                probability += 20
            
            # Boost for DeFi/blockchain interest
            if any(keyword in text_lower for keyword in ['defi', 'blockchain', 'crypto', 'protocol']):
                probability += 15
            
            # Boost for Sui blockchain
            if 'sui' in text_lower:
                probability += 10
            
            # Message count factor
            if len(messages) > 5:
                probability += 10
            
            probability = min(85, probability)  # Cap at 85% for rule-based
            
            # Estimate value
            estimated_value = 0
            if 'million' in text_lower or '$' in text_lower:
                estimated_value = 100000  # Default for financial discussions
            
            # Generate description
            description = f"Potential {opportunity_type} opportunity detected through keyword analysis"
            
            # Key interests
            key_interests = []
            if 'defi' in text_lower:
                key_interests.append('DeFi protocols')
            if 'investment' in text_lower or 'funding' in text_lower:
                key_interests.append('Investment opportunities')
            if 'blockchain' in text_lower:
                key_interests.append('Blockchain technology')
            
            return {
                'opportunity_detected': opportunity_detected,
                'opportunity_type': opportunity_type,
                'deal_stage': deal_stage,
                'estimated_value': estimated_value,
                'probability': probability,
                'urgency': urgency,
                'description': description,
                'key_interests': key_interests,
                'pain_points': [],
                'full_sail_fit_score': full_sail_score,
                'conversation_sentiment': 0.0,
                'engagement_level': 'medium',
                'next_action': 'Follow up with more information',
                'action_deadline_days': 7,
                'recommended_approach': 'Share Full Sail value proposition',
                'talking_points': ['ve(4,4) model benefits', 'ROE improvements', 'Sui blockchain advantages']
            }
            
        except Exception as e:
            logger.error(f"❌ Error in rule-based analysis: {e}")
            return {'opportunity_detected': False}

    def _calculate_full_sail_fit(self, text_lower: str) -> int:
        """Calculate Full Sail fit score based on keywords"""
        score = 40  # base score
        
        # DeFi interest
        if any(keyword in text_lower for keyword in ['defi', 'decentralized finance', 'yield farming']):
            score += 15
        
        # Investment focus
        if any(keyword in text_lower for keyword in ['invest', 'funding', 'capital']):
            score += 10
        
        # Blockchain technology
        if any(keyword in text_lower for keyword in ['blockchain', 'crypto', 'protocol']):
            score += 10
        
        # Sui ecosystem
        if 'sui' in text_lower:
            score += 15
        
        # Advanced DeFi concepts
        if any(keyword in text_lower for keyword in ['amm', 'liquidity', 'staking', 'governance']):
            score += 10
        
        return min(100, score)

    async def generate_deal_closing_strategy(self, opportunity: DealOpportunity) -> Dict[str, Any]:
        """Generate intelligent deal closing strategy"""
        try:
            strategy_prompt = f"""
            Generate a comprehensive deal closing strategy for this opportunity:
            
            OPPORTUNITY DETAILS:
            - Contact: {opportunity.contact_name} (@{opportunity.contact_username})
            - Type: {opportunity.opportunity_type.value}
            - Stage: {opportunity.deal_stage.value}
            - Value: ${opportunity.estimated_value:,.0f}
            - Probability: {opportunity.probability}%
            - Urgency: {opportunity.urgency.value}
            - Full Sail Fit: {opportunity.full_sail_fit_score}/100
            - Sentiment: {opportunity.conversation_sentiment}
            - Engagement: {opportunity.engagement_level}
            
            CONTEXT:
            - Description: {opportunity.description}
            - Interests: {', '.join(opportunity.key_interests)}
            - Pain Points: {', '.join(opportunity.pain_points)}
            - Last Interaction: {opportunity.last_interaction.strftime('%Y-%m-%d')}
            
            FULL SAIL CONTEXT:
            {self.full_sail_context}
            
            Provide detailed JSON strategy:
            {{
                "primary_strategy": "Main approach to close this deal",
                "timeline": "Recommended timeline for closing",
                "key_messages": ["message1", "message2", "message3"],
                "value_propositions": ["prop1", "prop2", "prop3"],
                "objection_handling": {{"objection": "response"}},
                "next_steps": ["step1", "step2", "step3"],
                "success_metrics": ["metric1", "metric2"],
                "risk_factors": ["risk1", "risk2"],
                "mitigation_strategies": ["strategy1", "strategy2"],
                "decision_makers": ["person1", "person2"],
                "influencers": ["influencer1", "influencer2"],
                "competitive_advantages": ["advantage1", "advantage2"],
                "closing_techniques": ["technique1", "technique2"],
                "follow_up_cadence": "How often to follow up",
                "escalation_path": "When and how to escalate",
                "success_probability": 0-100
            }}
            """
            
            response = await self._call_openai_analysis(strategy_prompt)
            strategy = json.loads(response)
            
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Error generating deal closing strategy: {e}")
            return {}

    async def identify_urgent_actions(self, opportunities: List[DealOpportunity]) -> List[ActionItem]:
        """Identify urgent actions needed to close deals"""
        try:
            urgent_actions = []
            
            for opp in opportunities:
                # Calculate urgency based on multiple factors
                urgency_score = self._calculate_urgency_score(opp)
                
                if urgency_score > 70:  # High urgency threshold
                    action = await self._generate_action_item(opp, urgency_score)
                    if action:
                        urgent_actions.append(action)
            
            # Sort by urgency and probability
            urgent_actions.sort(key=lambda x: (x.urgency.value, -x.success_probability))
            
            return urgent_actions
            
        except Exception as e:
            logger.error(f"❌ Error identifying urgent actions: {e}")
            return []

    async def _generate_action_item(self, opportunity: DealOpportunity, urgency_score: float) -> Optional[ActionItem]:
        """Generate specific action item for opportunity"""
        try:
            # Determine action type based on deal stage
            action_type = self._determine_action_type(opportunity.deal_stage)
            
            # Generate intelligent message
            message_prompt = f"""
            Generate a specific, actionable follow-up message for this opportunity:
            
            OPPORTUNITY: {opportunity.description}
            CONTACT: {opportunity.contact_name}
            STAGE: {opportunity.deal_stage.value}
            INTERESTS: {', '.join(opportunity.key_interests)}
            URGENCY: {opportunity.urgency.value}
            
            FULL SAIL CONTEXT:
            {self.full_sail_context}
            
            Generate a personalized message that:
            1. References previous conversation context
            2. Addresses their specific interests/pain points
            3. Highlights relevant Full Sail benefits
            4. Includes clear call-to-action
            5. Creates urgency without being pushy
            
            Return JSON:
            {{
                "subject": "Email subject line",
                "message": "Complete message text",
                "call_to_action": "Specific next step",
                "success_probability": 0-100
            }}
            """
            
            response = await self._call_openai_analysis(message_prompt)
            message_data = json.loads(response)
            
            action = ActionItem(
                id=f"action_{opportunity.id}_{int(datetime.now().timestamp())}",
                contact_name=opportunity.contact_name,
                action_type=action_type,
                description=f"{action_type.title()} with {opportunity.contact_name} regarding {opportunity.opportunity_type.value}",
                urgency=opportunity.urgency,
                deadline=opportunity.action_deadline,
                context=opportunity.description,
                success_probability=float(message_data.get('success_probability', 50)),
                recommended_message=message_data.get('message', '')
            )
            
            return action
            
        except Exception as e:
            logger.error(f"❌ Error generating action item: {e}")
            return None

    def _group_messages_by_contact(self, messages: List[Dict]) -> Dict[str, List[Dict]]:
        """Group messages by contact for analysis"""
        contact_groups = {}
        
        for msg in messages:
            user_id = msg.get('user_id')
            if user_id and user_id != int(os.getenv('USER_ID', 0)):  # Exclude own messages
                if user_id not in contact_groups:
                    contact_groups[user_id] = []
                contact_groups[user_id].append(msg)
        
        return contact_groups

    def _format_conversation_for_analysis(self, messages: List[Dict]) -> str:
        """Format conversation for AI analysis"""
        formatted_messages = []
        
        # Sort by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', ''))
        
        for msg in sorted_messages[-20:]:  # Last 20 messages
            sender = msg.get('first_name', 'Unknown')
            text = msg.get('message_text', '')
            timestamp = msg.get('timestamp', '')
            
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = timestamp[:16]
            else:
                time_str = 'Unknown'
            
            formatted_messages.append(f"[{time_str}] {sender}: {text}")
        
        return '\n'.join(formatted_messages)

    def _calculate_response_rate(self, messages: List[Dict]) -> float:
        """Calculate response rate for engagement analysis"""
        if len(messages) < 2:
            return 0.0
        
        user_messages = 0
        responses = 0
        user_id = int(os.getenv('USER_ID', 0))
        
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', ''))
        
        for i, msg in enumerate(sorted_messages):
            if msg.get('user_id') == user_id:
                user_messages += 1
                # Check if there's a response within reasonable time
                if i + 1 < len(sorted_messages):
                    next_msg = sorted_messages[i + 1]
                    if next_msg.get('user_id') != user_id:
                        responses += 1
        
        return responses / user_messages if user_messages > 0 else 0.0

    def _calculate_urgency_score(self, opportunity: DealOpportunity) -> float:
        """Calculate urgency score based on multiple factors"""
        score = 0
        
        # Base urgency level
        urgency_scores = {
            UrgencyLevel.CRITICAL: 100,
            UrgencyLevel.HIGH: 80,
            UrgencyLevel.MEDIUM: 60,
            UrgencyLevel.LOW: 40
        }
        score += urgency_scores.get(opportunity.urgency, 50)
        
        # Deal stage urgency
        stage_scores = {
            DealStage.CLOSING: 90,
            DealStage.NEGOTIATION: 80,
            DealStage.PROPOSAL: 70,
            DealStage.QUALIFICATION: 60,
            DealStage.DISCOVERY: 50,
            DealStage.INITIAL_CONTACT: 40
        }
        score += stage_scores.get(opportunity.deal_stage, 50)
        
        # Probability and value
        score += opportunity.probability * 0.5
        
        # Time since last interaction
        days_since = (datetime.now() - opportunity.last_interaction).days
        if days_since > 7:
            score -= 20
        elif days_since > 3:
            score -= 10
        
        # Full Sail fit
        score += opportunity.full_sail_fit_score * 0.3
        
        return min(100, max(0, score / 3))  # Normalize to 0-100

    def _determine_action_type(self, deal_stage: DealStage) -> str:
        """Determine appropriate action type based on deal stage"""
        action_map = {
            DealStage.COLD_LEAD: "initial_outreach",
            DealStage.INITIAL_CONTACT: "follow_up",
            DealStage.DISCOVERY: "discovery_call",
            DealStage.QUALIFICATION: "qualification_meeting",
            DealStage.PROPOSAL: "proposal_review",
            DealStage.NEGOTIATION: "negotiation_call",
            DealStage.CLOSING: "closing_meeting",
            DealStage.FOLLOW_UP: "follow_up"
        }
        
        return action_map.get(deal_stage, "follow_up")

    async def _call_openai_analysis(self, prompt: str) -> str:
        """Call OpenAI API for analysis"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business development analyst and deal closer. Provide detailed, actionable insights in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            raise

    async def generate_daily_deal_report(self, opportunities: List[DealOpportunity]) -> Dict[str, Any]:
        """Generate comprehensive daily deal report"""
        try:
            total_value = sum(opp.estimated_value * (opp.probability / 100) for opp in opportunities)
            
            # Categorize opportunities
            hot_deals = [opp for opp in opportunities if opp.probability > 70]
            warm_deals = [opp for opp in opportunities if 40 <= opp.probability <= 70]
            cold_deals = [opp for opp in opportunities if opp.probability < 40]
            
            # Urgent actions
            urgent_opportunities = [opp for opp in opportunities if opp.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]]
            
            # Deal stages
            stage_breakdown = {}
            for stage in DealStage:
                stage_count = len([opp for opp in opportunities if opp.deal_stage == stage])
                if stage_count > 0:
                    stage_breakdown[stage.value] = stage_count
            
            report = {
                "summary": {
                    "total_opportunities": len(opportunities),
                    "total_estimated_value": total_value,
                    "hot_deals": len(hot_deals),
                    "warm_deals": len(warm_deals),
                    "cold_deals": len(cold_deals),
                    "urgent_actions": len(urgent_opportunities)
                },
                "pipeline_breakdown": stage_breakdown,
                "top_opportunities": [
                    {
                        "name": opp.contact_name,
                        "type": opp.opportunity_type.value,
                        "value": opp.estimated_value,
                        "probability": opp.probability,
                        "stage": opp.deal_stage.value,
                        "urgency": opp.urgency.value
                    }
                    for opp in sorted(opportunities, key=lambda x: x.probability * x.estimated_value, reverse=True)[:5]
                ],
                "urgent_actions": [
                    {
                        "contact": opp.contact_name,
                        "action": opp.next_action,
                        "deadline": opp.action_deadline.strftime('%Y-%m-%d'),
                        "urgency": opp.urgency.value
                    }
                    for opp in urgent_opportunities
                ],
                "full_sail_alignment": {
                    "high_fit": len([opp for opp in opportunities if opp.full_sail_fit_score > 80]),
                    "medium_fit": len([opp for opp in opportunities if 50 <= opp.full_sail_fit_score <= 80]),
                    "low_fit": len([opp for opp in opportunities if opp.full_sail_fit_score < 50])
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating daily deal report: {e}")
            return {}

    async def generate_daily_briefing(self, opportunities: List[DealOpportunity]) -> Dict[str, Any]:
        """Generate comprehensive daily briefing with actionable insights"""
        try:
            logger.info("🎯 Generating daily business development briefing...")
            
            # Priority ranking based on urgency and value
            priority_opportunities = sorted(
                opportunities, 
                key=lambda x: self._calculate_urgency_score(x) * (x.probability / 100),
                reverse=True
            )[:5]
            
            # Today's key actions
            today_actions = []
            urgent_follow_ups = []
            
            for opp in priority_opportunities:
                days_since = (datetime.now() - opp.last_interaction).days
                
                if opp.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
                    today_actions.append({
                        'contact': opp.contact_name,
                        'action': opp.next_action,
                        'priority': opp.urgency.value,
                        'context': f"{opp.opportunity_type.value.title()} - {opp.probability}% probability"
                    })
                
                if days_since >= 3:
                    urgent_follow_ups.append({
                        'contact': opp.contact_name,
                        'days_since': days_since,
                        'last_stage': opp.deal_stage.value,
                        'recommended_action': f"Re-engage with {opp.talking_points[0] if opp.talking_points else 'Full Sail updates'}"
                    })
            
            # Performance insights
            avg_probability = sum(opp.probability for opp in opportunities) / len(opportunities) if opportunities else 0
            total_pipeline_value = sum(opp.estimated_value * (opp.probability / 100) for opp in opportunities)
            
            # Success metrics
            high_probability_deals = len([opp for opp in opportunities if opp.probability > 70])
            full_sail_fit_deals = len([opp for opp in opportunities if opp.full_sail_fit_score > 80])
            
            briefing = {
                "daily_focus": self._generate_daily_focus(opportunities),
                "priority_actions": today_actions[:3],
                "urgent_follow_ups": urgent_follow_ups[:3],
                "pipeline_health": {
                    "total_opportunities": len(opportunities),
                    "average_probability": round(avg_probability, 1),
                    "pipeline_value": round(total_pipeline_value, 0),
                    "high_probability_deals": high_probability_deals,
                    "full_sail_fit_deals": full_sail_fit_deals
                },
                "key_insights": self._generate_daily_insights(opportunities),
                "recommended_activities": self._generate_daily_recommendations(opportunities)
            }
            
            logger.info("✅ Daily briefing generated successfully")
            return briefing
            
        except Exception as e:
            logger.error(f"❌ Error generating daily briefing: {e}")
            return {}

    def _generate_daily_focus(self, opportunities: List[DealOpportunity]) -> str:
        """Generate today's primary focus"""
        if not opportunities:
            return "Focus on outreach and building new relationships in the DeFi/Sui ecosystem"
        
        # Find highest priority opportunity
        top_opp = max(opportunities, key=lambda x: x.probability * x.estimated_value)
        
        if top_opp.probability > 70:
            return f"🎯 PRIMARY FOCUS: Close deal with {top_opp.contact_name} - {top_opp.opportunity_type.value} opportunity at {top_opp.probability}% probability"
        elif top_opp.deal_stage in [DealStage.NEGOTIATION, DealStage.CLOSING]:
            return f"🎯 PRIMARY FOCUS: Advance {top_opp.contact_name} from {top_opp.deal_stage.value} to closing"
        else:
            return f"🎯 PRIMARY FOCUS: Nurture top opportunities and identify 2-3 new qualified leads"

    def _generate_daily_insights(self, opportunities: List[DealOpportunity]) -> List[str]:
        """Generate key insights for the day"""
        insights = []
        
        if not opportunities:
            insights.append("Pipeline needs immediate attention - focus on lead generation")
            return insights
        
        # Analyze trends
        stalled_deals = [opp for opp in opportunities if (datetime.now() - opp.last_interaction).days > 7]
        hot_deals = [opp for opp in opportunities if opp.probability > 70]
        
        if len(stalled_deals) > len(opportunities) * 0.3:
            insights.append(f"⚠️  {len(stalled_deals)} deals haven't been touched in 7+ days - prioritize re-engagement")
        
        if hot_deals:
            insights.append(f"🔥 {len(hot_deals)} hot deals ready for aggressive closing push")
        
        # Full Sail fit analysis
        high_fit_deals = [opp for opp in opportunities if opp.full_sail_fit_score > 80]
        if high_fit_deals:
            insights.append(f"🎪 {len(high_fit_deals)} deals are excellent Full Sail fits - emphasize ve(4,4) benefits")
        
        # Stage distribution
        early_stage = len([opp for opp in opportunities if opp.deal_stage in [DealStage.INITIAL_CONTACT, DealStage.DISCOVERY]])
        if early_stage > len(opportunities) * 0.6:
            insights.append("📈 Most deals in early stages - focus on qualification and value demonstration")
        
        return insights

    def _generate_daily_recommendations(self, opportunities: List[DealOpportunity]) -> List[str]:
        """Generate actionable daily recommendations"""
        recommendations = []
        
        # Standard recommendations
        recommendations.append("✅ Review and respond to all messages from the past 24 hours")
        recommendations.append("📞 Make 3-5 meaningful connections with high-value prospects")
        recommendations.append("📝 Share 1 piece of valuable content about Full Sail's ve(4,4) innovation")
        
        if opportunities:
            # Opportunity-specific recommendations
            urgent_count = len([opp for opp in opportunities if opp.urgency == UrgencyLevel.CRITICAL])
            if urgent_count > 0:
                recommendations.append(f"🚨 Address {urgent_count} critical deadline(s) immediately")
            
            # Investment-specific recommendations
            investment_opps = [opp for opp in opportunities if opp.opportunity_type == OpportunityType.INVESTMENT]
            if investment_opps:
                recommendations.append(f"💰 Follow up on {len(investment_opps)} investment discussions - share latest traction metrics")
            
            # Partnership recommendations
            partnership_opps = [opp for opp in opportunities if opp.opportunity_type == OpportunityType.PARTNERSHIP]
            if partnership_opps:
                recommendations.append(f"🤝 Advance {len(partnership_opps)} partnership discussions - propose specific collaboration frameworks")
        
        recommendations.append("🎯 End day by identifying 2-3 new prospects for tomorrow's outreach")
        
        return recommendations

    async def generate_business_context_message(self, contact_name: str = "", context_type: str = "funding") -> Dict[str, str]:
        """Generate contextual messages based on current business situation"""
        try:
            # Business context
            funding_context = {
                "current_round": "Series A",
                "raising_amount": "$1.6M",
                "current_valuation": "$20M", 
                "launch_valuation": "$25M",
                "stage": "Raising capital while building towards launch"
            }
            
            base_context = f"""
            Current Business Context:
            - Raising {funding_context['raising_amount']} Series A at {funding_context['current_valuation']} valuation
            - Launching at {funding_context['launch_valuation']} valuation 
            - Full Sail: Revolutionary ve(4,4) DeFi protocol on Sui blockchain
            - 86% ROE improvement over traditional models
            - Backed by Aftermath Finance and Sui Foundation
            """
            
            if context_type == "funding":
                message_template = f"""
Subject: Full Sail Series A - Revolutionary DeFi Innovation on Sui

Hi{' ' + contact_name if contact_name else ''},

I wanted to share an exciting opportunity with Full Sail, where we're revolutionizing DeFi through our breakthrough ve(4,4) model.

🚀 **Current Opportunity:**
• Raising $1.6M Series A at $20M valuation
• Launching at $25M valuation (56% upside potential)
• 86% ROE improvement over traditional AMM models
• First ve(4,4) implementation on Sui blockchain

🎯 **Why Now:**
• Sui ecosystem growing rapidly with Foundation backing
• Our 8-core solution addresses critical DeFi pain points
• Incubated by Aftermath Finance (proven Sui track record)
• Strategic positioning before major DeFi expansion cycle

💡 **Investment Highlights:**
• Concentrated liquidity without massive airdrops
• Elastic emissions with insurance fund protection
• POL gauge system with oSAIL options
• Liquidity locking for sustainable growth

Would love to discuss how Full Sail fits into your DeFi investment thesis. Available for a quick call this week?

Best regards,
[Your name]

P.S. Happy to share our technical deep-dive and traction metrics if helpful.
                """
                
            elif context_type == "partnership":
                message_template = f"""
Subject: Strategic Partnership - Full Sail x {contact_name if contact_name else '[Partner]'}

Hi{' ' + contact_name if contact_name else ''},

Full Sail is building the future of DeFi on Sui, and I believe there's strong alignment for a strategic partnership.

🎪 **About Full Sail:**
• Revolutionary ve(4,4) model delivering 86% ROE improvements
• Launching at $25M valuation with Sui Foundation backing
• Currently raising $1.6M to accelerate development

🤝 **Partnership Opportunities:**
• Liquidity provisioning with premium rewards
• Technical integration and co-development
• Joint marketing and ecosystem building
• Cross-protocol governance participation

🚀 **Mutual Benefits:**
• Access to Sui's fastest-growing DeFi protocol
• Early liquidity provider advantages
• Shared technical innovation and learning
• Joint ecosystem expansion opportunities

Our ve(4,4) model creates win-win scenarios that traditional AMMs can't match. Would love to explore how we can collaborate.

Available for a partnership discussion this week?

Best,
[Your name]
                """
                
            elif context_type == "advisor":
                message_template = f"""
Subject: Advisory Opportunity - Full Sail DeFi Protocol

Hi{' ' + contact_name if contact_name else ''},

I'm reaching out regarding an advisory opportunity with Full Sail, a revolutionary DeFi protocol launching on Sui.

🎯 **The Opportunity:**
• Join as strategic advisor for groundbreaking ve(4,4) protocol
• Equity participation in $20M valuation company
• Shape the future of DeFi with 86% ROE improvements
• Work with Sui Foundation-backed innovation

🚀 **Why Your Expertise Matters:**
• [Specific reason based on their background]
• Strategic guidance during crucial growth phase
• Network access to accelerate partnerships
• Technical insights for protocol optimization

📈 **Current Traction:**
• Incubated by Aftermath Finance
• Raising $1.6M Series A (launching at $25M)
• First mover advantage in Sui DeFi ecosystem
• Proven 86% ROE improvement model

Advisory positions include equity upside and the opportunity to shape next-generation DeFi infrastructure.

Interested in a brief conversation about how you could contribute?

Best regards,
[Your name]
                """
                
            else:  # general
                message_template = f"""
Subject: Full Sail - Next-Generation DeFi on Sui Blockchain

Hi{' ' + contact_name if contact_name else ''},

Hope you're doing well! I wanted to introduce you to Full Sail, where we're building revolutionary DeFi infrastructure.

🚀 **What We're Building:**
• First ve(4,4) protocol on Sui blockchain
• 86% ROE improvement over traditional models
• 8-core solution addressing critical DeFi challenges
• Launching at $25M valuation with Foundation support

💡 **Current Momentum:**
• Raising $1.6M Series A at $20M valuation
• Incubated by Aftermath Finance
• Sui Foundation partnership secured
• Major ecosystem partnerships in development

🎯 **Why This Matters:**
• DeFi is evolving beyond simple AMM/staking models
• Sui ecosystem poised for explosive growth
• Our ve(4,4) model creates sustainable value accrual
• Early positioning in next DeFi innovation cycle

Would love to share more details and explore potential synergies. Available for a quick call this week?

Best,
[Your name]

P.S. Happy to send our technical overview and latest metrics if you're interested.
                """
            
            return {
                "subject": message_template.split('\n')[0].replace('Subject: ', ''),
                "message": message_template,
                "context_type": context_type,
                "business_stage": funding_context['stage']
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating business context message: {e}")
            return {
                "subject": "Full Sail - Revolutionary DeFi Protocol",
                "message": "Error generating personalized message. Please try again.",
                "context_type": context_type,
                "business_stage": "Unknown"
            } 