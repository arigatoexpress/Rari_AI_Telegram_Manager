#!/usr/bin/env python3
"""
Smart Sync & Deduplication System
=================================
Coordinates all async components and handles intelligent deduplication:
- Cross-data-type deduplication
- Smart sync coordination
- Conflict resolution
- Performance optimization for sporadic usage
- Intelligent merging strategies
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

@dataclass
class DeduplicationResult:
    """Result of deduplication operation"""
    total_processed: int
    duplicates_found: int
    duplicates_merged: int
    conflicts_resolved: int
    space_saved_bytes: int
    processing_time_seconds: float

@dataclass
class SyncOperation:
    """Represents a sync operation"""
    operation_id: str
    operation_type: str  # 'full_sync', 'differential_sync', 'dedup', 'cleanup'
    status: str  # 'pending', 'running', 'completed', 'failed'
    priority: int = 5  # 1-10, higher is more important
    scheduled_time: Optional[datetime] = None
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class SmartSyncManager:
    """Coordinates all sync operations and deduplication"""
    
    def __init__(self):
        # Component references
        self.data_manager = None
        self.backup_manager = None
        
        # Operation scheduling
        self.scheduled_operations: Dict[str, SyncOperation] = {}
        self.operation_queue = asyncio.PriorityQueue()
        self.running_operations: Set[str] = set()
        self.max_concurrent_operations = 3
        
        # Deduplication state
        self.content_fingerprints: Dict[str, Set[str]] = defaultdict(set)
        self.similarity_threshold = 0.85
        self.dedup_batch_size = 1000
        
        # Performance tracking
        self.performance_metrics = {
            'operations_completed': 0,
            'total_duplicates_removed': 0,
            'total_space_saved_mb': 0.0,
            'avg_operation_time': 0.0,
            'last_full_sync': None,
            'last_deduplication': None
        }
        
        # Configuration
        self.auto_sync_enabled = True
        self.auto_sync_interval = 300  # 5 minutes
        self.auto_dedup_enabled = True
        self.auto_dedup_interval = 3600  # 1 hour
        self.auto_backup_enabled = True
        self.auto_backup_interval = 1800  # 30 minutes
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize the smart sync manager"""
        if self._initialized:
            return
        
        try:
            # Get component references
            from .async_data_manager import get_async_data_manager
            from .differential_backup import get_backup_manager
            
            self.data_manager = await get_async_data_manager()
            self.backup_manager = await get_backup_manager()
            
            # Load existing fingerprints
            await self._load_content_fingerprints()
            
            # Start background tasks
            asyncio.create_task(self._operation_scheduler())
            asyncio.create_task(self._operation_processor())
            # Note: _auto_sync_coordinator method needs to be implemented
            
            self._initialized = True
            logger.info("✅ Smart Sync Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Smart Sync Manager: {e}")
            raise
    
    async def _load_content_fingerprints(self):
        """Load content fingerprints for cross-data-type deduplication"""
        try:
            # Load message fingerprints
            async with self.data_manager.get_connection() as conn:
                async with conn.execute('''
                    SELECT content_hash, GROUP_CONCAT(id) as ids
                    FROM messages 
                    WHERE content_hash IS NOT NULL 
                    GROUP BY content_hash
                ''') as cursor:
                    async for row in cursor:
                        content_hash, ids = row
                        self.content_fingerprints['messages'].add(content_hash)
                
                # Skip contact fingerprints as contacts table doesn't have content_hash column
            
            total_fingerprints = sum(len(fps) for fps in self.content_fingerprints.values())
            logger.info(f"📚 Loaded {total_fingerprints} content fingerprints")
            
        except Exception as e:
            logger.error(f"❌ Failed to load content fingerprints: {e}")
    
    def schedule_operation(self, operation: SyncOperation):
        """Schedule a sync operation"""
        self.scheduled_operations[operation.operation_id] = operation
        
        # Add to priority queue (negative priority for max-heap behavior)
        self.operation_queue.put_nowait((-operation.priority, operation.operation_id))
        
        logger.info(f"📅 Scheduled operation: {operation.operation_type} (ID: {operation.operation_id})")
    
    async def _operation_scheduler(self):
        """Background task for scheduling automatic operations"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.now()
                
                # Schedule auto-sync operations
                if self.auto_sync_enabled:
                    last_sync = self.performance_metrics.get('last_full_sync')
                    if not last_sync or (current_time - last_sync).total_seconds() > self.auto_sync_interval:
                        await self._schedule_auto_sync()
            
                # Schedule auto-deduplication
                if self.auto_dedup_enabled:
                    last_dedup = self.performance_metrics.get('last_deduplication')
                    if not last_dedup or (current_time - last_dedup).total_seconds() > self.auto_dedup_interval:
                        await self._schedule_auto_deduplication()
                
                # Schedule auto-backup
                if self.auto_backup_enabled:
                    await self._schedule_auto_backup()
            
        except Exception as e:
                logger.error(f"❌ Operation scheduler error: {e}")
    
    async def _schedule_auto_sync(self):
        """Schedule automatic sync operation"""
        operation_id = f"auto_sync_{int(time.time())}"
        
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type="auto_sync",
            status="pending",
            priority=3,
            scheduled_time=datetime.now()
        )
        
        self.schedule_operation(operation)
    
    async def _schedule_auto_deduplication(self):
        """Schedule automatic deduplication"""
        operation_id = f"auto_dedup_{int(time.time())}"
        
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type="deduplication",
            status="pending",
            priority=2,
            scheduled_time=datetime.now()
        )
        
        self.schedule_operation(operation)
    
    async def _schedule_auto_backup(self):
        """Schedule automatic backup if needed"""
        try:
            needs_backup, backup_type = await self.backup_manager.needs_backup()
            
            if needs_backup:
                operation_id = f"auto_backup_{int(time.time())}"
                
                operation = SyncOperation(
                    operation_id=operation_id,
                    operation_type="backup",
                    status="pending",
                    priority=4,
                    scheduled_time=datetime.now(),
                    metadata={"backup_type": backup_type}
                )
                
                self.schedule_operation(operation)
            
        except Exception as e:
            logger.error(f"❌ Auto-backup scheduling error: {e}")
    
    async def _operation_processor(self):
        """Background task for processing operations"""
        while True:
            try:
                # Wait for operation or timeout
                try:
                    priority, operation_id = await asyncio.wait_for(
                        self.operation_queue.get(), timeout=30
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check if we can run more operations
                if len(self.running_operations) >= self.max_concurrent_operations:
                    # Put back in queue and wait
                    self.operation_queue.put_nowait((priority, operation_id))
                    await asyncio.sleep(5)
                    continue
                
                # Get operation details
                if operation_id not in self.scheduled_operations:
                    continue
                
                operation = self.scheduled_operations[operation_id]
                
                # Run operation
                self.running_operations.add(operation_id)
                asyncio.create_task(self._execute_operation(operation))
                
            except Exception as e:
                logger.error(f"❌ Operation processor error: {e}")
    
    async def _execute_operation(self, operation: SyncOperation):
        """Execute a sync operation"""
        start_time = datetime.now()
        operation.started_time = start_time
        operation.status = "running"
        
        try:
            logger.info(f"🚀 Executing operation: {operation.operation_type}")
            
            if operation.operation_type == "auto_sync":
                await self._execute_auto_sync(operation)
            elif operation.operation_type == "deduplication":
                await self._execute_deduplication(operation)
            elif operation.operation_type == "backup":
                await self._execute_backup(operation)
            elif operation.operation_type == "full_sync":
                await self._execute_full_sync(operation)
            else:
                logger.warning(f"⚠️ Unknown operation type: {operation.operation_type}")
            
            operation.status = "completed"
            operation.progress_percentage = 100.0
                
        except Exception as e:
            operation.status = "failed"
            operation.error_message = str(e)
            logger.error(f"❌ Operation {operation.operation_id} failed: {e}")
        
        finally:
            operation.completed_time = datetime.now()
            self.running_operations.discard(operation.operation_id)
            
            # Update performance metrics
            duration = (operation.completed_time - start_time).total_seconds()
            self._update_performance_metrics(operation, duration)
            
            logger.info(f"✅ Operation completed: {operation.operation_type} in {duration:.2f}s")
    
    async def _execute_auto_sync(self, operation: SyncOperation):
        """Execute automatic sync operation"""
        # Sync pending changes
        changes = await self.data_manager.get_unsynced_changes(limit=1000)
        
        if changes:
            logger.info(f"🔄 Syncing {len(changes)} pending changes")
            
            # Process changes in batches
            batch_size = 100
            for i in range(0, len(changes), batch_size):
                batch = changes[i:i + batch_size]
                await self._process_change_batch(batch)
                
                # Update progress
                progress = ((i + len(batch)) / len(changes)) * 100
                operation.progress_percentage = progress
        
        self.performance_metrics['last_full_sync'] = datetime.now()
    
    async def _execute_deduplication(self, operation: SyncOperation):
        """Execute deduplication operation"""
        result = await self.deduplicate_all_data()
        
        operation.metadata['deduplication_result'] = {
            'duplicates_found': result.duplicates_found,
            'duplicates_merged': result.duplicates_merged,
            'space_saved_mb': result.space_saved_bytes / (1024 * 1024)
        }
        
        self.performance_metrics['last_deduplication'] = datetime.now()
        self.performance_metrics['total_duplicates_removed'] += result.duplicates_merged
        self.performance_metrics['total_space_saved_mb'] += result.space_saved_bytes / (1024 * 1024)
    
    async def _execute_backup(self, operation: SyncOperation):
        """Execute backup operation"""
        backup_type = operation.metadata.get('backup_type', 'differential')
        force_full = backup_type == 'full'
        
        metadata = await self.backup_manager.create_backup(force_full=force_full)
        
        if metadata:
            operation.metadata['backup_metadata'] = {
                'backup_id': metadata.backup_id,
                'backup_size_mb': metadata.backup_size / (1024 * 1024),
                'changes_count': metadata.changes_count
        }
    
    async def _execute_full_sync(self, operation: SyncOperation):
        """Execute full sync operation"""
        # This would implement full synchronization with external systems
        logger.info("🔄 Full sync operation - implement as needed")
    
    async def _process_change_batch(self, changes):
        """Process a batch of changes"""
        # Group changes by type for efficient processing
        changes_by_type = defaultdict(list)
        for change in changes:
            changes_by_type[change.entity_type].append(change)
        
        # Process each type
        for entity_type, type_changes in changes_by_type.items():
            if entity_type == "message":
                await self._process_message_changes(type_changes)
            elif entity_type == "contact":
                await self._process_contact_changes(type_changes)
        
        # Mark as synced
        change_ids = [change.id for change in changes]
        await self.data_manager.mark_changes_synced(change_ids)
    
    async def _process_message_changes(self, changes):
        """Process message changes"""
        # Apply deduplication during sync
        for change in changes:
            content_hash = change.content_hash
            
            if content_hash in self.content_fingerprints['messages']:
                # Potential duplicate detected
                await self._handle_duplicate_message(change)
            else:
                self.content_fingerprints['messages'].add(content_hash)
    
    async def _process_contact_changes(self, changes):
        """Process contact changes"""
        for change in changes:
            content_hash = change.content_hash
            
            if content_hash in self.content_fingerprints['contacts']:
                await self._handle_duplicate_contact(change)
            else:
                self.content_fingerprints['contacts'].add(content_hash)
    
    async def _handle_duplicate_message(self, change):
        """Handle duplicate message during sync"""
        # Mark as duplicate and reference original
        async with self.data_manager.get_connection() as conn:
            # Find original message
            async with conn.execute(
                'SELECT id FROM messages WHERE content_hash = ? AND is_duplicate = FALSE LIMIT 1',
                (change.content_hash,)
            ) as cursor:
                original = await cursor.fetchone()
                
                if original:
                    # Update the new message as duplicate
                    await conn.execute('''
                        UPDATE messages 
                        SET is_duplicate = TRUE, duplicate_of = ?
                        WHERE id = ?
                    ''', (original[0], change.entity_id))
                    
                    await conn.commit()
    
    async def _handle_duplicate_contact(self, change):
        """Handle duplicate contact during sync"""
        # Implement contact merging logic
        logger.info(f"🔄 Merging duplicate contact: {change.entity_id}")
    
    async def deduplicate_all_data(self) -> DeduplicationResult:
        """Perform comprehensive deduplication across all data types"""
        start_time = time.time()
        total_processed = 0
        duplicates_found = 0
        duplicates_merged = 0
        conflicts_resolved = 0
        space_saved = 0
        
        try:
            # Deduplicate messages
            msg_result = await self._deduplicate_messages()
            total_processed += msg_result['processed']
            duplicates_found += msg_result['duplicates_found']
            duplicates_merged += msg_result['duplicates_merged']
            space_saved += msg_result['space_saved']
            
            # Deduplicate contacts
            contact_result = await self._deduplicate_contacts()
            total_processed += contact_result['processed']
            duplicates_found += contact_result['duplicates_found']
            duplicates_merged += contact_result['duplicates_merged']
            space_saved += contact_result['space_saved']
            
            # Cross-type deduplication (e.g., contact info from messages)
            cross_result = await self._deduplicate_cross_type()
            conflicts_resolved += cross_result['conflicts_resolved']
            
            processing_time = time.time() - start_time
            
            logger.info(f"🎯 Deduplication completed: {duplicates_merged} duplicates merged, {space_saved/1024/1024:.2f}MB saved")
            
            return DeduplicationResult(
                total_processed=total_processed,
                duplicates_found=duplicates_found,
                duplicates_merged=duplicates_merged,
                conflicts_resolved=conflicts_resolved,
                space_saved_bytes=space_saved,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Deduplication failed: {e}")
            raise
    
    async def _deduplicate_messages(self) -> Dict[str, int]:
        """Deduplicate messages based on content similarity"""
        processed = 0
        duplicates_found = 0
        duplicates_merged = 0
        space_saved = 0
        
        async with self.data_manager.get_connection() as conn:
            # Find messages with same content hash
            async with conn.execute('''
                SELECT content_hash, GROUP_CONCAT(id) as ids, COUNT(*) as count
                FROM messages 
                WHERE content_hash IS NOT NULL AND is_duplicate = FALSE
                GROUP BY content_hash 
                HAVING count > 1
            ''') as cursor:
                async for row in cursor:
                    content_hash, ids_str, count = row
                    message_ids = ids_str.split(',')
                    
                    if len(message_ids) > 1:
                        # Keep the first message, mark others as duplicates
                        original_id = message_ids[0]
                        duplicate_ids = message_ids[1:]
                        
                        for dup_id in duplicate_ids:
                            await conn.execute('''
                                UPDATE messages 
                                SET is_duplicate = TRUE, duplicate_of = ?
                                WHERE id = ?
                            ''', (original_id, dup_id))
                            
                            duplicates_merged += 1
                            space_saved += len(content_hash)  # Rough estimate
                    
                    duplicates_found += count - 1
                    processed += count
            
            await conn.commit()
        
        return {
            'processed': processed,
            'duplicates_found': duplicates_found,
            'duplicates_merged': duplicates_merged,
            'space_saved': space_saved
        }
    
    async def _deduplicate_contacts(self) -> Dict[str, int]:
        """Deduplicate contacts with intelligent merging"""
        processed = 0
        duplicates_found = 0
        duplicates_merged = 0
        space_saved = 0
        
        async with self.data_manager.get_connection() as conn:
            # Find potential duplicate contacts by username or name
            async with conn.execute('''
                SELECT username, name, GROUP_CONCAT(id) as ids, COUNT(*) as count
                FROM contacts 
                WHERE username IS NOT NULL AND username != ''
                GROUP BY LOWER(username)
                HAVING count > 1
            ''') as cursor:
                async for row in cursor:
                    username, name, ids_str, count = row
                    contact_ids = ids_str.split(',')
                    
                    if len(contact_ids) > 1:
                        # Merge contact data intelligently
                        await self._merge_contacts(conn, contact_ids)
                        duplicates_merged += count - 1
                        space_saved += len(username) * (count - 1)
                    
                    duplicates_found += count - 1
                    processed += count
            
            await conn.commit()
        
        return {
            'processed': processed,
            'duplicates_found': duplicates_found,
            'duplicates_merged': duplicates_merged,
            'space_saved': space_saved
        }
    
    async def _merge_contacts(self, conn, contact_ids: List[str]):
        """Intelligently merge duplicate contacts"""
        # Get all contact data
        contacts_data = []
        for contact_id in contact_ids:
            async with conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    contact_data = dict(zip(columns, row))
                    contacts_data.append(contact_data)
        
        if len(contacts_data) < 2:
            return
        
        # Merge strategy: keep most complete record
        best_contact = max(contacts_data, key=lambda c: sum(1 for v in c.values() if v))
        
        # Merge data from other contacts
        for contact in contacts_data:
            if contact['id'] == best_contact['id']:
                continue
                
            # Merge non-empty fields
            for field, value in contact.items():
                if value and not best_contact.get(field):
                    best_contact[field] = value
            
            # Aggregate numeric fields
            if contact.get('message_count', 0) > 0:
                best_contact['message_count'] = (best_contact.get('message_count', 0) + 
                                               contact.get('message_count', 0))
            
            if contact.get('lead_score', 0) > best_contact.get('lead_score', 0):
                best_contact['lead_score'] = contact['lead_score']
        
        # Update best contact with merged data
        update_fields = []
        update_values = []
        for field, value in best_contact.items():
            if field != 'id':
                update_fields.append(f'{field} = ?')
                update_values.append(value)
        
        update_values.append(best_contact['id'])
        
        await conn.execute(f'''
            UPDATE contacts SET {', '.join(update_fields)}, updated_at = ?
            WHERE id = ?
        ''', update_values + [datetime.now().isoformat()])
        
        # Remove duplicate contacts
        for contact in contacts_data:
            if contact['id'] != best_contact['id']:
                await conn.execute('DELETE FROM contacts WHERE id = ?', (contact['id'],))
    
    async def _deduplicate_cross_type(self) -> Dict[str, int]:
        """Perform cross-type deduplication and conflict resolution"""
        conflicts_resolved = 0
        
        # Example: Extract contact info from messages and merge with contacts
        async with self.data_manager.get_connection() as conn:
            # Find messages with user info that might enhance contacts
            async with conn.execute('''
                SELECT DISTINCT m.user_id, m.username, m.first_name, m.last_name
                FROM messages m
                LEFT JOIN contacts c ON m.user_id = c.id
                WHERE m.user_id IS NOT NULL 
                AND (c.id IS NULL OR c.name IS NULL OR c.name = '')
                AND (m.first_name IS NOT NULL OR m.last_name IS NOT NULL)
            ''') as cursor:
                async for row in cursor:
                    user_id, username, first_name, last_name = row
                    
                    # Create or update contact
                    full_name = f"{first_name or ''} {last_name or ''}".strip()
                    if full_name:
                        await conn.execute('''
                            INSERT OR REPLACE INTO contacts 
                            (id, name, username, category, created_at, updated_at)
                            VALUES (?, ?, ?, 'auto_extracted', ?, ?)
            ''', (
                            str(user_id), full_name, username or '',
                            datetime.now().isoformat(), datetime.now().isoformat()
                        ))
                        conflicts_resolved += 1
            
            await conn.commit()
        
        return {'conflicts_resolved': conflicts_resolved}
    
    def _update_performance_metrics(self, operation: SyncOperation, duration: float):
        """Update performance metrics"""
        self.performance_metrics['operations_completed'] += 1
        
        # Update average operation time
        current_avg = self.performance_metrics['avg_operation_time']
        count = self.performance_metrics['operations_completed']
        
        if count == 1:
            self.performance_metrics['avg_operation_time'] = duration
        else:
            self.performance_metrics['avg_operation_time'] = ((current_avg * (count - 1)) + duration) / count
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and metrics"""
        return {
            'performance_metrics': self.performance_metrics.copy(),
            'scheduled_operations': len(self.scheduled_operations),
            'running_operations': len(self.running_operations),
            'auto_sync_enabled': self.auto_sync_enabled,
            'auto_dedup_enabled': self.auto_dedup_enabled,
            'auto_backup_enabled': self.auto_backup_enabled,
            'content_fingerprints': {k: len(v) for k, v in self.content_fingerprints.items()}
        }
    
    async def force_full_sync(self) -> str:
        """Force a full sync operation"""
        operation_id = f"manual_full_sync_{int(time.time())}"
        
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type="full_sync",
            status="pending",
            priority=10,  # Highest priority
            scheduled_time=datetime.now()
        )
        
        self.schedule_operation(operation)
        return operation_id
    
    async def force_deduplication(self) -> str:
        """Force a deduplication operation"""
        operation_id = f"manual_dedup_{int(time.time())}"
        
        operation = SyncOperation(
            operation_id=operation_id,
            operation_type="deduplication",
            status="pending",
            priority=9,
            scheduled_time=datetime.now()
        )
        
        self.schedule_operation(operation)
        return operation_id

# Global instance
smart_sync_manager = None

async def get_smart_sync_manager() -> SmartSyncManager:
    """Get the global smart sync manager instance"""
    global smart_sync_manager
    if smart_sync_manager is None:
        smart_sync_manager = SmartSyncManager()
        await smart_sync_manager.initialize()
    return smart_sync_manager 