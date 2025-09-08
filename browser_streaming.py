#!/usr/bin/env python3
"""
Browser Streaming for Live Environment
Streams browser actions in real-time (experimental)
"""

import asyncio
import websockets
import json
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class BrowserStreamer:
    def __init__(self):
        self.connected_clients = set()
        
    async def register_client(self, websocket, path):
        """Register a new client for streaming"""
        self.connected_clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
    
    async def broadcast_screenshot(self, screenshot_data, action_info):
        """Broadcast screenshot to all connected clients"""
        if self.connected_clients:
            message = {
                'type': 'screenshot',
                'data': screenshot_data,
                'action': action_info,
                'timestamp': time.time()
            }
            
            # Send to all connected clients
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected
    
    def setup_streaming_browser(self):
        """Setup browser with streaming capabilities"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    async def stream_action(self, driver, action_name):
        """Stream a browser action"""
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode()
        
        # Broadcast to clients
        await self.broadcast_screenshot(screenshot_b64, {
            'action': action_name,
            'url': driver.current_url,
            'title': driver.title
        })

# This would require additional setup and may not work on Railway
# due to WebSocket limitations and port restrictions
