#!/usr/bin/env python3
"""
Automated Intelligence System for Telegram Manager Bot
Provides intelligent message analysis, contact profiling, and business intelligence
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
import re
from google_sheets_integration import GoogleSheetsManager
from chat_history_manager import ChatHistoryManager
import schedule
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContactProfile:
    """Comprehensive contact profile with business intelligence"""
    user_id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    category: str  # 'business_partner', 'lead', 'organization', 'random'
    priority: int  # 1-5 (5 being highest)
    
    # Communication patterns
    message_count: int = 0
    last_message_date: Optional[str] = None
    response_time_avg: Optional[float] = None
    active_hours: List[int] = None
    message_length_avg: float = 0
    
    # Business intelligence
    company: str = ""
    role: str = ""
    industry: str = ""
    location: str = ""
    interests: List[str] = None
    pain_points: List[str] = None
    opportunities: List[str] = None
    
    # Sentiment and engagement
    sentiment_score: float = 0
    engagement_level: str = "low"  # low, medium, high
    lead_score: float = 0
    
    # Relationship insights
    relationship_strength: float = 0
    trust_level: str = "unknown"
    collaboration_potential: float = 0
    
    # Key insights and takeaways
    key_insights: List[str] = None
    action_items: List[str] = None
    follow_up_required: bool = False
    next_follow_up: Optional[str] = None
    
    def __post_init__(self):
        if self.active_hours is None:
            self.active_hours = []
        if self.interests is None:
            self.interests = []
        if self.pain_points is None:
            self.pain_points = []
        if self.opportunities is None:
            self.opportunities = []
        if self.key_insights is None:
            self.key_insights = []
        if self.action_items is None:
            self.action_items = []

@dataclass
class BusinessIntelligence:
    """Business intelligence data structure"""
    total_contacts: int
    business_partners: int
    leads: int
    organizations: int
    
    # Lead generation metrics
    new_leads_this_month: int
    lead_conversion_rate: float
    average_lead_score: float
    
    # Communication insights
    most_active_contacts: List[Dict]
    top_industries: List[Dict]
    engagement_trends: Dict
    
    # Revenue opportunities
    potential_revenue: float
    pipeline_value: float
    top_opportunities: List[Dict]

class AutomatedIntelligenceSystem:
    """Main automated intelligence system"""
    
    def __init__(self, api_id: str, api_hash: str, bot_token: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.client = None
        self.gsheets = GoogleSheetsManager()
        self.chat_history = ChatHistoryManager()
        
        # Data storage
        self.contact_profiles: Dict[int, ContactProfile] = {}
        self.business_intelligence = None
        self.message_cache = {}
        
        # Configuration
        self.sync_interval = 300  # 5 minutes
        self.analysis_interval = 3600  # 1 hour
        self.report_interval = 86400  # 24 hours
        
        # Keywords for categorization
        self.business_keywords = [
            'business', 'company', 'startup', 'enterprise', 'corporate',
            'investment', 'funding', 'partnership', 'collaboration',
            'project', 'deal', 'contract', 'proposal', 'meeting',
            'revenue', 'profit', 'growth', 'expansion', 'market'
        ]
        
        self.lead_keywords = [
            'interested', 'looking for', 'need', 'want', 'searching',
            'problem', 'solution', 'help', 'support', 'service',
            'price', 'cost', 'budget', 'quote', 'proposal',
            'demo', 'trial', 'test', 'evaluate', 'consider'
        ]
        
        self.organization_keywords = [
            'organization', 'association', 'foundation', 'institute',
            'government', 'ministry', 'department', 'agency',
            'university', 'college', 'school', 'academy',
            'non-profit', 'ngo', 'charity', 'community'
        ]
    
    async def initialize(self):
        """Initialize the system"""
        logger.info("🤖 Initializing Automated Intelligence System...")
        
        # Initialize Telegram client
        self.client = TelegramClient('automated_intelligence', self.api_id, self.api_hash)
        await self.client.start()
        
        # Load existing profiles
        await self.load_contact_profiles()
        
        # Initialize Google Sheets
        await self.initialize_google_sheets()
        
        logger.info("✅ Automated Intelligence System initialized")
    
    async def initialize_google_sheets(self):
        """Initialize Google Sheets with intelligence sheets"""
        try:
            # Create intelligence sheets
            sheets_config = {
                'contact_profiles': {
                    'headers': [
                        'User ID', 'Username', 'Name', 'Category', 'Priority',
                        'Company', 'Role', 'Industry', 'Lead Score',
                        'Last Message', 'Engagement Level', 'Key Insights',
                        'Action Items', 'Next Follow Up'
                    ]
                },
                'business_intelligence': {
                    'headers': [
                        'Date', 'Total Contacts', 'Business Partners', 'Leads',
                        'New Leads', 'Conversion Rate', 'Pipeline Value',
                        'Top Industries', 'Engagement Score'
                    ]
                },
                'message_analytics': {
                    'headers': [
                        'Date', 'Contact ID', 'Message Count', 'Sentiment',
                        'Keywords', 'Topics', 'Response Time', 'Engagement'
                    ]
                },
                'lead_pipeline': {
                    'headers': [
                        'Lead ID', 'Name', 'Company', 'Industry', 'Lead Score',
                        'Source', 'Status', 'Value', 'Next Action', 'Created Date'
                    ]
                }
            }
            
            for sheet_name, config in sheets_config.items():
                await self.gsheets.create_or_clear_sheet(sheet_name, config['headers'])
            
            logger.info("✅ Google Sheets intelligence sheets initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Google Sheets: {e}")
    
    async def load_contact_profiles(self):
        """Load existing contact profiles from storage"""
        try:
            if os.path.exists('data/contact_profiles.json'):
                with open('data/contact_profiles.json', 'r') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        self.contact_profiles[int(user_id)] = ContactProfile(**profile_data)
                logger.info(f"📊 Loaded {len(self.contact_profiles)} contact profiles")
        except Exception as e:
            logger.error(f"❌ Error loading contact profiles: {e}")
    
    async def save_contact_profiles(self):
        """Save contact profiles to storage"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/contact_profiles.json', 'w') as f:
                json.dump({str(k): asdict(v) for k, v in self.contact_profiles.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving contact profiles: {e}")
    
    async def categorize_contact(self, user: User, messages: List[Dict]) -> Tuple[str, int]:
        """Categorize contact based on messages and profile"""
        if not messages:
            return "random", 1
        
        # Analyze message content
        all_text = " ".join([msg.get('text', '') for msg in messages if msg.get('text')])
        all_text_lower = all_text.lower()
        
        # Check for business keywords
        business_score = sum(1 for keyword in self.business_keywords if keyword in all_text_lower)
        lead_score = sum(1 for keyword in self.lead_keywords if keyword in all_text_lower)
        org_score = sum(1 for keyword in self.organization_keywords if keyword in all_text_lower)
        
        # Check username and name patterns
        username = user.username or ""
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        
        # Business indicators in name
        if any(word in username.lower() for word in ['inc', 'llc', 'corp', 'ltd', 'co']):
            business_score += 3
        
        if any(word in first_name.lower() for word in ['ceo', 'cto', 'cfo', 'vp', 'director', 'manager']):
            business_score += 2
        
        # Message frequency and engagement
        message_count = len(messages)
        if message_count > 50:
            business_score += 2
        elif message_count > 20:
            business_score += 1
        
        # Determine category and priority
        if business_score >= 3:
            category = "business_partner"
            priority = min(5, 3 + business_score)
        elif lead_score >= 2:
            category = "lead"
            priority = min(4, 2 + lead_score)
        elif org_score >= 2:
            category = "organization"
            priority = 3
        else:
            category = "random"
            priority = 1
        
        return category, priority
    
    async def analyze_messages(self, messages: List[Dict]) -> Dict:
        """Analyze messages for insights"""
        if not messages:
            return {}
        
        analysis = {
            'sentiment': 0,
            'topics': [],
            'keywords': [],
            'response_times': [],
            'active_hours': [],
            'message_lengths': [],
            'interests': [],
            'pain_points': [],
            'opportunities': []
        }
        
        # Analyze each message
        for i, msg in enumerate(messages):
            text = msg.get('text', '')
            if not text:
                continue
            
            # Message length
            analysis['message_lengths'].append(len(text))
            
            # Active hours
            if 'date' in msg:
                hour = datetime.fromisoformat(msg['date']).hour
                analysis['active_hours'].append(hour)
            
            # Response time
            if i > 0 and 'date' in msg and 'date' in messages[i-1]:
                current_time = datetime.fromisoformat(msg['date'])
                prev_time = datetime.fromisoformat(messages[i-1]['date'])
                response_time = (current_time - prev_time).total_seconds() / 3600  # hours
                if response_time < 24:  # Only count same-day responses
                    analysis['response_times'].append(response_time)
            
            # Extract keywords and topics
            words = re.findall(r'\b\w+\b', text.lower())
            analysis['keywords'].extend(words)
            
            # Simple sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy', 'excited']
            negative_words = ['bad', 'terrible', 'hate', 'dislike', 'angry', 'frustrated', 'problem', 'issue']
            
            sentiment = 0
            for word in words:
                if word in positive_words:
                    sentiment += 1
                elif word in negative_words:
                    sentiment -= 1
            
            analysis['sentiment'] += sentiment
            
            # Extract interests, pain points, and opportunities
            interest_indicators = ['interested in', 'like', 'love', 'enjoy', 'passionate about']
            pain_indicators = ['problem', 'issue', 'difficult', 'challenge', 'struggle', 'need help']
            opportunity_indicators = ['opportunity', 'potential', 'could', 'might', 'consider', 'looking for']
            
            for indicator in interest_indicators:
                if indicator in text.lower():
                    analysis['interests'].append(text)
            
            for indicator in pain_indicators:
                if indicator in text.lower():
                    analysis['pain_points'].append(text)
            
            for indicator in opportunity_indicators:
                if indicator in text.lower():
                    analysis['opportunities'].append(text)
        
        # Calculate averages
        if analysis['message_lengths']:
            analysis['avg_message_length'] = sum(analysis['message_lengths']) / len(analysis['message_lengths'])
        
        if analysis['response_times']:
            analysis['avg_response_time'] = sum(analysis['response_times']) / len(analysis['response_times'])
        
        if analysis['sentiment'] != 0:
            analysis['sentiment_score'] = analysis['sentiment'] / len(messages)
        
        # Get most common keywords
        keyword_counts = Counter(analysis['keywords'])
        analysis['top_keywords'] = [word for word, count in keyword_counts.most_common(10)]
        
        return analysis
    
    async def create_contact_profile(self, user: User, messages: List[Dict]) -> ContactProfile:
        """Create comprehensive contact profile"""
        # Categorize contact
        category, priority = await self.categorize_contact(user, messages)
        
        # Analyze messages
        analysis = await self.analyze_messages(messages)
        
        # Create profile
        profile = ContactProfile(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            phone=user.phone or "",
            category=category,
            priority=priority,
            message_count=len(messages),
            last_message_date=messages[-1]['date'] if messages else None,
            response_time_avg=analysis.get('avg_response_time'),
            active_hours=analysis.get('active_hours', []),
            message_length_avg=analysis.get('avg_message_length', 0),
            sentiment_score=analysis.get('sentiment_score', 0),
            interests=analysis.get('interests', []),
            pain_points=analysis.get('pain_points', []),
            opportunities=analysis.get('opportunities', [])
        )
        
        # Calculate engagement level
        if profile.message_count > 50:
            profile.engagement_level = "high"
        elif profile.message_count > 20:
            profile.engagement_level = "medium"
        else:
            profile.engagement_level = "low"
        
        # Calculate lead score for business contacts
        if category in ['business_partner', 'lead']:
            profile.lead_score = min(100, (
                profile.message_count * 2 +
                profile.priority * 10 +
                (profile.sentiment_score + 1) * 20 +
                len(profile.interests) * 5 +
                len(profile.opportunities) * 10
            ))
        
        # Generate key insights
        profile.key_insights = await self.generate_insights(profile, analysis)
        
        # Generate action items
        profile.action_items = await self.generate_action_items(profile)
        
        return profile
    
    async def generate_insights(self, profile: ContactProfile, analysis: Dict) -> List[str]:
        """Generate key insights about the contact"""
        insights = []
        
        # Communication patterns
        if profile.message_count > 50:
            insights.append("High engagement - frequent communicator")
        elif profile.message_count < 5:
            insights.append("Low engagement - minimal communication")
        
        if profile.response_time_avg and profile.response_time_avg < 2:
            insights.append("Quick responder - values prompt communication")
        
        if profile.active_hours:
            peak_hour = max(set(profile.active_hours), key=profile.active_hours.count)
            insights.append(f"Most active during {peak_hour}:00 hours")
        
        # Business insights
        if profile.category == 'business_partner':
            insights.append("Established business relationship")
        elif profile.category == 'lead':
            insights.append("Potential business opportunity")
        
        if profile.interests:
            insights.append(f"Shows interest in: {', '.join(profile.interests[:3])}")
        
        if profile.pain_points:
            insights.append(f"Has challenges with: {', '.join(profile.pain_points[:3])}")
        
        if profile.opportunities:
            insights.append(f"Opportunities identified: {', '.join(profile.opportunities[:3])}")
        
        # Sentiment insights
        if profile.sentiment_score > 0.5:
            insights.append("Positive sentiment - satisfied with interactions")
        elif profile.sentiment_score < -0.5:
            insights.append("Negative sentiment - may need attention")
        
        return insights
    
    async def generate_action_items(self, profile: ContactProfile) -> List[str]:
        """Generate action items for the contact"""
        actions = []
        
        if profile.category == 'lead' and profile.lead_score > 50:
            actions.append("Schedule follow-up call/meeting")
            actions.append("Send personalized proposal")
        
        if profile.pain_points:
            actions.append("Address identified pain points")
        
        if profile.opportunities:
            actions.append("Explore collaboration opportunities")
        
        if profile.sentiment_score < 0:
            actions.append("Check in to address concerns")
        
        if profile.message_count < 10 and profile.category in ['business_partner', 'lead']:
            actions.append("Increase engagement frequency")
        
        if profile.last_message_date:
            last_msg_date = datetime.fromisoformat(profile.last_message_date)
            days_since = (datetime.now() - last_msg_date).days
            if days_since > 7:
                actions.append(f"Follow up (last contact {days_since} days ago)")
        
        return actions
    
    async def sync_messages(self):
        """Sync and analyze new messages"""
        logger.info("🔄 Starting message sync...")
        
        try:
            # Get recent messages from all chats
            async for dialog in self.client.iter_dialogs():
                if dialog.is_user:  # Only individual users
                    user = dialog.entity
                    messages = await self.chat_history.get_messages(user.id, limit=100)
                    
                    if messages:
                        # Create or update profile
                        if user.id in self.contact_profiles:
                            # Update existing profile
                            profile = self.contact_profiles[user.id]
                            profile.message_count = len(messages)
                            profile.last_message_date = messages[-1]['date'] if messages else None
                            
                            # Re-analyze for new insights
                            analysis = await self.analyze_messages(messages)
                            profile.key_insights = await self.generate_insights(profile, analysis)
                            profile.action_items = await self.generate_action_items(profile)
                        else:
                            # Create new profile
                            profile = await self.create_contact_profile(user, messages)
                            self.contact_profiles[user.id] = profile
                        
                        logger.info(f"📊 Updated profile for {user.first_name} ({profile.category}, priority: {profile.priority})")
            
            # Save profiles
            await self.save_contact_profiles()
            
            logger.info(f"✅ Message sync completed. {len(self.contact_profiles)} profiles updated")
            
        except Exception as e:
            logger.error(f"❌ Error during message sync: {e}")
    
    async def update_google_sheets(self):
        """Update Google Sheets with latest data"""
        try:
            logger.info("📊 Updating Google Sheets...")
            
            # Update contact profiles sheet
            profiles_data = []
            for profile in self.contact_profiles.values():
                profiles_data.append([
                    profile.user_id,
                    profile.username,
                    f"{profile.first_name} {profile.last_name}".strip(),
                    profile.category,
                    profile.priority,
                    profile.company,
                    profile.role,
                    profile.industry,
                    profile.lead_score,
                    profile.last_message_date,
                    profile.engagement_level,
                    "; ".join(profile.key_insights[:3]),
                    "; ".join(profile.action_items[:3]),
                    profile.next_follow_up or ""
                ])
            
            await self.gsheets.update_sheet('contact_profiles', profiles_data)
            
            # Update business intelligence
            await self.update_business_intelligence()
            
            # Update lead pipeline
            await self.update_lead_pipeline()
            
            logger.info("✅ Google Sheets updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error updating Google Sheets: {e}")
    
    async def update_business_intelligence(self):
        """Update business intelligence metrics"""
        try:
            # Calculate metrics
            total_contacts = len(self.contact_profiles)
            business_partners = len([p for p in self.contact_profiles.values() if p.category == 'business_partner'])
            leads = len([p for p in self.contact_profiles.values() if p.category == 'lead'])
            organizations = len([p for p in self.contact_profiles.values() if p.category == 'organization'])
            
            # Lead metrics
            high_value_leads = [p for p in self.contact_profiles.values() if p.lead_score > 70]
            avg_lead_score = sum(p.lead_score for p in self.contact_profiles.values() if p.category == 'lead') / max(leads, 1)
            
            # Engagement trends
            high_engagement = len([p for p in self.contact_profiles.values() if p.engagement_level == 'high'])
            medium_engagement = len([p for p in self.contact_profiles.values() if p.engagement_level == 'medium'])
            
            # Industry analysis
            industries = Counter([p.industry for p in self.contact_profiles.values() if p.industry])
            top_industries = [{"industry": ind, "count": count} for ind, count in industries.most_common(5)]
            
            # Pipeline value (estimated)
            pipeline_value = sum(p.lead_score * 100 for p in self.contact_profiles.values() if p.category == 'lead')
            
            # Create BI data
            bi_data = [[
                datetime.now().strftime('%Y-%m-%d'),
                total_contacts,
                business_partners,
                leads,
                len(high_value_leads),
                round(avg_lead_score, 2),
                round(pipeline_value, 2),
                "; ".join([f"{ind['industry']}: {ind['count']}" for ind in top_industries]),
                round((high_engagement + medium_engagement * 0.5) / max(total_contacts, 1) * 100, 2)
            ]]
            
            await self.gsheets.update_sheet('business_intelligence', bi_data)
            
        except Exception as e:
            logger.error(f"❌ Error updating business intelligence: {e}")
    
    async def update_lead_pipeline(self):
        """Update lead pipeline sheet"""
        try:
            leads = [p for p in self.contact_profiles.values() if p.category == 'lead']
            
            pipeline_data = []
            for lead in leads:
                # Determine status based on lead score and engagement
                if lead.lead_score > 80:
                    status = "Hot Lead"
                elif lead.lead_score > 60:
                    status = "Warm Lead"
                else:
                    status = "Cold Lead"
                
                pipeline_data.append([
                    lead.user_id,
                    f"{lead.first_name} {lead.last_name}".strip(),
                    lead.company,
                    lead.industry,
                    round(lead.lead_score, 2),
                    "Telegram",
                    status,
                    round(lead.lead_score * 100, 2),  # Estimated value
                    lead.action_items[0] if lead.action_items else "Follow up",
                    lead.last_message_date or ""
                ])
            
            await self.gsheets.update_sheet('lead_pipeline', pipeline_data)
            
        except Exception as e:
            logger.error(f"❌ Error updating lead pipeline: {e}")
    
    async def generate_analytics_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        report = {
            'summary': {},
            'top_contacts': [],
            'business_opportunities': [],
            'insights': [],
            'recommendations': []
        }
        
        # Summary statistics
        total_contacts = len(self.contact_profiles)
        business_partners = len([p for p in self.contact_profiles.values() if p.category == 'business_partner'])
        leads = len([p for p in self.contact_profiles.values() if p.category == 'lead'])
        
        report['summary'] = {
            'total_contacts': total_contacts,
            'business_partners': business_partners,
            'leads': leads,
            'conversion_rate': round(leads / max(total_contacts, 1) * 100, 2),
            'avg_lead_score': round(sum(p.lead_score for p in self.contact_profiles.values() if p.category == 'lead') / max(leads, 1), 2)
        }
        
        # Top contacts by priority and engagement
        sorted_contacts = sorted(
            self.contact_profiles.values(),
            key=lambda x: (x.priority, x.lead_score, x.message_count),
            reverse=True
        )
        
        report['top_contacts'] = [
            {
                'name': f"{p.first_name} {p.last_name}".strip(),
                'category': p.category,
                'priority': p.priority,
                'lead_score': p.lead_score,
                'key_insights': p.key_insights[:3]
            }
            for p in sorted_contacts[:10]
        ]
        
        # Business opportunities
        opportunities = []
        for profile in self.contact_profiles.values():
            if profile.opportunities:
                opportunities.extend(profile.opportunities)
        
        opportunity_counts = Counter(opportunities)
        report['business_opportunities'] = [
            {'opportunity': opp, 'frequency': count}
            for opp, count in opportunity_counts.most_common(10)
        ]
        
        # Key insights
        all_insights = []
        for profile in self.contact_profiles.values():
            all_insights.extend(profile.key_insights)
        
        insight_counts = Counter(all_insights)
        report['insights'] = [
            {'insight': insight, 'frequency': count}
            for insight, count in insight_counts.most_common(10)
        ]
        
        # Recommendations
        recommendations = []
        
        # Lead generation recommendations
        if leads < total_contacts * 0.3:
            recommendations.append("Increase lead generation efforts - current lead ratio is low")
        
        # Engagement recommendations
        low_engagement = len([p for p in self.contact_profiles.values() if p.engagement_level == 'low'])
        if low_engagement > total_contacts * 0.5:
            recommendations.append("Focus on improving engagement with existing contacts")
        
        # Follow-up recommendations
        needs_followup = len([p for p in self.contact_profiles.values() if p.follow_up_required])
        if needs_followup > 0:
            recommendations.append(f"Schedule follow-ups with {needs_followup} contacts")
        
        report['recommendations'] = recommendations
        
        return report
    
    async def run_automated_system(self):
        """Run the automated intelligence system"""
        logger.info("🚀 Starting Automated Intelligence System...")
        
        # Schedule tasks
        schedule.every(self.sync_interval).seconds.do(lambda: asyncio.create_task(self.sync_messages()))
        schedule.every(self.analysis_interval).seconds.do(lambda: asyncio.create_task(self.update_google_sheets()))
        schedule.every().day.at("09:00").do(lambda: asyncio.create_task(self.generate_daily_report()))
        
        # Run initial sync
        await self.sync_messages()
        await self.update_google_sheets()
        
        # Start scheduling loop
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    async def generate_daily_report(self):
        """Generate and save daily analytics report"""
        try:
            report = await self.generate_analytics_report()
            
            # Save report to file
            os.makedirs('reports', exist_ok=True)
            report_file = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Daily report generated: {report_file}")
            
            # Send summary to Google Sheets
            summary_data = [[
                datetime.now().strftime('%Y-%m-%d'),
                report['summary']['total_contacts'],
                report['summary']['business_partners'],
                report['summary']['leads'],
                report['summary']['conversion_rate'],
                report['summary']['avg_lead_score'],
                len(report['recommendations'])
            ]]
            
            await self.gsheets.update_sheet('business_intelligence', summary_data)
            
        except Exception as e:
            logger.error(f"❌ Error generating daily report: {e}")

async def main():
    """Main function to run the automated intelligence system"""
    # Load environment variables
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not all([api_id, api_hash, bot_token]):
        logger.error("❌ Missing required environment variables")
        return
    
    # Initialize and run system
    system = AutomatedIntelligenceSystem(api_id, api_hash, bot_token)
    await system.initialize()
    await system.run_automated_system()

if __name__ == "__main__":
    asyncio.run(main()) 