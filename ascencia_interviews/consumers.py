# app/consumers.py
import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
import websockets
import asyncio
# from dotenv import load_dotenv
from django.conf import settings

import logging

logger = logging.getLogger('user_activity_logger')

# load_dotenv()

class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        token = settings.DEEPGRAM_API_KEY
        headers = [("Authorization", f"Token {settings.DEEPGRAM_API_KEY}")]
        self.deepgram_ws = await websockets.connect(
        "wss://api.deepgram.com/v1/listen?punctuate=true&model=nova-3&smart_format=true&language=en-US&endpointing=300&no_delay=true&numerals=true",
        extra_headers=headers
        )
        async def receive_deepgram():
            
            async for message in self.deepgram_ws:
                msg = json.loads(message)
                transcript = msg.get("channel", {}).get("alternatives", [{}])[0].get("transcript")
                if transcript:
                    await self.send(json.dumps({"text": transcript}))

        self.receive_task = asyncio.create_task(receive_deepgram())

    async def disconnect(self, close_code):
        if self.deepgram_ws:
            await self.deepgram_ws.close()
        if self.receive_task:
            self.receive_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        if self.deepgram_ws and bytes_data:
            await self.deepgram_ws.send(bytes_data)
