"""RSS collection scheduler using APScheduler."""
import logging
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from backend.app.core.database import SessionLocal
from backend.app.services.rss_collector import RSSCollector
from backend.app.models.source import Source
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()
executor = ThreadPoolExecutor(max_workers=5)


def collect_source_sync(source_id: int) -> dict:
    """Synchronously collect items from a source.
    
    This is a wrapper for the synchronous RSSCollector.collect_source method
    that can be executed in a thread pool.
    
    Args:
        source_id: Source ID to collect from
        
    Returns:
        Dictionary with source_id, count, and optional error
    """
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id, Source.is_active == True).first()
        if not source:
            return {"source_id": source_id, "count": 0, "error": "Source not found or inactive"}
        
        collector = RSSCollector(db)
        count = collector.collect_source(source)
        logger.info(f"[RSS] Collected {count} items from {source.title} (ID: {source_id})")
        return {"source_id": source_id, "count": count}
    except Exception as e:
        logger.error(f"[RSS] Error collecting source {source_id}: {e}", exc_info=True)
        return {"source_id": source_id, "count": 0, "error": str(e)}
    finally:
        db.close()


async def collect_all_active_sources():
    """Collect items from all active sources.
    
    This function runs synchronously in a thread pool to avoid blocking
    the async event loop with SQLAlchemy operations.
    """
    import asyncio
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.is_active == True).all()
        logger.info(f"[RSS] Starting collection for {len(sources)} active sources")
        
        # Collect all sources in parallel using thread pool
        loop = asyncio.get_event_loop()
        
        # Run in thread pool for async compatibility
        tasks = [
            loop.run_in_executor(executor, collect_source_sync, source.id)
            for source in sources
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log results
        successful = sum(1 for r in results if isinstance(r, dict) and "error" not in r)
        failed = len(results) - successful
        total_items = sum(r.get("count", 0) for r in results if isinstance(r, dict))
        
        logger.info(f"[RSS] Collection complete: {successful} successful, {failed} failed, {total_items} total items")
        
    except Exception as e:
        logger.error(f"[RSS] Error in collect_all_active_sources: {e}", exc_info=True)
    finally:
        db.close()


async def collect_arxiv_sources():
    """Collect items from arXiv sources only.
    
    arXiv feeds are updated once daily at midnight EST, so we check
    them less frequently than other sources.
    """
    import asyncio
    db = SessionLocal()
    try:
        # Filter arXiv sources (feed_url contains 'arxiv')
        sources = db.query(Source).filter(
            Source.is_active == True,
            Source.feed_url.ilike("%arxiv%")
        ).all()
        
        if not sources:
            logger.debug("[RSS] No active arXiv sources found")
            return
        
        logger.info(f"[RSS] Starting arXiv collection for {len(sources)} sources")
        
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, collect_source_sync, source.id)
            for source in sources
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if isinstance(r, dict) and "error" not in r)
        total_items = sum(r.get("count", 0) for r in results if isinstance(r, dict))
        
        logger.info(f"[RSS] arXiv collection complete: {successful} successful, {total_items} items")
        
    except Exception as e:
        logger.error(f"[RSS] Error in collect_arxiv_sources: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Start the RSS collection scheduler.
    
    Sets up two jobs:
    1. General sources: Collect every 20 minutes (configurable)
    2. arXiv sources: Collect twice daily (at 00:00 and 12:00 EST)
    """
    settings = get_settings()
    interval_minutes = settings.RSS_COLLECTION_INTERVAL_MINUTES
    
    # Job 1: Collect all active sources at regular intervals
    scheduler.add_job(
        collect_all_active_sources,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="rss_collection_all",
        name="Collect all active RSS sources",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping executions
    )
    
    # Job 2: Collect arXiv sources twice daily
    # Note: CronTrigger uses server timezone, adjust if needed
    scheduler.add_job(
        collect_arxiv_sources,
        trigger=CronTrigger(hour="0,12", minute=0),  # 00:00 and 12:00
        id="rss_collection_arxiv",
        name="Collect arXiv RSS sources",
        replace_existing=True,
        max_instances=1,
    )
    
    scheduler.start()
    logger.info(f"[RSS] Scheduler started with interval: {interval_minutes} minutes")
    logger.info("[RSS] arXiv collection scheduled at 00:00 and 12:00 daily")


def stop_scheduler():
    """Stop the RSS collection scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[RSS] Scheduler stopped")


def is_scheduler_running() -> bool:
    """Check if scheduler is running."""
    return scheduler.running

