#!/usr/bin/env python3
"""
Async Batch Processor
====================
High-performance batch processing system optimized for:
- Bulk message imports from Telegram
- Sporadic usage patterns
- Memory-efficient processing
- Intelligent batching and queuing
- Error recovery and retry mechanisms
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from collections import deque
import uuid
import traceback

logger = logging.getLogger(__name__)

@dataclass
class BatchJob:
    """Represents a batch processing job"""
    job_id: str
    job_type: str  # 'message_import', 'contact_analysis', 'data_export', etc.
    data: List[Any]
    processor_func: Callable
    batch_size: int = 100
    priority: int = 5
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed, retrying
    progress: int = 0
    total_items: int = 0
    processed_items: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatchResult:
    """Result of batch processing"""
    job_id: str
    success: bool
    processed_count: int
    error_count: int
    duration_seconds: float
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AsyncBatchProcessor:
    """High-performance async batch processor"""
    
    def __init__(self, max_concurrent_jobs: int = 3, max_batch_size: int = 1000):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_batch_size = max_batch_size
        
        # Job management
        self.job_queue = asyncio.PriorityQueue()
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        self.job_history_limit = 100
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.worker_semaphore = asyncio.Semaphore(max_concurrent_jobs)
        
        # Performance tracking
        self.stats = {
            'total_jobs_processed': 0,
            'total_items_processed': 0,
            'total_processing_time': 0.0,
            'average_throughput': 0.0,
            'active_jobs_count': 0,
            'pending_jobs_count': 0
        }
        
        # Memory management
        self.memory_threshold_mb = 500  # MB
        self.batch_size_adjustment = True
        self.adaptive_batching = True
        
        self._running = False
    
    async def start(self):
        """Start the batch processor"""
        if self._running:
            return
        
        self._running = True
        
        # Start worker tasks
        for i in range(self.max_concurrent_jobs):
            worker = asyncio.create_task(self._worker(f"worker_{i}"))
            self.workers.append(worker)
        
        # Start monitoring task
        asyncio.create_task(self._monitor_performance())
        
        logger.info(f"✅ Batch processor started with {self.max_concurrent_jobs} workers")
    
    async def stop(self):
        """Stop the batch processor"""
        if not self._running:
            return
        
        self._running = False
        
        # Wait for active jobs to complete
        while self.active_jobs:
            await asyncio.sleep(1)
        
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("✅ Batch processor stopped")
    
    async def submit_job(self, job_type: str, data: List[Any], processor_func: Callable,
                        batch_size: Optional[int] = None, priority: int = 5,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Submit a batch job for processing"""
        
        job_id = str(uuid.uuid4())
        
        # Determine optimal batch size
        if batch_size is None:
            batch_size = self._calculate_optimal_batch_size(len(data), job_type)
        
        job = BatchJob(
            job_id=job_id,
            job_type=job_type,
            data=data,
            processor_func=processor_func,
            batch_size=min(batch_size, self.max_batch_size),
            priority=priority,
            total_items=len(data),
            metadata=metadata or {}
        )
        
        # Add to queue (negative priority for max-heap behavior)
        await self.job_queue.put((-priority, job_id, job))
        
        self.stats['pending_jobs_count'] += 1
        
        logger.info(f"📦 Submitted batch job: {job_type} ({len(data)} items, batch_size={batch_size})")
        
        return job_id
    
    def _calculate_optimal_batch_size(self, total_items: int, job_type: str) -> int:
        """Calculate optimal batch size based on data size and type"""
        base_batch_size = 100
        
        # Adjust based on job type
        if job_type == "message_import":
            base_batch_size = 200
        elif job_type == "contact_analysis":
            base_batch_size = 50
        elif job_type == "ai_analysis":
            base_batch_size = 20
        
        # Adjust based on total items
        if total_items < 100:
            return min(total_items, 20)
        elif total_items < 1000:
            return min(base_batch_size, total_items // 5)
        else:
            return base_batch_size
    
    async def _worker(self, worker_id: str):
        """Worker task for processing jobs"""
        logger.info(f"🔄 Worker {worker_id} started")
        
        while self._running:
            try:
                # Get next job from queue
                try:
                    priority, job_id, job = await asyncio.wait_for(
                        self.job_queue.get(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                        continue
                
                # Acquire semaphore
                async with self.worker_semaphore:
                    await self._process_job(job, worker_id)
                
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
                
        logger.info(f"✅ Worker {worker_id} stopped")
    
    async def _process_job(self, job: BatchJob, worker_id: str):
        """Process a single job"""
        job.started_at = datetime.now()
        job.status = "running"
        self.active_jobs[job.job_id] = job
        
        self.stats['active_jobs_count'] += 1
        self.stats['pending_jobs_count'] -= 1
        
        logger.info(f"🚀 Worker {worker_id} processing job {job.job_type} ({job.total_items} items)")
        
        try:
            # Process data in batches
            processed_count = 0
            error_count = 0
            errors = []
            
            for batch_start in range(0, len(job.data), job.batch_size):
                if not self._running:
                    break
                
                batch_end = min(batch_start + job.batch_size, len(job.data))
                batch_data = job.data[batch_start:batch_end]
                
                try:
                    # Process batch
                    batch_result = await self._process_batch(job, batch_data, worker_id)
                    
                    processed_count += batch_result.get('processed', 0)
                    error_count += batch_result.get('errors', 0)
                    
                    if batch_result.get('error_messages'):
                        errors.extend(batch_result['error_messages'])
                    
                    # Update progress
                    job.processed_items = processed_count
                    job.progress = int((processed_count / job.total_items) * 100)
                    
                    # Adaptive batch size adjustment
                    if self.adaptive_batching:
                        await self._adjust_batch_size(job, batch_result)
                        
                except Exception as e:
                    error_count += len(batch_data)
                    errors.append(f"Batch {batch_start}-{batch_end}: {str(e)}")
                    logger.error(f"❌ Batch processing error: {e}")
                
                # Memory management
                if self.batch_size_adjustment:
                    await self._check_memory_usage(job)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
            
            # Job completed
            job.completed_at = datetime.now()
            job.status = "completed"
                
            # Create result
            duration = (job.completed_at - job.started_at).total_seconds()
            result = BatchResult(
                job_id=job.job_id,
                success=error_count == 0,
                processed_count=processed_count,
                error_count=error_count,
                duration_seconds=duration,
                errors=errors
            )
            
            await self._complete_job(job, result)
            
        except Exception as e:
            await self._handle_job_error(job, str(e))
    
    async def _process_batch(self, job: BatchJob, batch_data: List[Any], worker_id: str) -> Dict[str, Any]:
        """Process a single batch of data"""
        start_time = time.time()
        
        try:
            # Call the processor function
            if asyncio.iscoroutinefunction(job.processor_func):
                result = await job.processor_func(batch_data)
            else:
                result = job.processor_func(batch_data)
            
            processing_time = time.time() - start_time
            
            # Handle different result formats
            if isinstance(result, dict):
                return {
                    'processed': result.get('processed', len(batch_data)),
                    'errors': result.get('errors', 0),
                    'error_messages': result.get('error_messages', []),
                    'processing_time': processing_time
                }
            elif isinstance(result, tuple):
                # Assume (processed_count, error_count, error_messages)
                return {
                    'processed': result[0],
                    'errors': result[1] if len(result) > 1 else 0,
                    'error_messages': result[2] if len(result) > 2 else [],
                    'processing_time': processing_time
                }
            else:
                # Assume all items processed successfully
                return {
                    'processed': len(batch_data),
                    'errors': 0,
                    'error_messages': [],
                    'processing_time': processing_time
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Batch processor function error: {e}")
            return {
                'processed': 0,
                'errors': len(batch_data),
                'error_messages': [str(e)],
                'processing_time': processing_time
            }
    
    async def _adjust_batch_size(self, job: BatchJob, batch_result: Dict[str, Any]):
        """Dynamically adjust batch size based on performance"""
        processing_time = batch_result.get('processing_time', 0)
        
        # Target processing time per batch: 0.5-2.0 seconds
        target_time = 1.0
        
        if processing_time > 0:
            if processing_time < 0.5 and job.batch_size < self.max_batch_size:
                # Too fast, increase batch size
                job.batch_size = min(int(job.batch_size * 1.2), self.max_batch_size)
            elif processing_time > 2.0 and job.batch_size > 10:
                # Too slow, decrease batch size
                job.batch_size = max(int(job.batch_size * 0.8), 10)
    
    async def _check_memory_usage(self, job: BatchJob):
        """Check memory usage and adjust if needed"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.memory_threshold_mb:
                # Reduce batch size to conserve memory
                job.batch_size = max(int(job.batch_size * 0.7), 10)
                logger.warning(f"⚠️ High memory usage ({memory_mb:.1f}MB), reduced batch size to {job.batch_size}")
                
        except ImportError:
            # psutil not available, skip memory checking
            pass
        except Exception as e:
            logger.error(f"❌ Memory check error: {e}")
    
    async def _complete_job(self, job: BatchJob, result: BatchResult):
        """Complete a job and update statistics"""
        # Move to completed jobs
        self.completed_jobs[job.job_id] = job
        del self.active_jobs[job.job_id]
        
        # Update statistics
        self.stats['total_jobs_processed'] += 1
        self.stats['total_items_processed'] += result.processed_count
        self.stats['total_processing_time'] += result.duration_seconds
        self.stats['active_jobs_count'] -= 1
        
        # Calculate throughput
        if self.stats['total_processing_time'] > 0:
            self.stats['average_throughput'] = (
                self.stats['total_items_processed'] / self.stats['total_processing_time']
            )
        
        # Cleanup old job history
        while len(self.completed_jobs) > self.job_history_limit:
            jobs_with_completion = {
                jid: job for jid, job in self.completed_jobs.items() 
                if job.completed_at is not None
            }
            if jobs_with_completion:
                oldest_job_id = min(jobs_with_completion.keys(), 
                                  key=lambda jid: jobs_with_completion[jid].completed_at or datetime.now())
                del self.completed_jobs[oldest_job_id]
            else:
                # If no jobs have completion time, just remove the first one
                oldest_job_id = next(iter(self.completed_jobs))
                del self.completed_jobs[oldest_job_id]
        
        logger.info(f"✅ Job completed: {job.job_type} - {result.processed_count}/{job.total_items} items in {result.duration_seconds:.2f}s")
    
    async def _handle_job_error(self, job: BatchJob, error_message: str):
        """Handle job errors with retry logic"""
        job.error_message = error_message
        job.retry_count += 1
        
        if job.retry_count <= job.max_retries:
            # Retry job
            job.status = "retrying"
            logger.warning(f"⚠️ Job {job.job_type} failed, retrying ({job.retry_count}/{job.max_retries}): {error_message}")
            
            # Reduce batch size for retry
            job.batch_size = max(int(job.batch_size * 0.5), 10)
            
            # Re-queue with lower priority
            await self.job_queue.put((-job.priority + 1, job.job_id, job))
            
        else:
            # Max retries exceeded
            job.status = "failed"
            job.completed_at = datetime.now()
            
            self.completed_jobs[job.job_id] = job
            del self.active_jobs[job.job_id]
            self.stats['active_jobs_count'] -= 1
            
            logger.error(f"❌ Job {job.job_type} failed permanently after {job.max_retries} retries: {error_message}")
    
    async def _monitor_performance(self):
        """Monitor and log performance metrics"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                logger.info("📊 Batch Processor Performance:")
                logger.info(f"   Total Jobs: {self.stats['total_jobs_processed']}")
                logger.info(f"   Total Items: {self.stats['total_items_processed']}")
                logger.info(f"   Avg Throughput: {self.stats['average_throughput']:.1f} items/sec")
                logger.info(f"   Active Jobs: {self.stats['active_jobs_count']}")
                logger.info(f"   Pending Jobs: {self.stats['pending_jobs_count']}")
                
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        # Check active jobs
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                'job_id': job.job_id,
                'job_type': job.job_type,
                'status': job.status,
                'progress': job.progress,
                'processed_items': job.processed_items,
                'total_items': job.total_items,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'error_message': job.error_message
            }
        
        # Check completed jobs
        if job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
            duration = None
            if job.started_at and job.completed_at:
                duration = (job.completed_at - job.started_at).total_seconds()
            
            return {
                'job_id': job.job_id,
                'job_type': job.job_type,
                'status': job.status,
                'progress': job.progress,
                'processed_items': job.processed_items,
                'total_items': job.total_items,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'duration_seconds': duration,
                'error_message': job.error_message
            }
        
        return None
    
    async def list_jobs(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all jobs with optional status filter"""
        jobs = []
        
        # Active jobs
        for job in self.active_jobs.values():
            if status_filter is None or job.status == status_filter:
                jobs.append({
                    'job_id': job.job_id,
                    'job_type': job.job_type,
                    'status': job.status,
                    'progress': job.progress,
                    'total_items': job.total_items,
                    'created_at': job.created_at.isoformat(),
                    'started_at': job.started_at.isoformat() if job.started_at else None
                })
        
        # Completed jobs
        for job in self.completed_jobs.values():
            if status_filter is None or job.status == status_filter:
                jobs.append({
                    'job_id': job.job_id,
                    'job_type': job.job_type,
                    'status': job.status,
                    'progress': job.progress,
                    'total_items': job.total_items,
                    'created_at': job.created_at.isoformat(),
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None
                })
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jobs
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = "cancelled"
            job.completed_at = datetime.now()
            
            self.completed_jobs[job_id] = job
            del self.active_jobs[job_id]
            self.stats['active_jobs_count'] -= 1
            
            logger.info(f"🚫 Cancelled job: {job.job_type}")
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current processor statistics"""
        return self.stats.copy()

# Global instance
batch_processor = None

async def get_batch_processor() -> AsyncBatchProcessor:
    """Get the global batch processor instance"""
    global batch_processor
    if batch_processor is None:
        batch_processor = AsyncBatchProcessor()
        await batch_processor.start()
    return batch_processor 