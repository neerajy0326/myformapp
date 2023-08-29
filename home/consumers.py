
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async  # Import for asynchronous database operations
import logging

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
      if not self.scope["user"].is_authenticated:
        await self.close()
      else:
        await self.accept()
        print(f"WebSocket connection established with user {self.scope['user']}")

    async def disconnect(self, close_code):
      print(f"WebSocket connection closed with user {self.scope['user']}")
      pass


    @database_sync_to_async
    def save_chat_message(self, sender_id, receiver_id, message):
        
        from .models import ChatMessage
        return ChatMessage.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=message
        )

    async def receive(self, text_data):
      data = json.loads(text_data)
      message = data['message']
      sender_id = data['sender_id']
      receiver_id = data['receiver_id']
      
      logger = logging.getLogger(__name__)
      logger.info(f"Received message: {message}, sender_id: {sender_id}, receiver_id: {receiver_id}")
   
      await self.save_chat_message(sender_id, receiver_id, message)

    # Send the message to the receiver
      await self.send(text_data=json.dumps({
        'message': message,
        'sender_id': sender_id,
        'receiver_id': receiver_id
     }))