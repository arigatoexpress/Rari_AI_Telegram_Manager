#!/usr/bin/env python3
"""
Async Data Manager - Optimized for Performance
=============================================
Fully asynchronous data management with:
- Connection pooling for database operations
- Batch processing for bulk operations
- Differential sync with change tracking
- Enhanced deduplication with content hashing
- Smart caching for performance
- Optimized for sporadic usage patterns
"""

import asyncio
import aiosqlite
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator, Set
from dataclasses import dataclass, asdict, field
from contextlib import asynccontextmanager
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ChangeRecord:
    """Track changes for differential sync"""
    id: str
    entity_type: str  # 'message', 'contact', 'note', 'interaction'
    entity_id: str
    operation: str  # 'insert', 'update', 'delete'
    content_hash: str
    change_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    synced: bool = False
    retry_count: int = 0

@dataclass
class BatchOperation:
    """Batch operation for efficient bulk processing"""
    operation_type: str  # 'insert', 'update', 'delete'
    table_name: str
    data: List[Dict[str, Any]]
    conflict_resolution: str = 'replace'  # 'ignore', 'replace', 'abort'

@dataclass
class CacheEntry:
    """Cache entry with TTL and metadata"""
    data: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

class AsyncDataManager:
    """High-performance async data manager"""
    
    def __init__(self, data_dir: str = "data", max_connections: int = 10):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Database paths
        self.db_path = self.data_dir / "telegram_manager.db"
        self.changes_db_path = self.data_dir / "changes_tracking.db"
        
        # Connection management
        self.max_connections = max_connections
        self.connection_pool: List[aiosqlite.Connection] = []
        self.available_connections = asyncio.Queue(maxsize=max_connections)
        self.pool_lock = asyncio.Lock()
        
        # Change tracking
        self.pending_changes: Dict[str, ChangeRecord] = {}
        self.change_batch_size = 100
        self.last_sync_check = time.time()
        
        # Caching system
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        self.cache_max_size = 1000
        self.cache_cleanup_interval = 300  # 5 minutes
        self.last_cache_cleanup = time.time()
        
        # Deduplication tracking
        self.content_hashes: Set[str] = set()
        self.duplicate_tracking = defaultdict(list)
        
        # Performance metrics
        self.metrics = {
            'operations_count': 0,
            'batch_operations': 0,
            'cache_efficiency': 0.0,
            'avg_operation_time': 0.0,
            'duplicate_prevention_count': 0
        }
        
        self._initialized = False
        
    async def initialize(self):
        """Initialize the async data manager"""
        if self._initialized:
            return
            
        try:
            # Initialize connection pool
            await self._init_connection_pool()
            
            # Initialize database schema
            await self._init_database_schema()
            
            # Initialize change tracking
            await self._init_change_tracking()
            
            # Load content hashes for deduplication
            await self._load_content_hashes()
            
            # Start background tasks
            asyncio.create_task(self._periodic_sync())
            asyncio.create_task(self._periodic_cache_cleanup())
            asyncio.create_task(self._metrics_reporter())
            
            self._initialized = True
            logger.info("✅ Async Data Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Async Data Manager: {e}")
            raise
    
    async def _init_connection_pool(self):
        """Initialize database connection pool"""
        async with self.pool_lock:
            for _ in range(self.max_connections):
                conn = await aiosqlite.connect(self.db_path)
                await conn.execute('PRAGMA journal_mode=WAL')
                await conn.execute('PRAGMA synchronous=NORMAL')
                await conn.execute('PRAGMA cache_size=10000')
                await conn.execute('PRAGMA temp_store=MEMORY')
                await conn.execute('PRAGMA foreign_keys=ON')
                
                self.connection_pool.append(conn)
                await self.available_connections.put(conn)
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool with proper cleanup"""
        conn = await self.available_connections.get()
        try:
            yield conn
        finally:
            await self.available_connections.put(conn)
    
    async def _init_database_schema(self):
        """Initialize optimized database schema"""
        async with self.get_connection() as conn:
            # Enhanced messages table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    message_id INTEGER,
                    chat_id INTEGER,
                    chat_title TEXT,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    message_text TEXT,
                    message_type TEXT,
                    timestamp DATETIME,
                    content_hash TEXT UNIQUE,
                    sentiment_score REAL DEFAULT 0.0,
                    keywords TEXT,
                    is_duplicate BOOLEAN DEFAULT FALSE,
                    duplicate_of TEXT,
                    processing_status TEXT DEFAULT 'pending',
                    ai_analyzed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    change_hash TEXT
                )
            ''')
            
            # Create comprehensive indexes (only for existing columns)
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_messages_content_hash ON messages(content_hash)',
                'CREATE INDEX IF NOT EXISTS idx_messages_chat_user ON messages(chat_id, user_id)',
                'CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)'
            ]
            
            for index_sql in indexes:
                await conn.execute(index_sql)
            
            # Contacts table already exists - skip creation
            
            await conn.commit()
    
    async def _init_change_tracking(self):
        """Initialize change tracking database"""
        changes_conn = await aiosqlite.connect(self.changes_db_path)
        
        await changes_conn.execute('''
            CREATE TABLE IF NOT EXISTS change_log (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                change_data TEXT,
                timestamp DATETIME NOT NULL,
                synced BOOLEAN DEFAULT FALSE,
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await changes_conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_change_log_synced ON change_log(synced)
        ''')
        
        await changes_conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_change_log_entity ON change_log(entity_type, entity_id)
        ''')
        
        await changes_conn.commit()
        await changes_conn.close()
    
    async def _load_content_hashes(self):
        """Load existing content hashes for deduplication"""
        async with self.get_connection() as conn:
            async with conn.execute('SELECT content_hash FROM messages WHERE content_hash IS NOT NULL') as cursor:
                async for row in cursor:
                    self.content_hashes.add(row[0])
            
            # Skip loading content hashes from contacts table as it doesn't have this column
        
        logger.info(f"📚 Loaded {len(self.content_hashes)} content hashes for deduplication")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate content hash for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_change_hash(self, data: Dict[str, Any]) -> str:
        """Generate change hash for differential sync"""
        # Create a stable hash from the data
        stable_data = {k: v for k, v in sorted(data.items()) if v is not None}
        content = json.dumps(stable_data, sort_keys=True, default=str)
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def _track_change(self, entity_type: str, entity_id: str, operation: str, data: Dict[str, Any]):
        """Track changes for differential sync"""
        change_id = str(uuid.uuid4())
        content_hash = self._generate_content_hash(json.dumps(data, sort_keys=True, default=str))
        
        change = ChangeRecord(
            id=change_id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            content_hash=content_hash,
            change_data=data,
            timestamp=datetime.now()
        )
        
        self.pending_changes[change_id] = change
        
        # Batch persist changes
        if len(self.pending_changes) >= self.change_batch_size:
            await self._persist_changes()
    
    async def _persist_changes(self):
        """Persist pending changes to disk"""
        if not self.pending_changes:
            return
        
        changes_conn = await aiosqlite.connect(self.changes_db_path)
        
        try:
            changes_to_persist = list(self.pending_changes.values())
            
            batch_data = [
                (
                    change.id,
                    change.entity_type,
                    change.entity_id,
                    change.operation,
                    change.content_hash,
                    json.dumps(change.change_data, default=str),
                    change.timestamp.isoformat(),
                    change.synced,
                    change.retry_count
                )
                for change in changes_to_persist
            ]
            
            await changes_conn.executemany('''
                INSERT OR REPLACE INTO change_log 
                (id, entity_type, entity_id, operation, content_hash, change_data, timestamp, synced, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch_data)
            
            await changes_conn.commit()
            self.pending_changes.clear()
            
            logger.info(f"💾 Persisted {len(batch_data)} changes to disk")
            
        except Exception as e:
            logger.error(f"❌ Failed to persist changes: {e}")
        finally:
            await changes_conn.close()
    
    async def add_message_batch(self, messages: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
        """Add multiple messages in an optimized batch operation"""
        start_time = time.time()
        added_count = 0
        duplicate_count = 0
        errors = []
        
        # Pre-process messages for deduplication
        processed_messages = []
        seen_hashes = set()
        
        for msg_data in messages:
            try:
                # Generate content hash
                content = f"{msg_data.get('message_text', '')}{msg_data.get('timestamp', '')}"
                content_hash = self._generate_content_hash(content)
                
                # Check for duplicates
                if content_hash in self.content_hashes or content_hash in seen_hashes:
                    duplicate_count += 1
                    self.metrics['duplicate_prevention_count'] += 1
                    continue
                
                seen_hashes.add(content_hash)
                self.content_hashes.add(content_hash)
                
                # Prepare message data
                message_id = f"msg_{msg_data.get('message_id', 0)}_{msg_data.get('chat_id', 0)}"
                change_hash = self._generate_change_hash(msg_data)
                
                processed_msg = {
                    'id': message_id,
                    'message_id': msg_data.get('message_id', 0),
                    'chat_id': msg_data.get('chat_id', 0),
                    'chat_title': msg_data.get('chat_title', ''),
                    'user_id': msg_data.get('user_id', 0),
                    'username': msg_data.get('username', ''),
                    'first_name': msg_data.get('first_name', ''),
                    'last_name': msg_data.get('last_name', ''),
                    'message_text': msg_data.get('message_text', ''),
                    'message_type': msg_data.get('message_type', 'text'),
                    'timestamp': msg_data.get('timestamp', ''),
                    'content_hash': content_hash,
                    'sentiment_score': 0.0,
                    'keywords': '[]',
                    'is_duplicate': False,
                    'updated_at': datetime.now().isoformat()
                }
                
                processed_messages.append(processed_msg)
                
                # Track change
                await self._track_change('message', message_id, 'insert', processed_msg)
                
            except Exception as e:
                errors.append(f"Message processing error: {e}")
        
        # Batch insert processed messages
        if processed_messages:
            try:
                async with self.get_connection() as conn:
                    await conn.executemany('''
                        INSERT OR REPLACE INTO messages (
                            id, message_id, chat_id, chat_title, user_id, username, first_name, last_name,
                            message_text, message_type, timestamp, content_hash, sentiment_score,
                            keywords, is_duplicate, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', [
                        (
                            msg['id'], msg['message_id'], msg['chat_id'], msg['chat_title'],
                            msg['user_id'], msg['username'], msg['first_name'], msg['last_name'],
                            msg['message_text'], msg['message_type'], msg['timestamp'],
                            msg['content_hash'], msg['sentiment_score'], msg['keywords'],
                            msg['is_duplicate'], msg['updated_at']
                        )
                        for msg in processed_messages
                    ])
                    
                    await conn.commit()
                    added_count = len(processed_messages)
                    
            except Exception as e:
                errors.append(f"Batch insert error: {e}")
        
        # Update metrics
        operation_time = time.time() - start_time
        self.metrics['operations_count'] += 1
        self.metrics['batch_operations'] += 1
        self._update_avg_operation_time(operation_time)
        
        logger.info(f"📦 Batch processed {len(messages)} messages: {added_count} added, {duplicate_count} duplicates, {len(errors)} errors in {operation_time:.2f}s")
        
        return added_count, duplicate_count, errors
    
    async def get_messages_with_cache(self, chat_id: Optional[int] = None, limit: int = 100, 
                                     offset: int = 0, use_cache: bool = True) -> List[Dict]:
        """Get messages with intelligent caching"""
        cache_key = f"messages_{chat_id}_{limit}_{offset}"
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry.created_at < entry.ttl:
                entry.access_count += 1
                entry.last_accessed = time.time()
                self.cache_stats['hits'] += 1
                return entry.data
            else:
                # Cache expired
                del self.cache[cache_key]
        
        # Cache miss - fetch from database
        self.cache_stats['misses'] += 1
        
        async with self.get_connection() as conn:
            if chat_id:
                query = '''
                    SELECT * FROM messages 
                    WHERE chat_id = ? AND is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                '''
                params = (chat_id, limit, offset)
            else:
                query = '''
                    SELECT * FROM messages 
                    WHERE is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                '''
                params = (limit, offset)
            
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                messages = []
                for row in rows:
                    msg_dict = dict(zip(columns, row))
                    msg_dict['keywords'] = json.loads(msg_dict.get('keywords', '[]'))
                    messages.append(msg_dict)
        
        # Cache the result
        if use_cache:
            self.cache[cache_key] = CacheEntry(
                data=messages,
                created_at=time.time(),
                ttl=300,  # 5 minutes
                access_count=1
            )
            
            # Clean cache if too large
            await self._cleanup_cache_if_needed()
        
        return messages
    
    async def get_recent_messages(self, days: int = 7, chat_id: Optional[int] = None, 
                                 limit: int = 1000, use_cache: bool = True) -> List[Dict]:
        """Get recent messages with caching and optimization"""
        cache_key = f"recent_messages_{days}_{chat_id}_{limit}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry.created_at < entry.ttl:
                entry.access_count += 1
                entry.last_accessed = time.time()
                self.cache_stats['hits'] += 1
                return entry.data
            else:
                del self.cache[cache_key]
        
        self.cache_stats['misses'] += 1
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        async with self.get_connection() as conn:
            if chat_id:
                query = '''
                    SELECT * FROM messages 
                    WHERE chat_id = ? AND timestamp >= ? AND is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                params = (chat_id, cutoff_date.isoformat(), limit)
            else:
                query = '''
                    SELECT * FROM messages 
                    WHERE timestamp >= ? AND is_duplicate = FALSE
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                params = (cutoff_date.isoformat(), limit)
            
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                messages = []
                for row in rows:
                    msg_dict = dict(zip(columns, row))
                    msg_dict['keywords'] = json.loads(msg_dict.get('keywords', '[]'))
                    messages.append(msg_dict)
        
        # Cache the result
        if use_cache:
            self.cache[cache_key] = CacheEntry(
                data=messages,
                created_at=time.time(),
                ttl=120,  # 2 minutes for recent data
                access_count=1
            )
        
        return messages
    
    async def get_unsynced_changes(self, limit: int = 100) -> List[ChangeRecord]:
        """Get unsynced changes for differential backup"""
        changes_conn = await aiosqlite.connect(self.changes_db_path)
        
        try:
            async with changes_conn.execute('''
                SELECT * FROM change_log 
                WHERE synced = FALSE 
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                changes = []
                for row in rows:
                    data = dict(zip(columns, row))
                    change = ChangeRecord(
                        id=data['id'],
                        entity_type=data['entity_type'],
                        entity_id=data['entity_id'],
                        operation=data['operation'],
                        content_hash=data['content_hash'],
                        change_data=json.loads(data['change_data']),
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        synced=data['synced'],
                        retry_count=data['retry_count']
                    )
                    changes.append(change)
                
                return changes
                
        finally:
            await changes_conn.close()
    
    async def mark_changes_synced(self, change_ids: List[str]):
        """Mark changes as synced"""
        if not change_ids:
            return
            
        changes_conn = await aiosqlite.connect(self.changes_db_path)
        
        try:
            await changes_conn.executemany(
                'UPDATE change_log SET synced = TRUE WHERE id = ?',
                [(change_id,) for change_id in change_ids]
            )
            await changes_conn.commit()
            
        finally:
            await changes_conn.close()
    
    async def _cleanup_cache_if_needed(self):
        """Clean up cache if it's too large"""
        if len(self.cache) > self.cache_max_size:
            # Remove least recently used entries
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            to_remove = len(self.cache) - int(self.cache_max_size * 0.8)
            for key, _ in sorted_entries[:to_remove]:
                del self.cache[key]
                self.cache_stats['evictions'] += 1
    
    async def _periodic_cache_cleanup(self):
        """Periodic cache cleanup task"""
        while True:
            try:
                await asyncio.sleep(self.cache_cleanup_interval)
                
                current_time = time.time()
                expired_keys = []
                
                for key, entry in self.cache.items():
                    if current_time - entry.created_at > entry.ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                    self.cache_stats['evictions'] += 1
                
                if expired_keys:
                    logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
                
                # Update cache efficiency
                total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
                if total_requests > 0:
                    self.metrics['cache_efficiency'] = self.cache_stats['hits'] / total_requests
                
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
    
    async def _periodic_sync(self):
        """Periodic sync of pending changes"""
        while True:
            try:
                await asyncio.sleep(30)  # Sync every 30 seconds
                
                # Persist any pending changes
                if self.pending_changes:
                    await self._persist_changes()
                
                # Check for sync operations (can be extended for remote sync)
                current_time = time.time()
                if current_time - self.last_sync_check > 300:  # 5 minutes
                    await self._check_sync_health()
                    self.last_sync_check = current_time
                
            except Exception as e:
                logger.error(f"❌ Periodic sync error: {e}")
    
    async def _check_sync_health(self):
        """Check sync system health"""
        unsynced = await self.get_unsynced_changes(limit=1)
        changes_conn = await aiosqlite.connect(self.changes_db_path)
        
        try:
            async with changes_conn.execute('SELECT COUNT(*) FROM change_log WHERE synced = FALSE') as cursor:
                row = await cursor.fetchone()
                unsynced_count = row[0] if row else 0
            
            if unsynced_count > 1000:
                logger.warning(f"⚠️ {unsynced_count} unsynced changes - consider running full sync")
            elif unsynced_count > 0:
                logger.info(f"📊 {unsynced_count} changes pending sync")
                
        finally:
            await changes_conn.close()
    
    async def _metrics_reporter(self):
        """Periodic metrics reporting"""
        while True:
            try:
                await asyncio.sleep(600)  # Report every 10 minutes
                
                logger.info(f"📊 Performance Metrics:")
                logger.info(f"   Operations: {self.metrics['operations_count']}")
                logger.info(f"   Batch Operations: {self.metrics['batch_operations']}")
                logger.info(f"   Cache Efficiency: {self.metrics['cache_efficiency']:.2%}")
                logger.info(f"   Avg Operation Time: {self.metrics['avg_operation_time']:.3f}s")
                logger.info(f"   Duplicates Prevented: {self.metrics['duplicate_prevention_count']}")
                logger.info(f"   Cache Stats: {self.cache_stats}")
                
            except Exception as e:
                logger.error(f"❌ Metrics reporting error: {e}")
    
    def _update_avg_operation_time(self, operation_time: float):
        """Update average operation time"""
        current_avg = self.metrics['avg_operation_time']
        count = self.metrics['operations_count']
        
        if count == 1:
            self.metrics['avg_operation_time'] = operation_time
        else:
            self.metrics['avg_operation_time'] = ((current_avg * (count - 1)) + operation_time) / count
    
    async def close(self):
        """Cleanup and close all connections"""
        try:
            # Persist any pending changes
            await self._persist_changes()
            
            # Close all connections
            async with self.pool_lock:
                for conn in self.connection_pool:
                    await conn.close()
                self.connection_pool.clear()
            
            logger.info("✅ Async Data Manager closed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error closing Async Data Manager: {e}")
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        unsynced_count = len(await self.get_unsynced_changes(limit=10000))
        
        return {
            'metrics': self.metrics.copy(),
            'cache_stats': self.cache_stats.copy(),
            'cache_size': len(self.cache),
            'pending_changes': len(self.pending_changes),
            'unsynced_changes': unsynced_count,
            'content_hashes_loaded': len(self.content_hashes),
            'connection_pool_size': len(self.connection_pool),
            'available_connections': self.available_connections.qsize()
        }

# Global instance for easy access
async_data_manager = None

async def get_async_data_manager() -> AsyncDataManager:
    """Get the global async data manager instance"""
    global async_data_manager
    if async_data_manager is None:
        async_data_manager = AsyncDataManager()
        await async_data_manager.initialize()
    return async_data_manager 