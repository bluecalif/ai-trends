"""Worker process for running the scheduler standalone.

This script runs only the scheduler without the FastAPI server.
Useful for deployment scenarios where the scheduler needs to run
in a separate process (e.g., Railway, Render, Fly.io).

Run:
  poetry run python -m backend.scripts.worker
"""
import sys
import io
import signal
import logging

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.app.core.scheduler import start_scheduler, stop_scheduler
from backend.app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, stopping scheduler...")
    stop_scheduler()
    sys.exit(0)


def main():
    """Main entry point for the worker process."""
    settings = get_settings()
    logger.info(f"[Worker] Starting scheduler worker...")
    logger.info(f"[Worker] DATABASE_URL={settings.DATABASE_URL}")
    logger.info(f"[Worker] RSS_COLLECTION_INTERVAL_MINUTES={settings.RSS_COLLECTION_INTERVAL_MINUTES}")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the scheduler
        start_scheduler()
        logger.info("[Worker] Scheduler started successfully")
        
        # Keep the process alive
        # The scheduler runs in background threads, so we just wait
        import time
        while True:
            time.sleep(60)  # Sleep for 1 minute and check again
            
    except KeyboardInterrupt:
        logger.info("[Worker] Keyboard interrupt received")
    except Exception as e:
        logger.error(f"[Worker] Fatal error: {e}", exc_info=True)
    finally:
        stop_scheduler()
        logger.info("[Worker] Worker process stopped")


if __name__ == "__main__":
    main()

