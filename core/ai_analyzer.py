#!/usr/bin/env python3
"""
Core AI Analyzer
===============
Consolidated AI analysis with sentiment analysis, topic extraction,
business intelligence, and actionable insights.
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re
from collections import Counter, defaultdict
import sqlite3

# AI client imports
try:
    from ollama_client import get_ollama_client
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Analysis result data structure"""
    id: str
    chat_id: str
    chat_title: str
    analysis_date: str
    message_count: int
    participant_count: int
    sentiment_score: float
    key_topics: List[str]
    activity_summary: str
    engagement_metrics: Dict[str, Any]
    ai_insights: str
    recommendations: List[str]
    business_opportunities: List[str]
    action_items: List[str]
    risk_factors: List[str]
    processing_time: float
    confidence_score: float

@dataclass
class BusinessIntelligence:
    """Business intelligence data structure"""
    id: str
    chat_id: str
    intelligence_type: str  # 'opportunity', 'risk', 'insight', 'recommendation'
    title: str
    description: str
    confidence_score: float
    priority: str  # 'low', 'medium', 'high', 'critical'
    status: str  # 'new', 'in_progress', 'completed', 'archived'
    created_at: datetime = field(default_factory=datetime.now)

class ChatAnalysis:
    """Data class for chat analysis results"""
    def __init__(self, chat_id: str, chat_title: str, sentiment_score: float, 
                 key_topics: List[str], business_opportunities: List[str], 
                 recommendations: List[str], message_count: int, participants: int):
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.sentiment_score = sentiment_score
        self.key_topics = key_topics or []
        self.business_opportunities = business_opportunities or []
        self.recommendations = recommendations or []
        self.message_count = message_count
        self.participants = participants
        self.timestamp = datetime.now()

