import asyncio
import aiohttp
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self):
        self.ping_url = settings.KEEP_ALIVE_URL or f"http://{settings.API_HOST}:{settings.API_PORT}/health"
        self.interval = settings.KEEP_ALIVE_INTERVAL
        self.enabled = settings.KEEP_ALIVE_ENABLED
        self.is_running = False
        self.task = None
    
    async def ping_server(self):
        """Ping the server to keep it alive"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.ping_url, timeout=3) as response:
                    if response.status == 200:
                        logger.debug(f"Keep-alive ping successful: {response.status}")
                    else:
                        logger.warning(f"Keep-alive ping returned: {response.status}")
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")
    
    async def start_keep_alive(self):
        """Start the keep-alive ping loop"""
        self.is_running = True
        logger.info(f"Starting keep-alive service - pinging {self.ping_url} every {self.interval} seconds")
        
        while self.is_running:
            await self.ping_server()
            await asyncio.sleep(self.interval)
    
    def start(self):
        """Start keep-alive as background task"""
        if not self.enabled:
            logger.info("Keep-alive service is disabled")
            return
            
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.start_keep_alive())
            logger.info("Keep-alive service started")
    
    def stop(self):
        """Stop the keep-alive service"""
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
            logger.info("Keep-alive service stopped")

# Global instance
keep_alive_service = KeepAliveService()