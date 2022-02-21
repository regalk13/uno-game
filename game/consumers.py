import json
import asyncio
from random import randint
from time import sleep
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer

from home.models import User
from .models import GameHistory, Participant
from .helper import Card, PlayerServer, GameServer, Deck, CustomEncoder

class GameRoomConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.me = self.scope['user']

        self.unique_id = self.scope['url_route']['kwargs']['unique_id']

        self.game_type = int(self.scope['url_route']['kwargs']['game_type'])
        
        self.game_room_id = f"game_room_{self.unique_id}"

        self.player_server_obj = PlayerServer(username=self.me.username) 
        
        self.game = GameServer.create_new_game(unique_id=self.unique_id, player=User, game_type=self.game_type)

        if self.game is None:
            # Connection is rejected because this room is already full.
            return

        await self.send({
            "type": "websocket.accept"
        })
        

        await self.send({
            "type": "websocket.send",
            "text": json.dumps({'message': self.me.username})
        })