class AIAnalyzer:
    """AI-powered chat analyzer using Ollama"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Ollama client"""
        try:
            self.client = get_ollama_client()
            logger.info("✅ AI Analyzer initialized with Ollama client")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI client: {e}")
            self.client = None
    
    async def analyze_chat(self, chat_id: str, chat_title: str, messages: List[Dict]) -> Optional[ChatAnalysis]:
        """Analyze chat messages using AI"""
        if not self.client or not messages:
            return None
        
        try:
            start_time = datetime.now()
            
            # Prepare messages for analysis
            message_texts = [msg.get('message_text', '') for msg in messages if msg.get('message_text')]
            combined_text = ' '.join(message_texts[:50])  # Limit to first 50 messages
            
            if not combined_text.strip():
                return None
            
            # Analyze sentiment
            sentiment_score = await self._analyze_sentiment(combined_text)
            
            # Extract topics
            key_topics = await self._extract_topics(combined_text)
            
            # Business analysis
            business_opportunities = await self._analyze_business_opportunities(combined_text)
            recommendations = await self._generate_recommendations(combined_text, sentiment_score)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create analysis result
            analysis = ChatAnalysis(
                chat_id=chat_id,
                chat_title=chat_title,
                sentiment_score=sentiment_score,
                key_topics=key_topics,
                business_opportunities=business_opportunities,
                recommendations=recommendations,
                message_count=len(messages),
                participants=len(set(msg.get('user_id') for msg in messages if msg.get('user_id')))
            )
            
            logger.info(f"✅ Chat analysis completed in {processing_time:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in chat analysis: {e}")
            return None
    
    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text"""
        try:
            prompt = f"""
            Analyze the sentiment of the following text and return a score between -1 (very negative) and 1 (very positive).
            Return only the numeric score, no other text.
            
            Text: {text[:1000]}
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completions_create(messages, temperature=0.1)
            
            result = response.choices[0].message["content"].strip()
            
            # Try to extract numeric value
            try:
                return float(result)
            except ValueError:
                # If parsing fails, do simple keyword analysis
                positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy', 'thanks']
                negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'sad']
                
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count == 0 and negative_count == 0:
                    return 0.0
                
                return (positive_count - negative_count) / (positive_count + negative_count)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {e}")
            return 0.0
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""
        try:
            prompt = f"""
            Extract 3-5 key topics from the following text. Return only the topics separated by commas, no other text.
            
            Text: {text[:1000]}
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completions_create(messages, temperature=0.3)
            
            result = response.choices[0].message["content"].strip()
            topics = [topic.strip() for topic in result.split(',') if topic.strip()]
            
            return topics[:5]  # Limit to 5 topics
            
        except Exception as e:
            logger.error(f"❌ Error extracting topics: {e}")
            return []
    
    async def _analyze_business_opportunities(self, text: str) -> List[str]:
        """Analyze text for business opportunities"""
        try:
            prompt = f"""
            Analyze the following text for potential business opportunities. 
            Return 2-3 specific opportunities, separated by semicolons. If no opportunities found, return "None".
            
            Text: {text[:1000]}
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completions_create(messages, temperature=0.4)
            
            result = response.choices[0].message["content"].strip()
            
            if result.lower() == "none":
                return []
            
            opportunities = [opp.strip() for opp in result.split(';') if opp.strip()]
            return opportunities[:3]
            
        except Exception as e:
            logger.error(f"❌ Error in AI business analysis: {e}")
            return []
    
    async def _generate_recommendations(self, text: str, sentiment_score: float) -> List[str]:
        """Generate actionable recommendations"""
        try:
            prompt = f"""
            Based on the following text and sentiment score ({sentiment_score:.2f}), 
            provide 2-3 actionable business recommendations.
            Return recommendations separated by semicolons.
            
            Text: {text[:1000]}
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completions_create(messages, temperature=0.4)
            
            result = response.choices[0].message["content"].strip()
            recommendations = [rec.strip() for rec in result.split(';') if rec.strip()]
            
            return recommendations[:3]
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return ["High message volume - consider automation"]
    
    async def store_analysis(self, analysis: ChatAnalysis) -> bool:
        """Store analysis results in database"""
        try:
            # Store in SQLite database
            async with self.data_manager.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO chat_analyses 
                    (chat_id, chat_title, sentiment_score, key_topics, business_opportunities, 
                     recommendations, message_count, participants, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.chat_id,
                    analysis.chat_title,
                    analysis.sentiment_score,
                    json.dumps(analysis.key_topics),
                    json.dumps(analysis.business_opportunities),
                    json.dumps(analysis.recommendations),
                    analysis.message_count,
                    analysis.participants,
                    analysis.timestamp.isoformat()
                ))
                await conn.commit()
            
            logger.info(f"✅ Analysis stored for chat {analysis.chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing analysis: {e}")
            return False
    
    def _generate_id(self, prefix: str = "analysis") -> str:
        """Generate unique ID"""
        timestamp = int(time.time())
        random_suffix = hash(str(time.time())) % 10000
        return f"{prefix}_{timestamp}_{random_suffix}"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Remove URLs, mentions, and special characters
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using simple NLP"""
        if not text:
            return []
        
        # Clean text
        clean_text = self._clean_text(text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours',
            'his', 'hers', 'ours', 'theirs', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', clean_text)
        words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Count frequency
        word_counts = Counter(words)
        
        # Return most common keywords
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    async def analyze_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment of text"""
        if not text:
            return 0.0, 0.0
        
        # Check cache first
        cache_key = f"sentiment_{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            if self.client:
                # Use AI for sentiment analysis
                prompt = f"""
                Analyze the sentiment of this text and provide a score between -1 (very negative) and 1 (very positive).
                Also provide a confidence score between 0 and 1.
                
                Text: "{text}"
                
                Respond in JSON format:
                {{"sentiment": <score>, "confidence": <confidence>}}
                """
                
                response = self.client.chat_completions_create(prompt)
                
                try:
                    result = response.choices[0].message["content"].strip()
                    sentiment = float(result)
                    confidence = 0.5  # Placeholder confidence
                except:
                    # Fallback to simple analysis
                    sentiment, confidence = self._simple_sentiment_analysis(text)
            else:
                # Fallback to simple analysis
                sentiment, confidence = self._simple_sentiment_analysis(text)
            
            # Cache result
            self.cache[cache_key] = (sentiment, confidence)
            return sentiment, confidence
            
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {e}")
            return 0.0, 0.0
    
    def _simple_sentiment_analysis(self, text: str) -> Tuple[float, float]:
        """Simple rule-based sentiment analysis"""
        if not text:
            return 0.0, 0.0
        
        text_lower = text.lower()
        
        # Positive words
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'love', 'like', 'happy', 'joy', 'excited', 'thrilled', 'perfect', 'best',
            'success', 'win', 'profit', 'gain', 'improve', 'better', 'positive'
        }
        
        # Negative words
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike',
            'sad', 'angry', 'frustrated', 'disappointed', 'fail', 'loss', 'problem',
            'issue', 'error', 'broken', 'negative', 'poor', 'weak'
        }
        
        # Count positive and negative words
        words = re.findall(r'\b\w+\b', text_lower)
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Calculate sentiment score
        total_words = len(words)
        if total_words == 0:
            return 0.0, 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        sentiment = max(-1.0, min(1.0, sentiment * 5))  # Scale and clamp
        
        # Calculate confidence based on word count
        confidence = min(0.9, total_words / 50)  # Higher confidence with more words
        
        return sentiment, confidence
    
    async def extract_topics(self, messages: List[Dict]) -> List[str]:
        """Extract key topics from messages"""
        if not messages:
            return []
        
        try:
            # Combine all message texts
            all_text = " ".join([msg.get('message_text', '') for msg in messages])
            
            if self.client:
                # Use AI for topic extraction
                prompt = f"""
                Extract the main topics from this conversation text. Return only the topic names, separated by commas.
                Focus on business-relevant topics, trends, and key themes.
                
                Text: "{all_text[:2000]}"  # Limit text length
                
                Topics:
                """
                
                response = self.client.chat_completions_create(prompt)
                topics = [topic.strip() for topic in response.choices[0].message["content"].split(',') if topic.strip()]
            else:
                # Fallback to keyword extraction
                keywords = self._extract_keywords(all_text, max_keywords=15)
                topics = keywords[:10]  # Limit to 10 topics
            
            return topics[:10]  # Return top 10 topics
            
        except Exception as e:
            logger.error(f"❌ Error extracting topics: {e}")
            return []
    
    async def generate_business_insights(self, messages: List[Dict], sentiment: float, topics: List[str]) -> Dict[str, Any]:
        """Generate business intelligence insights"""
        try:
            # Analyze message patterns
            user_activity = defaultdict(int)
            message_types = defaultdict(int)
            time_patterns = defaultdict(int)
            
            for msg in messages:
                user_id = msg.get('user_id', 'unknown')
                user_activity[user_id] += 1
                
                msg_type = msg.get('message_type', 'text')
                message_types[msg_type] += 1
                
                # Analyze time patterns (hour of day)
                timestamp = msg.get('timestamp')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_patterns[dt.hour] += 1
                    except:
                        pass
            
            # Generate insights
            insights = {
                'engagement_metrics': {
                    'total_messages': len(messages),
                    'unique_users': len(user_activity),
                    'avg_messages_per_user': len(messages) / max(len(user_activity), 1),
                    'most_active_hour': max(time_patterns.items(), key=lambda x: x[1])[0] if time_patterns else 0,
                    'message_type_distribution': dict(message_types)
                },
                'sentiment_analysis': {
                    'overall_sentiment': sentiment,
                    'sentiment_category': self._categorize_sentiment(sentiment),
                    'confidence': 0.8  # Placeholder
                },
                'key_topics': topics,
                'business_opportunities': [],
                'risk_factors': [],
                'recommendations': []
            }
            
            # Generate business opportunities and risks
            if self.client:
                insights.update(await self._ai_business_analysis(messages, sentiment, topics))
            else:
                insights.update(self._rule_based_business_analysis(messages, sentiment, topics))
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating business insights: {e}")
            return {}
    
    async def _ai_business_analysis(self, messages: List[Dict], sentiment: float, topics: List[str]) -> Dict[str, Any]:
        """AI-powered business analysis"""
        try:
            # Sample messages for analysis
            sample_messages = messages[:50]  # Limit for AI processing
            sample_text = " ".join([msg.get('message_text', '') for msg in sample_messages])
            
            prompt = f"""
            Analyze this business conversation and provide insights in JSON format:
            
            Conversation: "{sample_text[:1500]}"
            Overall Sentiment: {sentiment}
            Key Topics: {', '.join(topics)}
            
            Provide analysis in this JSON format:
            {{
                "business_opportunities": ["opportunity1", "opportunity2"],
                "risk_factors": ["risk1", "risk2"],
                "recommendations": ["recommendation1", "recommendation2"],
                "action_items": ["action1", "action2"]
            }}
            """
            
            response = self.client.chat_completions_create(prompt)
            
            try:
                result = response.choices[0].message["content"].strip()
                return json.loads(result)
            except:
                return self._rule_based_business_analysis(messages, sentiment, topics)
                
        except Exception as e:
            logger.error(f"❌ Error in AI business analysis: {e}")
            return self._rule_based_business_analysis(messages, sentiment, topics)
    
    def _rule_based_business_analysis(self, messages: List[Dict], sentiment: float, topics: List[str]) -> Dict[str, Any]:
        """Rule-based business analysis fallback"""
        opportunities = []
        risks = []
        recommendations = []
        action_items = []
        
        # Analyze sentiment-based opportunities/risks
        if sentiment > 0.3:
            opportunities.append("Positive sentiment indicates potential for business growth")
        elif sentiment < -0.3:
            risks.append("Negative sentiment may indicate customer dissatisfaction")
        
        # Analyze topics for business relevance
        business_keywords = {
            'opportunity': ['deal', 'contract', 'partnership', 'collaboration', 'investment'],
            'risk': ['problem', 'issue', 'complaint', 'delay', 'cancel'],
            'action': ['meeting', 'call', 'follow', 'review', 'discuss']
        }
        
        for topic in topics:
            topic_lower = topic.lower()
            for category, keywords in business_keywords.items():
                if any(keyword in topic_lower for keyword in keywords):
                    if category == 'opportunity':
                        opportunities.append(f"Business opportunity identified: {topic}")
                    elif category == 'risk':
                        risks.append(f"Potential risk identified: {topic}")
                    elif category == 'action':
                        action_items.append(f"Action required: {topic}")
        
        # Generate recommendations
        if opportunities:
            recommendations.append("Focus on identified business opportunities")
        if risks:
            recommendations.append("Address potential risks proactively")
        if len(messages) > 100:
            recommendations.append("High message volume - consider automation")
        
        return {
            'business_opportunities': opportunities,
            'risk_factors': risks,
            'recommendations': recommendations,
            'action_items': action_items
        }
    
    def _categorize_sentiment(self, sentiment: float) -> str:
        """Categorize sentiment score"""
        if sentiment >= 0.5:
            return "Very Positive"
        elif sentiment >= 0.1:
            return "Positive"
        elif sentiment >= -0.1:
            return "Neutral"
        elif sentiment >= -0.5:
            return "Negative"
        else:
            return "Very Negative"
    
    async def close(self):
        """Cleanup resources"""
        logger.info("✅ AI Analyzer closed successfully") 