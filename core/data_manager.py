#!/usr/bin/env python3
"""
Core Data Manager
================
Consolidated data handling with sync error management, duplicate prevention,
and robust failover between local SQLite and Google Sheets.
"""

import os
import json
import sqlite3
import logging
import hashlib
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import time

# Google Sheets integration
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SyncStatus:
    """Sync status tracking"""
    id: str
    entity_type: str  # 'message', 'note', 'contact', 'analysis'
    entity_id: str
    local_hash: str
    remote_hash: Optional[str] = None
    sync_status: str = 'pending'  # 'pending', 'synced', 'failed', 'conflict'
    last_sync_attempt: Optional[datetime] = None
    sync_error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Message:
    """Message data structure with duplicate detection"""
    id: str
    message_id: int
    chat_id: int
    chat_title: str
    user_id: int
    username: str
    first_name: str
    last_name: str
    message_text: str
    message_type: str
    timestamp: datetime
    content_hash: str = field(default='')
    sentiment_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None

@dataclass
class Note:
    """Note data structure"""
    id: str
    text: str
    timestamp: datetime
    category: str = "general"
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    completed: bool = False
    content_hash: str = field(default='')

@dataclass
class Contact:
    """Contact data structure"""
    id: str
    name: str
    username: str
    phone: str
    category: str
    priority: int
    message_count: int
    last_message_date: datetime
    lead_score: float
    company: str = ""
    role: str = ""
    industry: str = ""
    interests: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    next_follow_up: Optional[datetime] = None

