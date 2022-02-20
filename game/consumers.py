import json
import asyncio
from random import randint
from time import sleep
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer

class WSConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })
        

        for i in range(1000):
            await self.send({
                "type": "websocket.send",
                "text": json.dumps({'message': randint(1,100)})
            })
            await asyncio.sleep(10)


