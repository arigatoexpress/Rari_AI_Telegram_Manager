#!/usr/bin/env python3
"""
Smart Cache System
==================
Intelligent caching optimized for sporadic usage patterns:
- Multi-level caching (memory, disk, distributed)
- Intelligent cache warming and eviction
- Adaptive TTL based on access patterns
- Cache analytics and optimization
- Memory-efficient storage with compression
"""

import asyncio
import json
import pickle
import gzip
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from pathlib import Path
import weakref
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    """Cache entry with metadata"""
    key: str
    value: T
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: float = 3600  # 1 hour default
    size_bytes: int = 0
    compressed: bool = False
    priority: int = 5  # 1-10, higher is more important
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at
    
    @property
    def seconds_since_access(self) -> float:
        return time.time() - self.last_accessed

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0
    memory_usage_mb: float = 0.0

class SmartCache:
    """Multi-level intelligent cache system"""
    
    def __init__(self, 
                 memory_limit_mb: int = 256,
                 disk_cache_dir: str = "cache",
                 disk_limit_mb: int = 1024,
                 enable_compression: bool = True,
                 default_ttl: int = 3600):
        
        # Configuration
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.disk_limit_bytes = disk_limit_mb * 1024 * 1024
        self.enable_compression = enable_compression
        self.default_ttl = default_ttl
        
        # Memory cache (LRU)
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.memory_size = 0
        self.cache_lock = asyncio.Lock()
        
        # Disk cache
        self.disk_cache_dir = Path(disk_cache_dir)
        self.disk_cache_dir.mkdir(exist_ok=True)
        self.disk_index: Dict[str, Dict[str, Any]] = {}
        self.disk_size = 0
        
        # Statistics
        self.stats = CacheStats()
        
        # Access patterns tracking
        self.access_patterns: Dict[str, List[float]] = {}
        self.pattern_window = 3600  # 1 hour window
        
        # Background tasks
        self.cleanup_interval = 300  # 5 minutes
        self.analytics_interval = 900  # 15 minutes
        
        # Adaptive TTL settings
        self.adaptive_ttl_enabled = True
        self.ttl_multipliers = {
            'hot': 2.0,    # Frequently accessed
            'warm': 1.0,   # Normal access
            'cold': 0.5    # Rarely accessed
        }
        
        self._initialized = False
        self._running = False
    
    async def initialize(self):
        """Initialize the cache system"""
        if self._initialized:
            return
        
        try:
            # Load disk cache index
            await self._load_disk_index()
            
            # Start background tasks
            self._running = True
            asyncio.create_task(self._cleanup_task())
            asyncio.create_task(self._analytics_task())
            asyncio.create_task(self._cache_warming_task())
            
            self._initialized = True
            logger.info(f"✅ Smart Cache initialized (Memory: {self.memory_limit_bytes/1024/1024:.1f}MB, Disk: {self.disk_limit_bytes/1024/1024:.1f}MB)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Smart Cache: {e}")
            raise
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with intelligent access tracking"""
        start_time = time.time()
        
        try:
            async with self.cache_lock:
                # Check memory cache first
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    
                    # Check if expired
                    if entry.is_expired:
                        await self._remove_from_memory(key)
                        self.stats.misses += 1
                        return default
                    
                    # Update access info
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    
                    # Move to end (LRU)
                    self.memory_cache.move_to_end(key)
                    
                    # Track access pattern
                    self._track_access_pattern(key)
                    
                    self.stats.hits += 1
                    access_time = (time.time() - start_time) * 1000
                    self._update_avg_access_time(access_time)
                    
                    return entry.value
                
                # Check disk cache
                disk_entry = await self._get_from_disk(key)
                if disk_entry is not None:
                    # Promote to memory cache
                    await self._promote_to_memory(key, disk_entry)
                    
                    self.stats.hits += 1
                    access_time = (time.time() - start_time) * 1000
                    self._update_avg_access_time(access_time)
                    
                    return disk_entry.value
                
                # Cache miss
                self.stats.misses += 1
                return default
                
        except Exception as e:
            logger.error(f"❌ Cache get error for key {key}: {e}")
            return default
    
    async def put(self, key: str, value: Any, ttl: Optional[int] = None, 
                  priority: int = 5, tags: Optional[List[str]] = None) -> bool:
        """Store value in cache with intelligent placement"""
        try:
            # Calculate adaptive TTL
            if ttl is None:
                ttl = self._calculate_adaptive_ttl(key)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=ttl,
                priority=priority,
                tags=tags or [],
                size_bytes=self._calculate_size(value)
            )
            
            async with self.cache_lock:
                # Try to store in memory first
                if await self._can_fit_in_memory(entry):
                    await self._put_in_memory(key, entry)
                else:
                    # Store in disk cache
                    await self._put_in_disk(key, entry)
                
                self._track_access_pattern(key)
                return True
                
        except Exception as e:
            logger.error(f"❌ Cache put error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        try:
            async with self.cache_lock:
                deleted = False
                
                # Remove from memory
                if key in self.memory_cache:
                    await self._remove_from_memory(key)
                    deleted = True
                
                # Remove from disk
                if await self._remove_from_disk(key):
                    deleted = True
                
                # Clean up access patterns
                if key in self.access_patterns:
                    del self.access_patterns[key]
                
                return deleted
                
        except Exception as e:
            logger.error(f"❌ Cache delete error for key {key}: {e}")
            return False
    
    async def clear(self, tags: Optional[List[str]] = None) -> int:
        """Clear cache entries, optionally by tags"""
        try:
            async with self.cache_lock:
                cleared_count = 0
                
                if tags is None:
                    # Clear everything
                    cleared_count = len(self.memory_cache)
                    self.memory_cache.clear()
                    self.memory_size = 0
                    
                    # Clear disk cache
                    for cache_file in self.disk_cache_dir.glob("*.cache"):
                        cache_file.unlink()
                    self.disk_index.clear()
                    self.disk_size = 0
                    
                    # Clear access patterns
                    self.access_patterns.clear()
                    
                else:
                    # Clear by tags
                    keys_to_remove = []
                    
                    # Check memory cache
                    for key, entry in self.memory_cache.items():
                        if any(tag in entry.tags for tag in tags):
                            keys_to_remove.append(key)
                    
                    # Check disk cache
                    for key, metadata in self.disk_index.items():
                        if any(tag in metadata.get('tags', []) for tag in tags):
                            keys_to_remove.append(key)
                    
                    # Remove found keys
                    for key in set(keys_to_remove):
                        await self.delete(key)
                        cleared_count += 1
                
                return cleared_count
                
        except Exception as e:
            logger.error(f"❌ Cache clear error: {e}")
            return 0
    
    async def _can_fit_in_memory(self, entry: CacheEntry) -> bool:
        """Check if entry can fit in memory cache"""
        available_space = self.memory_limit_bytes - self.memory_size
        
        if entry.size_bytes <= available_space:
            return True
        
        # Try to make space by evicting old entries
        space_needed = entry.size_bytes - available_space
        return await self._can_evict_for_space(space_needed)
    
    async def _can_evict_for_space(self, space_needed: int) -> bool:
        """Check if we can evict enough entries to make space"""
        space_available = 0
        
        # Check from least recently used
        for key, entry in list(self.memory_cache.items()):
            if entry.priority < 8:  # Don't evict high priority items
                space_available += entry.size_bytes
                if space_available >= space_needed:
                    return True
        
        return False
    
    async def _put_in_memory(self, key: str, entry: CacheEntry):
        """Store entry in memory cache"""
        # Make space if needed
        while self.memory_size + entry.size_bytes > self.memory_limit_bytes:
            if not await self._evict_lru():
                break
        
        self.memory_cache[key] = entry
        self.memory_size += entry.size_bytes
        self.stats.entry_count += 1
        self.stats.size_bytes += entry.size_bytes
    
    async def _evict_lru(self) -> bool:
        """Evict least recently used entry from memory"""
        if not self.memory_cache:
            return False
        
        # Find LRU entry (first in OrderedDict)
        lru_key = next(iter(self.memory_cache))
        lru_entry = self.memory_cache[lru_key]
        
        # Don't evict high priority items unless absolutely necessary
        if lru_entry.priority >= 8 and len(self.memory_cache) > 1:
            # Try to find a lower priority item
            for key, entry in self.memory_cache.items():
                if entry.priority < 8:
                    lru_key = key
                    lru_entry = entry
                    break
        
        # Move to disk cache before evicting
        await self._put_in_disk(lru_key, lru_entry)
        
        # Remove from memory
        await self._remove_from_memory(lru_key)
        self.stats.evictions += 1
        
        return True
    
    async def _remove_from_memory(self, key: str):
        """Remove entry from memory cache"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            del self.memory_cache[key]
            self.memory_size -= entry.size_bytes
            self.stats.entry_count -= 1
            self.stats.size_bytes -= entry.size_bytes
    
    async def _put_in_disk(self, key: str, entry: CacheEntry):
        """Store entry in disk cache"""
        try:
            # Create filename
            key_hash = hashlib.md5(key.encode()).hexdigest()
            cache_file = self.disk_cache_dir / f"{key_hash}.cache"
            
            # Prepare data for storage
            data = {
                'key': key,
                'value': entry.value,
                'created_at': entry.created_at,
                'last_accessed': entry.last_accessed,
                'access_count': entry.access_count,
                'ttl': entry.ttl,
                'priority': entry.priority,
                'tags': entry.tags,
                'metadata': entry.metadata
            }
            
            # Serialize and optionally compress
            serialized = pickle.dumps(data)
            
            if self.enable_compression and len(serialized) > 1024:  # Compress if > 1KB
                serialized = gzip.compress(serialized)
                entry.compressed = True
            
            # Write to disk
            with open(cache_file, 'wb') as f:
                f.write(serialized)
            
            # Update disk index
            self.disk_index[key] = {
                'file': cache_file.name,
                'size': len(serialized),
                'compressed': entry.compressed,
                'created_at': entry.created_at,
                'ttl': entry.ttl,
                'tags': entry.tags
            }
            
            self.disk_size += len(serialized)
            
            # Cleanup disk cache if too large
            await self._cleanup_disk_cache()
            
        except Exception as e:
            logger.error(f"❌ Disk cache put error for key {key}: {e}")
    
    async def _get_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Retrieve entry from disk cache"""
        try:
            if key not in self.disk_index:
                return None
            
            metadata = self.disk_index[key]
            cache_file = self.disk_cache_dir / metadata['file']
            
            if not cache_file.exists():
                # Clean up stale index entry
                del self.disk_index[key]
                return None
            
            # Check if expired
            age = time.time() - metadata['created_at']
            if age > metadata['ttl']:
                await self._remove_from_disk(key)
                return None
            
            # Read and deserialize
            with open(cache_file, 'rb') as f:
                data = f.read()
            
            if metadata.get('compressed', False):
                data = gzip.decompress(data)
            
            obj_data = pickle.loads(data)
            
            # Create cache entry
            entry = CacheEntry(
                key=obj_data['key'],
                value=obj_data['value'],
                created_at=obj_data['created_at'],
                last_accessed=time.time(),  # Update access time
                access_count=obj_data['access_count'] + 1,
                ttl=obj_data['ttl'],
                priority=obj_data['priority'],
                tags=obj_data['tags'],
                metadata=obj_data['metadata'],
                size_bytes=self._calculate_size(obj_data['value'])
            )
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Disk cache get error for key {key}: {e}")
            return None
    
    async def _remove_from_disk(self, key: str) -> bool:
        """Remove entry from disk cache"""
        try:
            if key not in self.disk_index:
                return False
            
            metadata = self.disk_index[key]
            cache_file = self.disk_cache_dir / metadata['file']
            
            if cache_file.exists():
                cache_file.unlink()
            
            self.disk_size -= metadata['size']
            del self.disk_index[key]
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Disk cache remove error for key {key}: {e}")
            return False
    
    async def _promote_to_memory(self, key: str, entry: CacheEntry):
        """Promote disk cache entry to memory cache"""
        if await self._can_fit_in_memory(entry):
            await self._put_in_memory(key, entry)
            await self._remove_from_disk(key)
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, tuple)):
                return sum(self._calculate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._calculate_size(k) + self._calculate_size(v) 
                          for k, v in value.items())
            else:
                # Use pickle size as approximation
                return len(pickle.dumps(value))
        except Exception:
            return 1024  # Default estimate
    
    def _track_access_pattern(self, key: str):
        """Track access patterns for adaptive optimization"""
        current_time = time.time()
        
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        
        self.access_patterns[key].append(current_time)
        
        # Keep only recent accesses within window
        cutoff_time = current_time - self.pattern_window
        self.access_patterns[key] = [
            t for t in self.access_patterns[key] if t > cutoff_time
        ]
    
    def _calculate_adaptive_ttl(self, key: str) -> int:
        """Calculate adaptive TTL based on access patterns"""
        if not self.adaptive_ttl_enabled:
            return self.default_ttl
        
        base_ttl = self.default_ttl
        
        if key in self.access_patterns:
            accesses = self.access_patterns[key]
            current_time = time.time()
            
            # Calculate access frequency
            recent_accesses = [t for t in accesses if current_time - t < 3600]  # Last hour
            frequency = len(recent_accesses)
            
            # Categorize access pattern
            if frequency >= 10:
                category = 'hot'
            elif frequency >= 3:
                category = 'warm'
            else:
                category = 'cold'
            
            # Apply multiplier
            multiplier = self.ttl_multipliers[category]
            return int(base_ttl * multiplier)
        
        return base_ttl
    
    def _update_avg_access_time(self, access_time_ms: float):
        """Update average access time"""
        current_avg = self.stats.avg_access_time_ms
        total_accesses = self.stats.hits + self.stats.misses
        
        if total_accesses == 1:
            self.stats.avg_access_time_ms = access_time_ms
        else:
            self.stats.avg_access_time_ms = ((current_avg * (total_accesses - 1)) + access_time_ms) / total_accesses
    
    async def _cleanup_task(self):
        """Background cleanup task"""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_entries()
                
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
    
    async def _cleanup_expired_entries(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = []
        
        async with self.cache_lock:
            # Check memory cache
            for key, entry in self.memory_cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            
            # Check disk cache
            for key, metadata in self.disk_index.items():
                age = current_time - metadata['created_at']
                if age > metadata['ttl']:
                    expired_keys.append(key)
        
        # Remove expired entries
        for key in set(expired_keys):
            await self.delete(key)
        
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(set(expired_keys))} expired cache entries")
    
    async def _cleanup_disk_cache(self):
        """Cleanup disk cache if it exceeds size limit"""
        if self.disk_size <= self.disk_limit_bytes:
            return
        
        # Sort by access time (oldest first)
        sorted_entries = sorted(
            self.disk_index.items(),
            key=lambda x: x[1]['created_at']
        )
        
        # Remove oldest entries until under limit
        for key, metadata in sorted_entries:
            if self.disk_size <= self.disk_limit_bytes * 0.8:  # 80% of limit
                break
            
            await self._remove_from_disk(key)
    
    async def _analytics_task(self):
        """Background analytics and optimization task"""
        while self._running:
            try:
                await asyncio.sleep(self.analytics_interval)
                await self._update_cache_analytics()
                
            except Exception as e:
                logger.error(f"❌ Cache analytics error: {e}")
    
    async def _update_cache_analytics(self):
        """Update cache analytics and performance metrics"""
        # Calculate hit rate
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.hit_rate = self.stats.hits / total_requests
        
        # Calculate memory usage
        self.stats.memory_usage_mb = self.memory_size / (1024 * 1024)
        
        # Log analytics
        logger.info(f"📊 Cache Analytics:")
        logger.info(f"   Hit Rate: {self.stats.hit_rate:.2%}")
        logger.info(f"   Memory Usage: {self.stats.memory_usage_mb:.1f}MB")
        logger.info(f"   Entries: {self.stats.entry_count} (memory) + {len(self.disk_index)} (disk)")
        logger.info(f"   Avg Access Time: {self.stats.avg_access_time_ms:.2f}ms")
    
    async def _cache_warming_task(self):
        """Proactive cache warming based on access patterns"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Every hour
                await self._warm_frequently_accessed()
                
            except Exception as e:
                logger.error(f"❌ Cache warming error: {e}")
    
    async def _warm_frequently_accessed(self):
        """Warm cache with frequently accessed items"""
        # Identify hot keys
        hot_keys = []
        current_time = time.time()
        
        for key, accesses in self.access_patterns.items():
            recent_accesses = [t for t in accesses if current_time - t < 3600]
            if len(recent_accesses) >= 5:  # 5+ accesses in last hour
                hot_keys.append(key)
        
        # Promote hot keys to memory if they're in disk cache
        for key in hot_keys:
            if key not in self.memory_cache and key in self.disk_index:
                entry = await self._get_from_disk(key)
                if entry:
                    await self._promote_to_memory(key, entry)
        
        if hot_keys:
            logger.info(f"🔥 Cache warming: promoted {len(hot_keys)} hot keys to memory")
    
    async def _load_disk_index(self):
        """Load disk cache index"""
        index_file = self.disk_cache_dir / "cache_index.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self.disk_index = json.load(f)
                
                # Calculate disk size
                self.disk_size = sum(metadata['size'] for metadata in self.disk_index.values())
                
                logger.info(f"📚 Loaded disk cache index: {len(self.disk_index)} entries, {self.disk_size/1024/1024:.1f}MB")
                
            except Exception as e:
                logger.error(f"❌ Failed to load disk cache index: {e}")
                self.disk_index = {}
    
    async def _save_disk_index(self):
        """Save disk cache index"""
        index_file = self.disk_cache_dir / "cache_index.json"
        
        try:
            with open(index_file, 'w') as f:
                json.dump(self.disk_index, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save disk cache index: {e}")
    
    async def close(self):
        """Close cache and cleanup"""
        self._running = False
        
        # Save disk index
        await self._save_disk_index()
        
        logger.info("✅ Smart Cache closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        return {
            'hits': self.stats.hits,
            'misses': self.stats.misses,
            'hit_rate': self.stats.hit_rate,
            'evictions': self.stats.evictions,
            'memory_usage_mb': self.stats.memory_usage_mb,
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(self.disk_index),
            'disk_size_mb': self.disk_size / (1024 * 1024),
            'avg_access_time_ms': self.stats.avg_access_time_ms,
            'total_size_bytes': self.stats.size_bytes
        }

# Global instance
smart_cache = None

async def get_smart_cache() -> SmartCache:
    """Get the global smart cache instance"""
    global smart_cache
    if smart_cache is None:
        smart_cache = SmartCache()
        await smart_cache.initialize()
    return smart_cache 