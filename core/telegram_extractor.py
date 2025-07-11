#!/usr/bin/env python3
"""
Telegram Data Extractor
=======================
Extracts all chat history from Telegram using Telethon API.
Handles both individual chats and group chats with comprehensive data extraction.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import json

from telethon import TelegramClient, errors
from telethon.tl.types import (
    User, Chat, Channel, Message, MessageMediaPhoto, MessageMediaDocument,
    PeerUser, PeerChat, PeerChannel, InputPeerEmpty
)

logger = logging.getLogger(__name__)

@dataclass
class ExtractionProgress:
    """Track extraction progress"""
    total_chats: int = 0
    processed_chats: int = 0
    total_messages: int = 0
    extracted_messages: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class TelegramExtractor:
    """Extract all Telegram data for BD analysis"""
    
    def __init__(self, api_id: str, api_hash: str, phone: str, session_name: str = "telegram_bd"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        
        self.client = None
        self.progress = ExtractionProgress()
        
        # BD-relevant keywords for filtering
        self.business_keywords = {
            'investment', 'investor', 'funding', 'venture', 'capital', 'startup',
            'business', 'deal', 'partnership', 'collaboration', 'opportunity',
            'meeting', 'pitch', 'presentation', 'proposal', 'contract',
            'roi', 'revenue', 'profit', 'growth', 'scale', 'market',
            'defi', 'crypto', 'blockchain', 'token', 'protocol', 'dao'
        }
        
        logger.info("📱 Telegram Extractor initialized")
    
    async def initialize(self):
        """Initialize Telegram client"""
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            
            # Get self info
            me = await self.client.get_me()
            logger.info(f"✅ Connected as {me.first_name} {me.last_name} (@{me.username})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Telegram client initialization failed: {e}")
            return False
    
    async def extract_all_data(self) -> Dict[str, Any]:
        """Extract all chat data"""
        if not await self.initialize():
            return {}
        
        logger.info("📥 Starting comprehensive data extraction...")
        
        try:
            # Get all dialogs (chats)
            dialogs = await self.client.get_dialogs()
            self.progress.total_chats = len(dialogs)
            
            logger.info(f"📊 Found {len(dialogs)} chats to process")
            
            extraction_data = {
                'contacts': {},
                'chats': {},
                'messages': [],
                'groups': {},
                'channels': {},
                'extraction_stats': {}
            }
            
            # Process each dialog
            for dialog in dialogs:
                try:
                    await self._extract_dialog_data(dialog, extraction_data)
                    self.progress.processed_chats += 1
                    
                    # Log progress
                    if self.progress.processed_chats % 10 == 0:
                        logger.info(f"📊 Progress: {self.progress.processed_chats}/{self.progress.total_chats} chats")
                
                except Exception as e:
                    error_msg = f"Error processing chat {dialog.name}: {e}"
                    logger.error(error_msg)
                    self.progress.errors.append(error_msg)
            
            # Calculate final stats
            extraction_data['extraction_stats'] = {
                'total_chats': self.progress.total_chats,
                'processed_chats': self.progress.processed_chats,
                'total_messages': self.progress.total_messages,
                'extracted_messages': self.progress.extracted_messages,
                'contacts_found': len(extraction_data['contacts']),
                'groups_found': len(extraction_data['groups']),
                'channels_found': len(extraction_data['channels']),
                'errors': len(self.progress.errors),
                'extraction_time': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Extraction complete: {extraction_data['extraction_stats']}")
            
            # Save raw data
            await self._save_raw_data(extraction_data)
            
            return extraction_data
            
        except Exception as e:
            logger.error(f"❌ Data extraction failed: {e}")
            return {}
        
        finally:
            if self.client:
                await self.client.disconnect()
    
    async def _extract_dialog_data(self, dialog, extraction_data: Dict):
        """Extract data from a single dialog"""
        entity = dialog.entity
        chat_id = dialog.id
        
        # Determine chat type and extract basic info
        if isinstance(entity, User):
            chat_type = 'private'
            chat_title = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
            username = entity.username
            
            # Add to contacts
            extraction_data['contacts'][entity.id] = {
                'user_id': entity.id,
                'username': username,
                'first_name': entity.first_name,
                'last_name': entity.last_name,
                'phone': entity.phone,
                'is_verified': entity.verified or False,
                'is_premium': getattr(entity, 'premium', False),
                'is_bot': entity.bot or False,
                'last_seen': getattr(entity.status, 'was_online', None) if hasattr(entity, 'status') else None
            }
            
        elif isinstance(entity, Chat):
            chat_type = 'group'
            chat_title = entity.title
            username = None
            
            # Add to groups
            extraction_data['groups'][entity.id] = {
                'chat_id': entity.id,
                'title': chat_title,
                'participants_count': getattr(entity, 'participants_count', 0),
                'is_creator': getattr(entity, 'creator', False),
                'date_created': getattr(entity, 'date', None)
            }
            
        elif isinstance(entity, Channel):
            chat_type = 'channel' if entity.broadcast else 'supergroup'
            chat_title = entity.title
            username = entity.username
            
            # Add to channels
            extraction_data['channels'][entity.id] = {
                'chat_id': entity.id,
                'title': chat_title,
                'username': username,
                'participants_count': getattr(entity, 'participants_count', 0),
                'is_verified': entity.verified or False,
                'is_creator': getattr(entity, 'creator', False),
                'description': getattr(entity, 'about', None)
            }
        
        else:
            logger.warning(f"Unknown entity type: {type(entity)}")
            return
        
        # Store chat info
        extraction_data['chats'][chat_id] = {
            'chat_id': chat_id,
            'chat_type': chat_type,
            'title': chat_title,
            'username': username,
            'unread_count': dialog.unread_count,
            'last_message_date': dialog.date,
            'is_pinned': dialog.pinned
        }
        
        # Extract messages from this chat
        await self._extract_chat_messages(chat_id, entity, extraction_data)
    
    async def _extract_chat_messages(self, chat_id: int, entity, extraction_data: Dict):
        """Extract messages from a specific chat"""
        try:
            # Limit message extraction for performance (last 1000 messages or 6 months)
            limit = 1000
            offset_date = datetime.now() - timedelta(days=180)  # 6 months
            
            messages = []
            async for message in self.client.iter_messages(
                entity, 
                limit=limit,
                offset_date=offset_date
            ):
                if isinstance(message, Message):
                    message_data = await self._extract_message_data(message, chat_id)
                    if message_data:
                        messages.append(message_data)
                        self.progress.extracted_messages += 1
            
            # Add messages to extraction data
            extraction_data['messages'].extend(messages)
            
            # Update progress
            self.progress.total_messages += len(messages)
            
            # Check for business relevance
            business_score = self._calculate_business_relevance(messages)
            if chat_id in extraction_data['chats']:
                extraction_data['chats'][chat_id]['business_relevance_score'] = business_score
                extraction_data['chats'][chat_id]['message_count'] = len(messages)
            
            logger.info(f"📥 Chat {chat_id}: {len(messages)} messages (business score: {business_score})")
            
        except errors.FloodWaitError as e:
            logger.warning(f"⏳ Rate limited for {e.seconds} seconds on chat {chat_id}")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"❌ Error extracting messages from chat {chat_id}: {e}")
    
    async def _extract_message_data(self, message: Message, chat_id: int) -> Optional[Dict]:
        """Extract data from a single message"""
        try:
            # Skip service messages
            if not message.message and not message.media:
                return None
            
            # Determine message type
            message_type = 'text'
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    message_type = 'photo'
                elif isinstance(message.media, MessageMediaDocument):
                    message_type = 'document'
                else:
                    message_type = 'media'
            
            # Extract message data
            message_data = {
                'message_id': message.id,
                'chat_id': chat_id,
                'from_user_id': message.from_id.user_id if message.from_id else None,
                'date': message.date,
                'text': message.message or '',
                'message_type': message_type,
                'is_reply': bool(message.reply_to),
                'is_forwarded': bool(message.forward),
                'views': getattr(message, 'views', 0),
                'edit_date': message.edit_date,
                
                # BD analysis fields (to be filled later)
                'contains_business_keywords': self._contains_business_keywords(message.message or ''),
                'is_question': self._is_question(message.message or ''),
                'sentiment_preliminary': self._get_preliminary_sentiment(message.message or ''),
                'word_count': len((message.message or '').split()),
                'has_contact_info': self._has_contact_info(message.message or '')
            }
            
            return message_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting message data: {e}")
            return None
    
    def _contains_business_keywords(self, text: str) -> bool:
        """Check if text contains business-relevant keywords"""
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.business_keywords)
    
    def _is_question(self, text: str) -> bool:
        """Check if message is a question"""
        if not text:
            return False
        
        question_indicators = ['?', 'how', 'what', 'when', 'where', 'why', 'can you', 'could you', 'would you']
        text_lower = text.lower()
        
        return any(indicator in text_lower for indicator in question_indicators)
    
    def _get_preliminary_sentiment(self, text: str) -> str:
        """Get preliminary sentiment (positive/negative/neutral)"""
        if not text:
            return 'neutral'
        
        positive_words = ['great', 'good', 'excellent', 'amazing', 'perfect', 'yes', 'interested', 'love']
        negative_words = ['bad', 'terrible', 'no', 'not interested', 'boring', 'hate', 'disappointed']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _has_contact_info(self, text: str) -> bool:
        """Check if message contains contact information"""
        if not text:
            return False
        
        contact_patterns = ['@', 'http', 'email', 'phone', 'telegram.me', 't.me', '+1', 'call me', 'reach me']
        text_lower = text.lower()
        
        return any(pattern in text_lower for pattern in contact_patterns)
    
    def _calculate_business_relevance(self, messages: List[Dict]) -> int:
        """Calculate business relevance score for a chat (0-100)"""
        if not messages:
            return 0
        
        score = 0
        total_messages = len(messages)
        
        # Count business keywords
        business_messages = sum(1 for msg in messages if msg.get('contains_business_keywords', False))
        if business_messages > 0:
            score += min(40, (business_messages / total_messages) * 100)
        
        # Check for questions (engagement)
        questions = sum(1 for msg in messages if msg.get('is_question', False))
        if questions > 0:
            score += min(20, (questions / total_messages) * 50)
        
        # Check for contact info sharing
        contact_sharing = sum(1 for msg in messages if msg.get('has_contact_info', False))
        if contact_sharing > 0:
            score += min(20, contact_sharing * 10)
        
        # Recent activity bonus
        recent_messages = [msg for msg in messages if 
                          (datetime.now() - msg['date']).days <= 30]
        if recent_messages:
            score += min(20, len(recent_messages) / total_messages * 40)
        
        return min(100, int(score))
    
    async def _save_raw_data(self, extraction_data: Dict):
        """Save raw extraction data for backup"""
        try:
            # Create backup file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"data/telegram_extraction_{timestamp}.json"
            
            # Convert datetime objects to strings for JSON serialization
            json_data = self._prepare_for_json(extraction_data)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Raw data saved to {backup_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save raw data: {e}")
    
    def _prepare_for_json(self, data):
        """Prepare data for JSON serialization"""
        if isinstance(data, dict):
            return {key: self._prepare_for_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_json(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data 