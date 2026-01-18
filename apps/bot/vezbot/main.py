"""Bot entry point."""

import asyncio
import signal
import sys
from typing import Any

from vezbot.bot import bot
from vezbot.config import settings
from vezbot.database import close_db, init_db
from vezbot.utils.logging import configure_logging, get_logger

# Import API for Railway (runs alongside bot)
try:
    from vezbot.api.main import app
    import uvicorn
except ImportError:
    app = None
    uvicorn = None

logger = get_logger(__name__)


async def main() -> None:
    """Main entry point."""
    # Configure logging
    configure_logging(settings.log_level)

    logger.info("Starting Vezbot...")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Start FastAPI server in background (for webhooks)
    if app and uvicorn:
        import threading
        def run_api():
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        logger.info("API server started on port 8000")

    # Start bot
    try:
        await bot.start(settings.discord_token)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await close_db()
        await bot.close()


def signal_handler(sig: int, frame: Any) -> None:
    """Handle shutdown signals."""
    logger.info("Received shutdown signal")
    asyncio.create_task(bot.close())
    asyncio.create_task(close_db())


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
