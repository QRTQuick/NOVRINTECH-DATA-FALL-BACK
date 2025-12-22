import asyncio
import aiohttp
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self):
        # Use external URL for Render deployment
        self.ping_url = "https://novrintech-data-fall-back.onrender.com/health"
        self.interval = 4  # 4 seconds
        self.enabled = True
        self.is_running = False
        self.task = None
    
    async def ping_server(self):
        """Ping the server to keep it alive"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.ping_url, timeout=3) as response:
                    if response.status == 200:
                        print(f"✅ Keep-alive ping successful: {response.status} at {asyncio.get_event_loop().time()}")
                    else:
                        print(f"⚠️ Keep-alive ping returned: {response.status}")
        except Exception as e:
            print(f"❌ Keep-alive ping failed: {e}")
    
    async def start_keep_alive(self):
        """Start the keep-alive ping loop"""
        self.is_running = True
        print(f"🔄 Starting keep-alive service - pinging {self.ping_url} every {self.interval} seconds")
        
        while self.is_running:
            await self.ping_server()
            await asyncio.sleep(self.interval)
    
    def start(self):
        """Start keep-alive as background task"""
        if not self.enabled:
            print("⚠️ Keep-alive service is disabled")
            return
            
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.start_keep_alive())
            print("🚀 Keep-alive service started")
    
    def stop(self):
        """Stop the keep-alive service"""
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
            print("⏹️ Keep-alive service stopped")

# Global instance
keep_alive_service = KeepAliveService()