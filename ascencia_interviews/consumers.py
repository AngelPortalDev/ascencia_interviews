# # app/consumers.py
# import json
# import os
# from channels.generic.websocket import AsyncWebsocketConsumer
# import websockets
# import asyncio
# # from dotenv import load_dotenv
# from django.conf import settings

# import logging

# logger = logging.getLogger('user_activity_logger')

# # load_dotenv()

# class AudioStreamConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         token = settings.DEEPGRAM_API_KEY
#         print("Deepgram API Token:", token)
#         headers = [("Authorization", f"Token {settings.DEEPGRAM_API_KEY}")]
#         self.deepgram_ws = await websockets.connect(
#             "wss://api.deepgram.com/v2/listen?"
#             "model=flux-general-en&"
#             "language=en&",
#             extra_headers=headers,
#         )
#         async def receive_deepgram():
            
#             async for message in self.deepgram_ws:
#                 msg = json.loads(message)
#                 transcript = msg.get("channel", {}).get("alternatives", [{}])[0].get("transcript")
#                 if transcript:
#                     await self.send(json.dumps({"text": transcript}))

#         self.receive_task = asyncio.create_task(receive_deepgram())

#     async def disconnect(self, close_code):
#         if self.deepgram_ws:
#             await self.deepgram_ws.close()
#         if self.receive_task:
#             self.receive_task.cancel()

#     async def receive(self, text_data=None, bytes_data=None):
#         if self.deepgram_ws and bytes_data:
#             await self.deepgram_ws.send(bytes_data)


import json
import asyncio
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer

import logging

logger = logging.getLogger('zoho_webhook_logger')

ASSEMBLY_API_KEY = "6af9609039af426f822ac6a728aa94b3"

class TranscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f" WebSocket path received: '{self.scope['path']}'")
        
        logger.info(f" Full scope: {self.scope}")
        await self.accept()
        logger.info(" Browser connected")
        
        # Initialize buffer
        self.audio_buffer = bytearray()
        self.SAMPLE_RATE = 16000
        self.BYTES_PER_SAMPLE = 2
        self.MIN_CHUNK_SIZE = int((self.SAMPLE_RATE * self.BYTES_PER_SAMPLE * 100) / 1000)
        
        # Connect to AssemblyAI with proper headers
        streaming_url = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&encoding=pcm_s16le&speech_model=universal-streaming-english"
        
        try:
            # Create headers dict
            headers = {"Authorization": ASSEMBLY_API_KEY}
            
            # Connect with additional_headers parameter (not extra_headers)
            self.assembly_ws = await websockets.connect(
                streaming_url,
                additional_headers=headers
            )
            # print(" AssemblyAI connected")
            logger.info(" AssemblyAI connected")
            
            # Start listening for transcriptions
            asyncio.create_task(self.receive_from_assembly())
            
        except Exception as e:
            logger.info(f" Failed to connect to AssemblyAI: {e}")
            await self.close()

    async def disconnect(self, close_code):
        logger.info("Browser disconnected")
        
        # Send remaining audio
        if len(self.audio_buffer) > 0 and hasattr(self, 'assembly_ws'):
            try:
                await self.assembly_ws.send(bytes(self.audio_buffer))
                self.audio_buffer = bytearray()
            except:
                pass
        
        # Close AssemblyAI connection
        if hasattr(self, 'assembly_ws'):
            try:
                await self.assembly_ws.send(json.dumps({"type": "TerminateSession"}))
                await self.assembly_ws.close()
            except:
                pass

    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data and hasattr(self, 'assembly_ws'):
            # Accumulate audio data
            self.audio_buffer.extend(bytes_data)
            
            # Send chunks of at least 100ms
            while len(self.audio_buffer) >= self.MIN_CHUNK_SIZE:
                chunk_to_send = bytes(self.audio_buffer[:self.MIN_CHUNK_SIZE])
                self.audio_buffer = self.audio_buffer[self.MIN_CHUNK_SIZE:]
                
                try:
                    await self.assembly_ws.send(chunk_to_send)
                except Exception as e:
                    logger.info(f"Error sending audio: {e}")

    async def receive_from_assembly(self):
        """Listen for messages from AssemblyAI"""
        try:
            async for message in self.assembly_ws:
                data = json.loads(message)
                
                if data.get("type") == "SessionBegins":
                    logger.info(f"Session started: {data.get('id')}")
                    
                elif data.get("type") == "Turn":
                    if data.get("transcript"):
                        message_type = "final" if data.get("end_of_turn") else "partial"
                        
                        # Send to browser
                        await self.send(text_data=json.dumps({
                            "text": data.get("transcript"),
                            "type": message_type,
                            "confidence": data.get("end_of_turn_confidence"),
                            "end_of_turn": data.get("end_of_turn")
                        }))
                        
                        if data.get("end_of_turn"):
                            logger.info(f" Turn completed: {data.get('transcript')}")
                            
                elif data.get("type") == "SessionTerminated":
                    logger.info(" Session terminated")
                    
        except Exception as e:
            logger.info(f"Error receiving from AssemblyAI: {e}")