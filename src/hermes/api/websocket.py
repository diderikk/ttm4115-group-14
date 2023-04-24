# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

async def send_to_group(group_name, message):
		await channel_layer.group_send(
				group_name,
				{
						"type": "broadcast",
						"message": message,
				},
		)
  

async def broadcast_message(message):
    """
    Handler for message type 'broadcast'. 
    Broadcasts the message to all active websocket connections.
    """
    await channel_layer.group_send("test", {"type": "broadcast", "message": message})
  


class WebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'message',
                'message': message
            }
        )
        
    async def send_to_room(self, text_data, room):
      channel_layer = get_channel_layer()
      await channel_layer.group_send(
				room,
				{
					'type': 'broadcast',
					'message': text_data
				}
			)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    async def broadcast(self, event):
      message = event['message']
      
      await self.send(text_data=json.dumps({
            'broadcast': message
      }))
