#!/usr/bin/env python3
"""
Differential Backup System
==========================
Smart backup system that only syncs changes, optimized for sporadic usage:
- Tracks what has changed since last backup
- Only syncs modified/new data
- Supports multiple backup targets (local, cloud, etc.)
- Optimized for bandwidth and storage efficiency
- Handles conflict resolution and merge strategies
"""

import asyncio
import json
import hashlib
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class BackupMetadata:
    """Metadata for backup operations"""
    backup_id: str
    timestamp: datetime
    source_db_hash: str
    changes_count: int
    backup_size: int
    backup_type: str  # 'full', 'differential', 'incremental'
    success: bool
    error_message: Optional[str] = None
    duration_seconds: float = 0.0

@dataclass
class SyncTarget:
    """Configuration for backup target"""
    name: str
    type: str  # 'local', 'cloud', 'remote_db'
    path: str
    enabled: bool = True
    last_sync: Optional[datetime] = None
    compression: bool = True
    encryption: bool = False

class DifferentialBackupManager:
    """Manages differential backups and syncing"""
    
    def __init__(self, data_dir: str = "data", backup_dir: str = "backups"):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup subdirectories
        self.full_backups_dir = self.backup_dir / "full"
        self.differential_dir = self.backup_dir / "differential"
        self.metadata_dir = self.backup_dir / "metadata"
        
        for dir_path in [self.full_backups_dir, self.differential_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Configuration
        self.max_differential_count = 10  # Create full backup after 10 differentials
        self.max_backup_age_days = 30    # Keep backups for 30 days
        self.compression_level = 6       # ZIP compression level
        
        # Sync targets
        self.sync_targets: Dict[str, SyncTarget] = {}
        self._load_sync_targets()
        
        # State tracking
        self.last_full_backup: Optional[BackupMetadata] = None
        self.last_differential_backup: Optional[BackupMetadata] = None
        self._load_backup_history()
        
    def _load_sync_targets(self):
        """Load sync target configurations"""
        config_file = self.backup_dir / "sync_targets.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    targets_data = json.load(f)
                    
                for name, data in targets_data.items():
                    self.sync_targets[name] = SyncTarget(
                        name=data['name'],
                        type=data['type'],
                        path=data['path'],
                        enabled=data.get('enabled', True),
                        last_sync=datetime.fromisoformat(data['last_sync']) if data.get('last_sync') else None,
                        compression=data.get('compression', True),
                        encryption=data.get('encryption', False)
                    )
                    
            except Exception as e:
                logger.error(f"❌ Failed to load sync targets: {e}")
        
        # Add default local backup target if none exist
        if not self.sync_targets:
            self.add_sync_target(SyncTarget(
                name="local_backup",
                type="local",
                path=str(self.backup_dir / "local"),
                enabled=True,
                compression=True
            ))
    
    def _save_sync_targets(self):
        """Save sync target configurations"""
        config_file = self.backup_dir / "sync_targets.json"
        
        try:
            targets_data = {}
            for name, target in self.sync_targets.items():
                targets_data[name] = {
                    'name': target.name,
                    'type': target.type,
                    'path': target.path,
                    'enabled': target.enabled,
                    'last_sync': target.last_sync.isoformat() if target.last_sync else None,
                    'compression': target.compression,
                    'encryption': target.encryption
                }
            
            with open(config_file, 'w') as f:
                json.dump(targets_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save sync targets: {e}")
    
    def add_sync_target(self, target: SyncTarget):
        """Add a new sync target"""
        self.sync_targets[target.name] = target
        self._save_sync_targets()
        
        # Create target directory if local
        if target.type == "local":
            Path(target.path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Added sync target: {target.name} ({target.type})")
    
    def _load_backup_history(self):
        """Load backup history metadata"""
        history_file = self.metadata_dir / "backup_history.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    
                if 'last_full_backup' in history and history['last_full_backup']:
                    data = history['last_full_backup']
                    self.last_full_backup = BackupMetadata(
                        backup_id=data['backup_id'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        source_db_hash=data['source_db_hash'],
                        changes_count=data['changes_count'],
                        backup_size=data['backup_size'],
                        backup_type=data['backup_type'],
                        success=data['success'],
                        error_message=data.get('error_message'),
                        duration_seconds=data.get('duration_seconds', 0.0)
                    )
                
                if 'last_differential_backup' in history and history['last_differential_backup']:
                    data = history['last_differential_backup']
                    self.last_differential_backup = BackupMetadata(
                        backup_id=data['backup_id'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        source_db_hash=data['source_db_hash'],
                        changes_count=data['changes_count'],
                        backup_size=data['backup_size'],
                        backup_type=data['backup_type'],
                        success=data['success'],
                        error_message=data.get('error_message'),
                        duration_seconds=data.get('duration_seconds', 0.0)
                    )
                    
            except Exception as e:
                logger.error(f"❌ Failed to load backup history: {e}")
    
    def _save_backup_history(self):
        """Save backup history metadata"""
        history_file = self.metadata_dir / "backup_history.json"
        
        try:
            history = {}
            
            if self.last_full_backup:
                history['last_full_backup'] = asdict(self.last_full_backup)
                history['last_full_backup']['timestamp'] = self.last_full_backup.timestamp.isoformat()
            
            if self.last_differential_backup:
                history['last_differential_backup'] = asdict(self.last_differential_backup)
                history['last_differential_backup']['timestamp'] = self.last_differential_backup.timestamp.isoformat()
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Failed to save backup history: {e}")
    
    def _calculate_db_hash(self) -> str:
        """Calculate hash of the current database state"""
        try:
            db_path = self.data_dir / "telegram_manager.db"
            if not db_path.exists():
                return "empty"
            
            hash_md5 = hashlib.md5()
            with open(db_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate DB hash: {e}")
            return "error"
    
    async def needs_backup(self) -> Tuple[bool, str]:
        """Check if backup is needed and what type"""
        current_hash = self._calculate_db_hash()
        
        # Check if database has changed
        if self.last_differential_backup:
            if current_hash == self.last_differential_backup.source_db_hash:
                return False, "no_changes"
        elif self.last_full_backup:
            if current_hash == self.last_full_backup.source_db_hash:
                return False, "no_changes"
        
        # Determine backup type needed
        if not self.last_full_backup:
            return True, "full"
        
        # Check if full backup is too old
        days_since_full = (datetime.now() - self.last_full_backup.timestamp).days
        if days_since_full > 7:  # Weekly full backups
            return True, "full"
        
        # Count differential backups since last full
        differential_count = await self._count_differentials_since_full()
        if differential_count >= self.max_differential_count:
            return True, "full"
        
        return True, "differential"
    
    async def _count_differentials_since_full(self) -> int:
        """Count differential backups since last full backup"""
        if not self.last_full_backup:
            return 0
        
        count = 0
        for backup_file in self.differential_dir.glob("*.zip"):
            # Extract timestamp from filename
            try:
                timestamp_str = backup_file.stem.split("_")[-1]
                backup_time = datetime.fromisoformat(timestamp_str.replace("-", ":"))
                if backup_time > self.last_full_backup.timestamp:
                    count += 1
            except Exception:
                continue
        
        return count
    
    async def create_backup(self, force_full: bool = False) -> Optional[BackupMetadata]:
        """Create a backup (full or differential)"""
        start_time = datetime.now()
        
        try:
            # Check if backup is needed
            needs_backup, backup_type = await self.needs_backup()
            
            if not needs_backup and not force_full:
                logger.info("📦 No backup needed - database unchanged")
                return None
            
            if force_full:
                backup_type = "full"
            
            logger.info(f"📦 Creating {backup_type} backup...")
            
            # Create backup based on type
            if backup_type == "full":
                metadata = await self._create_full_backup()
            else:
                metadata = await self._create_differential_backup()
            
            if metadata and metadata.success:
                # Update backup history
                if backup_type == "full":
                    self.last_full_backup = metadata
                else:
                    self.last_differential_backup = metadata
                
                self._save_backup_history()
                
                # Sync to targets
                await self._sync_to_targets(metadata)
                
                # Cleanup old backups
                await self._cleanup_old_backups()
                
                logger.info(f"✅ {backup_type.title()} backup completed: {metadata.backup_id}")
                
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return BackupMetadata(
                backup_id=f"failed_{int(start_time.timestamp())}",
                timestamp=start_time,
                source_db_hash="error",
                changes_count=0,
                backup_size=0,
                backup_type="error",
                success=False,
                error_message=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    async def _create_full_backup(self) -> BackupMetadata:
        """Create a full backup of the database"""
        start_time = datetime.now()
        backup_id = f"full_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Calculate current DB hash
            db_hash = self._calculate_db_hash()
            
            # Create backup filename
            backup_filename = f"{backup_id}.zip"
            backup_path = self.full_backups_dir / backup_filename
            
            # Create ZIP archive
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=self.compression_level) as zipf:
                # Add main database
                db_path = self.data_dir / "telegram_manager.db"
                if db_path.exists():
                    zipf.write(db_path, "telegram_manager.db")
                
                # Add changes tracking database
                changes_db_path = self.data_dir / "changes_tracking.db"
                if changes_db_path.exists():
                    zipf.write(changes_db_path, "changes_tracking.db")
                
                # Add any other data files
                for data_file in self.data_dir.glob("*.json"):
                    zipf.write(data_file, data_file.name)
                
                # Add metadata
                metadata = {
                    'backup_id': backup_id,
                    'timestamp': start_time.isoformat(),
                    'backup_type': 'full',
                    'db_hash': db_hash
                }
                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
            
            # Calculate backup size
            backup_size = backup_path.stat().st_size
            duration = (datetime.now() - start_time).total_seconds()
            
            return BackupMetadata(
                backup_id=backup_id,
                timestamp=start_time,
                source_db_hash=db_hash,
                changes_count=0,  # Full backup doesn't track individual changes
                backup_size=backup_size,
                backup_type="full",
                success=True,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"❌ Full backup failed: {e}")
            raise
    
    async def _create_differential_backup(self) -> BackupMetadata:
        """Create a differential backup with only changes"""
        start_time = datetime.now()
        backup_id = f"diff_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Get async data manager
            from .async_data_manager import get_async_data_manager
            data_manager = await get_async_data_manager()
            
            # Get unsynced changes
            changes = await data_manager.get_unsynced_changes(limit=10000)
            
            if not changes:
                logger.info("📦 No changes to backup")
                return BackupMetadata(
                    backup_id=backup_id,
                    timestamp=start_time,
                    source_db_hash=self._calculate_db_hash(),
                    changes_count=0,
                    backup_size=0,
                    backup_type="differential",
                    success=True,
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Create backup filename
            backup_filename = f"{backup_id}.zip"
            backup_path = self.differential_dir / backup_filename
            
            # Create ZIP archive with changes
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=self.compression_level) as zipf:
                # Add changes data
                changes_data = []
                for change in changes:
                    changes_data.append({
                        'id': change.id,
                        'entity_type': change.entity_type,
                        'entity_id': change.entity_id,
                        'operation': change.operation,
                        'content_hash': change.content_hash,
                        'change_data': change.change_data,
                        'timestamp': change.timestamp.isoformat()
                    })
                
                zipf.writestr("changes.json", json.dumps(changes_data, indent=2))
                
                # Add metadata
                metadata = {
                    'backup_id': backup_id,
                    'timestamp': start_time.isoformat(),
                    'backup_type': 'differential',
                    'changes_count': len(changes),
                    'base_backup': self.last_full_backup.backup_id if self.last_full_backup else None,
                    'db_hash': self._calculate_db_hash()
                }
                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
            
            # Calculate backup size
            backup_size = backup_path.stat().st_size
            duration = (datetime.now() - start_time).total_seconds()
            
            # Mark changes as synced
            change_ids = [change.id for change in changes]
            await data_manager.mark_changes_synced(change_ids)
            
            return BackupMetadata(
                backup_id=backup_id,
                timestamp=start_time,
                source_db_hash=self._calculate_db_hash(),
                changes_count=len(changes),
                backup_size=backup_size,
                backup_type="differential",
                success=True,
                duration_seconds=duration
            )
                        
        except Exception as e:
            logger.error(f"❌ Differential backup failed: {e}")
            raise
    
    async def _sync_to_targets(self, metadata: BackupMetadata):
        """Sync backup to configured targets"""
        backup_filename = f"{metadata.backup_id}.zip"
        
        if metadata.backup_type == "full":
            source_path = self.full_backups_dir / backup_filename
            else:
            source_path = self.differential_dir / backup_filename
        
        if not source_path.exists():
            logger.error(f"❌ Backup file not found: {source_path}")
            return
        
        for target in self.sync_targets.values():
            if not target.enabled:
                continue
            
            try:
                if target.type == "local":
                    await self._sync_to_local_target(source_path, target, metadata)
                elif target.type == "cloud":
                    await self._sync_to_cloud_target(source_path, target, metadata)
                # Add more target types as needed
                
                target.last_sync = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Failed to sync to target {target.name}: {e}")
        
        self._save_sync_targets()
    
    async def _sync_to_local_target(self, source_path: Path, target: SyncTarget, metadata: BackupMetadata):
        """Sync backup to local target"""
        target_dir = Path(target.path)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / source_path.name
        
        # Copy file
        shutil.copy2(source_path, target_path)
        
        logger.info(f"📁 Synced to local target: {target.name}")
    
    async def _sync_to_cloud_target(self, source_path: Path, target: SyncTarget, metadata: BackupMetadata):
        """Sync backup to cloud target (placeholder for cloud implementation)"""
        # This would implement cloud sync (AWS S3, Google Drive, etc.)
        logger.info(f"☁️ Cloud sync to {target.name} - Implementation needed")
    
    async def _cleanup_old_backups(self):
        """Clean up old backup files"""
        cutoff_date = datetime.now() - timedelta(days=self.max_backup_age_days)
        
        # Clean up full backups
        for backup_file in self.full_backups_dir.glob("*.zip"):
            try:
                # Extract timestamp from filename
                timestamp_str = backup_file.stem.split("_")[1]
                backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if backup_time < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"🗑️ Removed old full backup: {backup_file.name}")
                    
        except Exception as e:
                logger.error(f"❌ Failed to process backup file {backup_file}: {e}")
        
        # Clean up differential backups
        for backup_file in self.differential_dir.glob("*.zip"):
            try:
                timestamp_str = backup_file.stem.split("_")[1]
                backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if backup_time < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"🗑️ Removed old differential backup: {backup_file.name}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process backup file {backup_file}: {e}")
    
    async def restore_from_backup(self, backup_id: str) -> bool:
        """Restore database from backup"""
        try:
            # Find backup file
            backup_file = None
            
            # Check full backups
            full_backup_path = self.full_backups_dir / f"{backup_id}.zip"
            if full_backup_path.exists():
                backup_file = full_backup_path
                backup_type = "full"
            
            # Check differential backups
            if not backup_file:
                diff_backup_path = self.differential_dir / f"{backup_id}.zip"
                if diff_backup_path.exists():
                    backup_file = diff_backup_path
                    backup_type = "differential"
            
            if not backup_file:
                logger.error(f"❌ Backup not found: {backup_id}")
                return False
            
            logger.info(f"🔄 Restoring from {backup_type} backup: {backup_id}")
            
            if backup_type == "full":
                return await self._restore_full_backup(backup_file)
            else:
                return await self._restore_differential_backup(backup_file)
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False
    
    async def _restore_full_backup(self, backup_file: Path) -> bool:
        """Restore from full backup"""
        try:
            # Create backup of current state
            current_backup_dir = self.backup_dir / "pre_restore"
            current_backup_dir.mkdir(exist_ok=True)
            
            db_path = self.data_dir / "telegram_manager.db"
            if db_path.exists():
                shutil.copy2(db_path, current_backup_dir / f"backup_{int(datetime.now().timestamp())}.db")
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(self.data_dir)
            
            logger.info(f"✅ Full backup restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Full backup restore failed: {e}")
            return False
    
    async def _restore_differential_backup(self, backup_file: Path) -> bool:
        """Restore from differential backup (requires base backup)"""
        # This would implement differential restore logic
        # For now, suggest doing a full restore
        logger.warning("⚠️ Differential restore not implemented - use full backup")
        return False
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup status and statistics"""
        full_backups = list(self.full_backups_dir.glob("*.zip"))
        diff_backups = list(self.differential_dir.glob("*.zip"))
        
        total_backup_size = sum(f.stat().st_size for f in full_backups + diff_backups)
                
                return {
            'last_full_backup': asdict(self.last_full_backup) if self.last_full_backup else None,
            'last_differential_backup': asdict(self.last_differential_backup) if self.last_differential_backup else None,
            'full_backups_count': len(full_backups),
            'differential_backups_count': len(diff_backups),
            'total_backup_size_mb': total_backup_size / (1024 * 1024),
            'sync_targets': {name: asdict(target) for name, target in self.sync_targets.items()},
            'needs_backup': await self.needs_backup()
        }

# Global instance
backup_manager = None

async def get_backup_manager() -> DifferentialBackupManager:
    """Get the global backup manager instance"""
    global backup_manager
    if backup_manager is None:
        backup_manager = DifferentialBackupManager()
    return backup_manager 