class DataManager:
    """Consolidated data manager with sync error handling and duplicate prevention"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Database paths
        self.local_db_path = self.data_dir / "telegram_manager.db"
        self.sync_db_path = self.data_dir / "sync_tracking.db"
        
        # Initialize databases
        self._init_local_database()
        self._init_sync_database()
        
        # Google Sheets integration
        self.google_sheets = None
        self.google_sheets_enabled = False
        self._init_google_sheets()
        
        # Connection pooling
        self.connection_pool = Queue(maxsize=10)
        self._init_connection_pool()
        
        # Sync management
        self.sync_lock = threading.Lock()
        self.sync_queue = Queue()
        self.sync_worker_running = False
        
        # Performance optimization
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_cleanup = time.time()
        
        logger.info("✅ Data Manager initialized successfully")
    
    def _init_connection_pool(self):
        """Initialize database connection pool"""
        for _ in range(10):
            conn = sqlite3.connect(self.local_db_path, check_same_thread=False)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=MEMORY')
            self.connection_pool.put(conn)
    
    def _get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.get(timeout=5)
        except:
            conn = sqlite3.connect(self.local_db_path, check_same_thread=False)
            conn.execute('PRAGMA journal_mode=WAL')
            return conn
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        try:
            self.connection_pool.put(conn, timeout=1)
        except:
            conn.close()
    
    def _init_local_database(self):
        """Initialize local SQLite database with optimized schema"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Messages table with duplicate detection
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                message_id INTEGER UNIQUE,
                chat_id INTEGER,
                chat_title TEXT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                message_text TEXT,
                message_type TEXT,
                timestamp DATETIME,
                content_hash TEXT,
                sentiment_score REAL DEFAULT 0.0,
                keywords TEXT,
                is_duplicate BOOLEAN DEFAULT FALSE,
                duplicate_of TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                timestamp DATETIME,
                category TEXT DEFAULT 'general',
                priority TEXT DEFAULT 'medium',
                tags TEXT,
                completed BOOLEAN DEFAULT FALSE,
                content_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT,
                phone TEXT,
                category TEXT,
                priority INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                last_message_date DATETIME,
                lead_score REAL DEFAULT 0.0,
                company TEXT,
                role TEXT,
                industry TEXT,
                interests TEXT,
                pain_points TEXT,
                opportunities TEXT,
                key_insights TEXT,
                action_items TEXT,
                next_follow_up DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_content_hash ON messages(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_timestamp ON notes(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_lead_score ON contacts(lead_score)')
        
        conn.commit()
        conn.close()
    
    def _init_sync_database(self):
        """Initialize sync tracking database"""
        conn = sqlite3.connect(self.sync_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                local_hash TEXT NOT NULL,
                remote_hash TEXT,
                sync_status TEXT DEFAULT 'pending',
                last_sync_attempt DATETIME,
                sync_error TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_entity ON sync_status(entity_type, entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_status(sync_status)')
        
        conn.commit()
        conn.close()
    
    def _init_google_sheets(self):
        """Initialize Google Sheets integration"""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning("⚠️ Google Sheets not available - using local storage only")
            return
        
        try:
            service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "google_service_account.json")
            spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
            
            if not os.path.exists(service_account_file):
                logger.warning("⚠️ Google service account file not found")
                return
            
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(service_account_file, scopes=scope)
            self.google_sheets = gspread.authorize(credentials)
            
            if spreadsheet_id:
                self.spreadsheet = self.google_sheets.open_by_key(spreadsheet_id)
            else:
                self.spreadsheet = self.google_sheets.create("Telegram Manager Database")
                logger.info(f"📋 Created new spreadsheet: {self.spreadsheet.id}")
            
            self.google_sheets_enabled = True
            logger.info("✅ Google Sheets integration initialized")
            
        except Exception as e:
            logger.error(f"❌ Google Sheets initialization failed: {e}")
            self.google_sheets_enabled = False
    
    def _generate_hash(self, content: str) -> str:
        """Generate content hash for duplicate detection"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _serialize_list(self, data: List[str]) -> str:
        """Serialize list to JSON string"""
        return json.dumps(data) if data else '[]'
    
    def _deserialize_list(self, data: str) -> List[str]:
        """Deserialize JSON string to list"""
        try:
            return json.loads(data) if data else []
        except:
            return []
    
    async def add_message(self, message_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add message with duplicate detection"""
        try:
            # Generate content hash
            content = f"{message_data.get('message_text', '')}{message_data.get('timestamp', '')}"
            content_hash = self._generate_hash(content)
            
            # Check for duplicates
            duplicate_id = await self._check_duplicate_message(content_hash)
            
            message = Message(
                id=f"msg_{message_data.get('message_id')}_{message_data.get('chat_id')}",
                message_id=message_data.get('message_id'),
                chat_id=message_data.get('chat_id'),
                chat_title=message_data.get('chat_title', ''),
                user_id=message_data.get('user_id'),
                username=message_data.get('username', ''),
                first_name=message_data.get('first_name', ''),
                last_name=message_data.get('last_name', ''),
                message_text=message_data.get('message_text', ''),
                message_type=message_data.get('message_type', 'text'),
                timestamp=datetime.fromisoformat(message_data.get('timestamp')),
                content_hash=content_hash,
                is_duplicate=bool(duplicate_id),
                duplicate_of=duplicate_id
            )
            
            # Store in local database
            success = await self._store_message_local(message)
            if success:
                # Queue for sync
                await self._queue_for_sync('message', message.id, content_hash)
                return True, "Message added successfully"
            else:
                return False, "Failed to store message locally"
                
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
            return False, str(e)
    
    async def _check_duplicate_message(self, content_hash: str) -> Optional[str]:
        """Check if message is duplicate based on content hash"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM messages WHERE content_hash = ? LIMIT 1',
                (content_hash,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"❌ Error checking duplicate: {e}")
            return None
        finally:
            if conn:
                self._return_connection(conn)
    
    async def _store_message_local(self, message: Message) -> bool:
        """Store message in local database"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO messages (
                    id, message_id, chat_id, chat_title, user_id, username, first_name, last_name,
                    message_text, message_type, timestamp, content_hash, sentiment_score,
                    keywords, is_duplicate, duplicate_of, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.id, message.message_id, message.chat_id, message.chat_title,
                message.user_id, message.username, message.first_name, message.last_name,
                message.message_text, message.message_type, message.timestamp.isoformat(),
                message.content_hash, message.sentiment_score, self._serialize_list(message.keywords),
                message.is_duplicate, message.duplicate_of, datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing message locally: {e}")
            return False
        finally:
            if conn:
                self._return_connection(conn)
    
    async def add_note(self, text: str, category: str = "general", priority: str = "medium", tags: List[str] = None) -> Tuple[bool, str]:
        """Add note with duplicate detection"""
        try:
            content_hash = self._generate_hash(text)
            note_id = f"note_{int(time.time())}_{hash(text) % 10000}"
            
            note = Note(
                id=note_id,
                text=text,
                timestamp=datetime.now(),
                category=category,
                priority=priority,
                tags=tags or [],
                content_hash=content_hash
            )
            
            # Store locally
            success = await self._store_note_local(note)
            if success:
                await self._queue_for_sync('note', note.id, content_hash)
                return True, f"Note added with ID: {note_id}"
            else:
                return False, "Failed to store note locally"
                
        except Exception as e:
            logger.error(f"❌ Error adding note: {e}")
            return False, str(e)
    
    async def _store_note_local(self, note: Note) -> bool:
        """Store note in local database"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notes (
                    id, text, timestamp, category, priority, tags, completed, content_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note.id, note.text, note.timestamp.isoformat(), note.category,
                note.priority, self._serialize_list(note.tags), note.completed,
                note.content_hash, datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing note locally: {e}")
            return False
        finally:
            if conn:
                self._return_connection(conn)
    
    async def get_messages(self, chat_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get messages with optional filtering"""
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if chat_id:
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE chat_id = ? AND is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                ''', (chat_id, limit, offset))
            else:
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            messages = []
            for row in cursor.fetchall():
                msg_dict = dict(row)
                msg_dict['keywords'] = self._deserialize_list(msg_dict.get('keywords', '[]'))
                messages.append(msg_dict)
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    async def get_notes(self, category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get notes with optional filtering"""
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT * FROM notes 
                    WHERE category = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (category, limit))
            else:
                cursor.execute('''
                    SELECT * FROM notes 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            notes = []
            for row in cursor.fetchall():
                note_dict = dict(row)
                note_dict['tags'] = self._deserialize_list(note_dict.get('tags', '[]'))
                notes.append(note_dict)
            
            return notes
            
        except Exception as e:
            logger.error(f"❌ Error getting notes: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    async def _queue_for_sync(self, entity_type: str, entity_id: str, content_hash: str):
        """Queue entity for sync to Google Sheets"""
        if not self.google_sheets_enabled:
            return
        
        sync_status = SyncStatus(
            id=f"sync_{entity_type}_{entity_id}",
            entity_type=entity_type,
            entity_id=entity_id,
            local_hash=content_hash
        )
        
        # Store sync status
        conn = None
        try:
            conn = sqlite3.connect(self.sync_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sync_status (
                    id, entity_type, entity_id, local_hash, sync_status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                sync_status.id, sync_status.entity_type, sync_status.entity_id,
                sync_status.local_hash, sync_status.sync_status, datetime.now().isoformat()
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error queuing sync: {e}")
        finally:
            if conn:
                conn.close()
        
        # Add to sync queue
        self.sync_queue.put(sync_status)
    
    async def start_sync_worker(self):
        """Start background sync worker"""
        if self.sync_worker_running:
            return
        
        self.sync_worker_running = True
        asyncio.create_task(self._sync_worker())
        logger.info("🔄 Sync worker started")
    
    async def _sync_worker(self):
        """Background worker for syncing data to Google Sheets"""
        while self.sync_worker_running:
            try:
                # Process sync queue
                while not self.sync_queue.empty():
                    sync_status = self.sync_queue.get_nowait()
                    await self._sync_entity(sync_status)
                
                # Retry failed syncs
                await self._retry_failed_syncs()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                logger.error(f"❌ Sync worker error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _sync_entity(self, sync_status: SyncStatus):
        """Sync individual entity to Google Sheets"""
        if not self.google_sheets_enabled:
            return
        
        try:
            # Get entity data
            entity_data = await self._get_entity_data(sync_status.entity_type, sync_status.entity_id)
            if not entity_data:
                return
            
            # Sync to Google Sheets
            success = await self._sync_to_google_sheets(sync_status.entity_type, entity_data)
            
            # Update sync status
            await self._update_sync_status(sync_status.id, success, None if success else "Sync failed")
            
        except Exception as e:
            logger.error(f"❌ Error syncing entity: {e}")
            await self._update_sync_status(sync_status.id, False, str(e))
    
    async def _get_entity_data(self, entity_type: str, entity_id: str) -> Optional[Dict]:
        """Get entity data from local database"""
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if entity_type == 'message':
                cursor.execute('SELECT * FROM messages WHERE id = ?', (entity_id,))
            elif entity_type == 'note':
                cursor.execute('SELECT * FROM notes WHERE id = ?', (entity_id,))
            else:
                return None
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"❌ Error getting entity data: {e}")
            return None
        finally:
            if conn:
                self._return_connection(conn)
    
    async def _sync_to_google_sheets(self, entity_type: str, entity_data: Dict) -> bool:
        """Sync entity data to Google Sheets"""
        try:
            if not self.google_sheets_enabled or not self.sheets_service:
                logger.warning("⚠️ Google Sheets not enabled or service not available")
                return False
            
            # Get or create the appropriate worksheet
            worksheet_name = self._get_worksheet_name(entity_type)
            worksheet = await self._get_or_create_worksheet(worksheet_name)
            
            if not worksheet:
                logger.error(f"❌ Could not get or create worksheet: {worksheet_name}")
                return False
            
            # Prepare data for Google Sheets
            row_data = self._prepare_data_for_sheets(entity_type, entity_data)
            
            if not row_data:
                logger.warning(f"⚠️ No data to sync for {entity_type}")
                return True
            
            # Append data to worksheet
            range_name = f"{worksheet_name}!A:Z"
            
            # Check if this is an update or new entry
            existing_row = await self._find_existing_row(worksheet, entity_data.get('id', ''))
            
            if existing_row:
                # Update existing row
                update_range = f"{worksheet_name}!A{existing_row}:Z{existing_row}"
                await self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=update_range,
                    valueInputOption='RAW',
                    body={'values': [row_data]}
                ).execute()
                logger.info(f"✅ Updated {entity_type} in Google Sheets: {entity_data.get('id')}")
            else:
                # Append new row
                await self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row_data]}
                ).execute()
                logger.info(f"✅ Added {entity_type} to Google Sheets: {entity_data.get('id')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error syncing to Google Sheets: {e}")
            return False
    
    def _get_worksheet_name(self, entity_type: str) -> str:
        """Get worksheet name for entity type"""
        worksheet_map = {
            'message': 'Messages',
            'note': 'Notes',
            'contact': 'Contacts',
            'analysis': 'Analyses'
        }
        return worksheet_map.get(entity_type, 'Data')
    
    async def _get_or_create_worksheet(self, worksheet_name: str):
        """Get or create worksheet in Google Sheets"""
        try:
            # Try to get existing worksheet
            try:
                worksheet = self.sheets_service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{worksheet_name}!A1"
                ).execute()
                return worksheet
            except:
                pass
            
            # Create new worksheet if it doesn't exist
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': worksheet_name,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26
                        }
                    }
                }
            }]
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"✅ Created new worksheet: {worksheet_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating worksheet {worksheet_name}: {e}")
            return None
    
    def _prepare_data_for_sheets(self, entity_type: str, entity_data: Dict) -> List[str]:
        """Prepare entity data for Google Sheets format"""
        if entity_type == 'message':
            return [
                entity_data.get('id', ''),
                entity_data.get('message_id', ''),
                entity_data.get('chat_id', ''),
                entity_data.get('chat_title', ''),
                entity_data.get('user_id', ''),
                entity_data.get('username', ''),
                entity_data.get('first_name', ''),
                entity_data.get('last_name', ''),
                entity_data.get('message_text', ''),
                entity_data.get('message_type', ''),
                entity_data.get('timestamp', ''),
                entity_data.get('sentiment_score', 0),
                entity_data.get('keywords', ''),
                entity_data.get('is_duplicate', False),
                datetime.now().isoformat()
            ]
        elif entity_type == 'note':
            return [
                entity_data.get('id', ''),
                entity_data.get('text', ''),
                entity_data.get('timestamp', ''),
                entity_data.get('category', ''),
                entity_data.get('priority', ''),
                entity_data.get('tags', ''),
                entity_data.get('completed', False),
                datetime.now().isoformat()
            ]
        elif entity_type == 'contact':
            return [
                entity_data.get('user_id', ''),
                entity_data.get('username', ''),
                entity_data.get('name', ''),
                entity_data.get('message_count', 0),
                entity_data.get('lead_score', 0),
                entity_data.get('category', ''),
                entity_data.get('company', ''),
                entity_data.get('role', ''),
                entity_data.get('industry', ''),
                entity_data.get('last_message_date', ''),
                datetime.now().isoformat()
            ]
        elif entity_type == 'analysis':
            return [
                entity_data.get('chat_id', ''),
                entity_data.get('chat_title', ''),
                entity_data.get('sentiment_score', 0),
                entity_data.get('key_topics', ''),
                entity_data.get('business_opportunities', ''),
                entity_data.get('recommendations', ''),
                entity_data.get('message_count', 0),
                entity_data.get('participants', 0),
                entity_data.get('timestamp', ''),
                datetime.now().isoformat()
            ]
        else:
            return []
    
    async def _find_existing_row(self, worksheet, entity_id: str) -> Optional[int]:
        """Find existing row by entity ID"""
        try:
            if not entity_id:
                return None
            
            # Get all values from the worksheet
            values = worksheet.get('values', [])
            
            # Look for the entity ID in the first column
            for i, row in enumerate(values, 1):
                if row and row[0] == entity_id:
                    return i
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding existing row: {e}")
            return None
    
    async def get_connection(self):
        """Get database connection for async operations"""
        return self._get_connection()
    
    async def _update_sync_status(self, sync_id: str, success: bool, error: Optional[str] = None):
        """Update sync status in database"""
        conn = None
        try:
            conn = sqlite3.connect(self.sync_db_path)
            cursor = conn.cursor()
            
            status = 'synced' if success else 'failed'
            retry_count = 0 if success else 1
            
            cursor.execute('''
                UPDATE sync_status 
                SET sync_status = ?, last_sync_attempt = ?, sync_error = ?, 
                    retry_count = retry_count + ?, updated_at = ?
                WHERE id = ?
            ''', (status, datetime.now().isoformat(), error, retry_count, datetime.now().isoformat(), sync_id))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating sync status: {e}")
        finally:
            if conn:
                conn.close()
    
    async def _retry_failed_syncs(self):
        """Retry failed syncs with exponential backoff"""
        conn = None
        try:
            conn = sqlite3.connect(self.sync_db_path)
            cursor = conn.cursor()
            
            # Get failed syncs that haven't been retried too many times
            cursor.execute('''
                SELECT * FROM sync_status 
                WHERE sync_status = 'failed' AND retry_count < 5
                ORDER BY last_sync_attempt ASC
                LIMIT 10
            ''')
            
            failed_syncs = cursor.fetchall()
            for row in failed_syncs:
                sync_status = SyncStatus(
                    id=row[0], entity_type=row[1], entity_id=row[2],
                    local_hash=row[3], remote_hash=row[4], sync_status=row[5],
                    last_sync_attempt=datetime.fromisoformat(row[6]) if row[6] else None,
                    sync_error=row[7], retry_count=row[8]
                )
                
                # Add back to queue for retry
                self.sync_queue.put(sync_status)
            
        except Exception as e:
            logger.error(f"❌ Error retrying failed syncs: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get overall sync status"""
        conn = None
        try:
            conn = sqlite3.connect(self.sync_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT sync_status, COUNT(*) as count 
                FROM sync_status 
                GROUP BY sync_status
            ''')
            
            status_counts = dict(cursor.fetchall())
            
            return {
                'total_items': sum(status_counts.values()),
                'synced': status_counts.get('synced', 0),
                'pending': status_counts.get('pending', 0),
                'failed': status_counts.get('failed', 0),
                'google_sheets_enabled': self.google_sheets_enabled
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting sync status: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        if current_time - self.last_cache_cleanup > 300:  # 5 minutes
            expired_keys = [
                key for key, (_, timestamp) in self.cache.items()
                if current_time - timestamp > self.cache_ttl
            ]
            for key in expired_keys:
                del self.cache[key]
            self.last_cache_cleanup = current_time
    
    async def close(self):
        """Cleanup and close connections"""
        self.sync_worker_running = False
        
        # Close all connections in pool
        while not self.connection_pool.empty():
            try:
                conn = self.connection_pool.get_nowait()
                conn.close()
            except:
                pass
        
        logger.info("✅ Data Manager closed successfully")
    
    async def get_contacts(self, limit: int = None) -> List[Dict]:
        """Get contacts from messages with lead scoring"""
        try:
            query = """
                SELECT DISTINCT
                    user_id,
                    username,
                    first_name,
                    last_name,
                    COUNT(*) as message_count,
                    MAX(timestamp) as last_message_date,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(CASE WHEN sentiment_score > 0.5 THEN 1 END) as positive_messages,
                    COUNT(CASE WHEN sentiment_score < -0.5 THEN 1 END) as negative_messages
                FROM messages 
                WHERE user_id IS NOT NULL AND user_id != 0
                GROUP BY user_id, username, first_name, last_name
                ORDER BY message_count DESC, last_message_date DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            async with self.get_connection() as conn:
                cursor = await conn.execute(query)
                rows = await cursor.fetchall()
                
                contacts = []
                for row in rows:
                    contact = {
                        'user_id': row[0],
                        'username': row[1] or '',
                        'first_name': row[2] or '',
                        'last_name': row[3] or '',
                        'name': f"{row[2] or ''} {row[3] or ''}".strip() or f"User {row[0]}",
                        'message_count': row[4],
                        'last_message_date': row[5],
                        'avg_sentiment': row[6] or 0,
                        'positive_messages': row[7],
                        'negative_messages': row[8],
                        'category': self._categorize_contact(row[4], row[6] or 0),
                        'lead_score': self._calculate_lead_score(row[4], row[6] or 0, row[7], row[8]),
                        'company': self._extract_company_info(row[1] or ''),
                        'role': self._extract_role_info(row[1] or ''),
                        'industry': self._extract_industry_info(row[1] or '')
                    }
                    contacts.append(contact)
                
                return contacts
                
        except Exception as e:
            logger.error(f"❌ Error getting contacts: {e}")
            return []
    
    def _categorize_contact(self, message_count: int, avg_sentiment: float) -> str:
        """Categorize contact based on activity and sentiment"""
        if message_count > 50 and avg_sentiment > 0.3:
            return "High-Value Lead"
        elif message_count > 20 and avg_sentiment > 0:
            return "Active Contact"
        elif message_count > 10:
            return "Regular Contact"
        elif avg_sentiment > 0.5:
            return "Positive Contact"
        else:
            return "Contact"
    
    def _calculate_lead_score(self, message_count: int, avg_sentiment: float, 
                            positive_messages: int, negative_messages: int) -> float:
        """Calculate lead score based on engagement and sentiment"""
        # Base score from message count (0-0.4)
        message_score = min(message_count / 100, 0.4)
        
        # Sentiment score (0-0.3)
        sentiment_score = max(0, avg_sentiment) * 0.3
        
        # Engagement score (0-0.3)
        total_messages = positive_messages + negative_messages
        if total_messages > 0:
            engagement_score = (positive_messages / total_messages) * 0.3
        else:
            engagement_score = 0
        
        return min(message_score + sentiment_score + engagement_score, 1.0)
    
    def _extract_company_info(self, username: str) -> str:
        """Extract company information from username"""
        # Simple extraction - can be enhanced with AI
        if '@' in username:
            username = username.split('@')[1]
        
        # Common company indicators
        company_indicators = ['corp', 'inc', 'ltd', 'co', 'tech', 'ai', 'digital', 'media']
        for indicator in company_indicators:
            if indicator in username.lower():
                return username.title()
        
        return "N/A"
    
    def _extract_role_info(self, username: str) -> str:
        """Extract role information from username"""
        # Simple extraction - can be enhanced with AI
        role_indicators = {
            'ceo': 'CEO',
            'cto': 'CTO',
            'cfo': 'CFO',
            'founder': 'Founder',
            'cofounder': 'Co-Founder',
            'manager': 'Manager',
            'director': 'Director',
            'lead': 'Lead',
            'senior': 'Senior',
            'junior': 'Junior'
        }
        
        username_lower = username.lower()
        for indicator, role in role_indicators.items():
            if indicator in username_lower:
                return role
        
        return "N/A"
    
    def _extract_industry_info(self, username: str) -> str:
        """Extract industry information from username"""
        # Simple extraction - can be enhanced with AI
        industry_indicators = {
            'tech': 'Technology',
            'ai': 'Artificial Intelligence',
            'fintech': 'Financial Technology',
            'health': 'Healthcare',
            'edu': 'Education',
            'media': 'Media',
            'marketing': 'Marketing',
            'sales': 'Sales',
            'consulting': 'Consulting',
            'realestate': 'Real Estate'
        }
        
        username_lower = username.lower()
        for indicator, industry in industry_indicators.items():
            if indicator in username_lower:
                return industry
        
        return "N/A" 

    # Add missing methods that the bot is trying to use
    async def get_recent_messages(self, days: int = 7, chat_id: Optional[int] = None, limit: int = 1000) -> List[Dict]:
        """Get recent messages from specified days"""
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if chat_id:
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE chat_id = ? AND timestamp >= ? AND is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (chat_id, cutoff_date.isoformat(), limit))
            else:
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE timestamp >= ? AND is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (cutoff_date.isoformat(), limit))
            
            messages = []
            for row in cursor.fetchall():
                msg_dict = dict(row)
                msg_dict['keywords'] = self._deserialize_list(msg_dict.get('keywords', '[]'))
                messages.append(msg_dict)
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error getting recent messages: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_chat_list(self, limit: int = 50) -> List[Dict]:
        """Get list of chats with message counts"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    chat_title,
                    chat_id,
                    COUNT(*) as message_count,
                    COUNT(DISTINCT user_id) as participant_count,
                    MAX(timestamp) as last_message,
                    MIN(timestamp) as first_message
                FROM messages 
                WHERE is_duplicate = FALSE AND chat_title IS NOT NULL
                GROUP BY chat_id, chat_title
                ORDER BY message_count DESC
                LIMIT ?
            ''', (limit,))
            
            chats = []
            for row in cursor.fetchall():
                chats.append({
                    'title': row[0],
                    'chat_id': row[1],
                    'message_count': row[2],
                    'participant_count': row[3],
                    'last_message': row[4],
                    'first_message': row[5]
                })
            
            return chats
            
        except Exception as e:
            logger.error(f"❌ Error getting chat list: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_last_message_timestamp(self, chat_id: int) -> Optional[datetime]:
        """Get the timestamp of the last message in a chat"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT MAX(timestamp) FROM messages 
                WHERE chat_id = ? AND is_duplicate = FALSE
            ''', (chat_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                return datetime.fromisoformat(result[0])
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting last message timestamp: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def store_message(self, message_data: Dict[str, Any]) -> bool:
        """Store a message (synchronous version for compatibility)"""
        try:
            # Convert timestamp if it's a datetime object
            if isinstance(message_data.get('timestamp'), datetime):
                message_data['timestamp'] = message_data['timestamp'].isoformat()
            
            # Generate content hash
            content = f"{message_data.get('message_text', '')}{message_data.get('timestamp', '')}"
            content_hash = self._generate_hash(content)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create message ID
            message_id = f"msg_{message_data.get('message_id', 0)}_{message_data.get('chat_id', 0)}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO messages (
                    id, message_id, chat_id, chat_title, user_id, username, first_name, last_name,
                    message_text, message_type, timestamp, content_hash, sentiment_score,
                    keywords, is_duplicate, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                message_data.get('message_id', 0),
                message_data.get('chat_id', 0),
                message_data.get('chat_title', ''),
                message_data.get('user_id', 0),
                message_data.get('username', ''),
                message_data.get('first_name', ''),
                message_data.get('last_name', ''),
                message_data.get('message_text', ''),
                message_data.get('message_type', 'text'),
                message_data.get('timestamp', ''),
                content_hash,
                0.0,  # sentiment_score
                '[]',  # keywords
                False,  # is_duplicate
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self._return_connection(conn)
            
            # Also store/update contact information
            self._store_contact_from_message(message_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing message: {e}")
            return False
    
    def _store_contact_from_message(self, message_data: Dict[str, Any]):
        """Extract and store contact information from message"""
        try:
            user_id = message_data.get('user_id')
            if not user_id or user_id == 0:
                return
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if contact exists
            cursor.execute('SELECT id FROM contacts WHERE id = ?', (str(user_id),))
            exists = cursor.fetchone()
            
            name = f"{message_data.get('first_name', '')} {message_data.get('last_name', '')}".strip()
            if not name:
                name = message_data.get('username', f'User {user_id}')
            
            if exists:
                # Update existing contact
                cursor.execute('''
                    UPDATE contacts SET
                        name = ?,
                        username = ?,
                        message_count = message_count + 1,
                        last_message_date = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (
                    name,
                    message_data.get('username', ''),
                    message_data.get('timestamp', ''),
                    datetime.now().isoformat(),
                    str(user_id)
                ))
            else:
                # Create new contact
                cursor.execute('''
                    INSERT INTO contacts (
                        id, name, username, category, priority, message_count,
                        last_message_date, lead_score, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(user_id),
                    name,
                    message_data.get('username', ''),
                    'contact',
                    1,
                    1,
                    message_data.get('timestamp', ''),
                    0.0,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            self._return_connection(conn)
            
        except Exception as e:
            logger.error(f"❌ Error storing contact: {e}") 