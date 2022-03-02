import json
import asyncio
from random import randint
from time import sleep
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer
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
        
        self.game = GameServer.create_new_game(unique_id=self.unique_id, player=self.player_server_obj, game_type=self.game_type)

        if self.game is None:
            return
        
        await self.channel_layer.group_add(
            self.game_room_id,
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept"
        })
        
    
    async def websocket_receive(self, event):
        front_text = event.get('text', None)
        forced_draw_data = None  # If some player had to draw cards due to DRAW_TWO or WILD_FOUR.
        voluntary_draw_data = None  # When player voluntary drew a card.
        won_data = None  # When player has played all his cards.
        caught_data = None  # When a player didn't call uno and got caught. Stores cards drawn by that player.
        time_out_data = None  # When a player has exhausted his/her limit to play a card.
        if front_text:
            loaded_dict_data = json.loads(front_text)
            type_of_event = loaded_dict_data['type']
            text_of_event = loaded_dict_data['text']

            if type_of_event == "start.game":
                # print(f"Before Broadcasting: Going to call start.game")
                print("Starting game...")
                self.game.start_game()


                # This can be called by Friend Game only.
                if self.game.game_type == GameServer.PRIVATE:
                    GameServer.PRIVATE.remove(self.game)
                if self.game.game_type == GameServer.PUBLIC:
                    GameServer.AVAILABLE_PUBLIC_GAMES.remove(self.game)


            elif type_of_event == "end.game":
                # await self.create_game_history()
                self.game.end_game()
            elif type_of_event == "play.card":
                client_data = text_of_event['data']
                server_data = {
                    "username": self.me.username,
                }
                returned_data = None
                if self.game.is_valid_play_move(client_data=client_data, server_data=server_data):
                    returned_data = self.game.play_card(client_data=client_data)
                    if returned_data:
                        if returned_data['status'] == "won":
                            won_data = returned_data
                            winner_username = won_data['username']
                            winner_score = int(won_data['score'])
                            if winner_score >= GameServer.WINNING_SCORE:
                                text_of_event['status'] = "won_game"
                                type_of_event = "won_game"

                                for player_obj in self.game.players:
                                    if player_obj.username == winner_username:
                                        await self.handle_winning_game(winner_player_obj=player_obj)
                                    else:
                                        await self.handle_losing_game(loser_player_obj=player_obj)

                                # Creating Game History in Database
                                await self.create_game_history()

                                print(f"End Game. {winner_username} has scored winning points.")
                            else:
                                text_of_event['status'] = "won_round"
                                type_of_event = "won_round"

                                await self.handle_winning_round(winner_username=winner_username)

                                print(f"This round ended. Get ready for next round.")

                        elif returned_data['status'] == "skipped":
                            forced_draw_data = returned_data
                else:
                    # Handle Cheating
                    cheating_response = {
                        "status": "cheating",
                        "message": "Trying to play Illegal Move",
                        "data": {
                            "username": str(self.me.username),
                        }
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(cheating_response),
                    })
                    return
            elif type_of_event == "voluntary_draw_card":  # When current player clicked on deck to draw the card.
                client_data = text_of_event['data']
                server_data = {
                    "username": self.me.username,
                }
                if self.game.is_valid_draw_move(client_data=client_data, server_data=server_data):
                    voluntary_draw_data = self.game.draw_card()
                else:
                    # Handle Cheating
                    cheating_response = {
                        "status": "cheating",
                        "message": "Trying to play Illegal Move",
                        "data": {
                            "username": str(self.me.username),
                        }
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(cheating_response),
                    })
                    return
            elif type_of_event == "keep.card":  # Player kept the card after drawing.
                client_data = text_of_event['data']
                server_data = {
                    "username": self.me.username,
                }
                # Note: Here is_valid_draw_move will work fine to check if this is valid person.
                if self.game.is_valid_draw_move(client_data=client_data, server_data=server_data):
                    self.game.keep_card()
            elif type_of_event == "call.uno":  # Player called UNO.
                client_data = text_of_event['data']
                server_data = {
                    "username": self.me.username,
                }
                # If this player can call UNO.
                if self.game.can_call_uno(client_data=client_data, server_data=server_data):
                    self.game.call_uno(client_data=client_data)
                else:
                    text_of_event['status'] = "failed_call_uno"
                    print(f"Cannot call UNO!")
            elif type_of_event == "catch.player":  # When someone catches a player who forgot to say UNO!
                client_data = text_of_event['data']
                server_previous_player = self.game.get_previous_player()
                if server_previous_player is not None:
                    server_data = {
                        "caught": server_previous_player.username,
                        "catcher": self.me.username,
                    }
                    if self.game.is_valid_catch(client_data=client_data, server_data=server_data):
                        caught_data = self.game.catch_player()
                    else:
                        text_of_event['status'] = "failed_catch_player"
                        print("Cannot catch.")
                else:  # No one has played any card yet.
                    text_of_event['status'] = "failed_catch_player"
                    print("Cannot catch.")
            elif type_of_event == "time.out":
                client_data = text_of_event['data']
                server_data = {
                    "username": self.me.username,
                }
                if self.game.can_time_out(client_data=client_data, server_data=server_data):
                    time_out_data = self.game.time_out()

            if self.game is not None:
                game_data = json.dumps(self.game.prepare_client_data(), cls=CustomEncoder)
            else:
                game_data = None

            response = {
                "status": text_of_event['status'],
                "message": text_of_event['message'],
                "data": text_of_event['data'],
                "gameData": game_data,
            }

            if type_of_event == "won_game":
                extra_data = {
                    "wonGameData": json.dumps(self.game.players, cls=CustomEncoder)
                }
                response.update(extra_data)
                self.game.end_game()

            if time_out_data:
                extra_data = {
                    "timeOutData": time_out_data,
                }
                response.update(extra_data)

            if caught_data:
                extra_data = {
                    "caughtData": caught_data,
                }
                response.update(extra_data)

            if won_data:
                extra_data = {
                    "wonData": won_data,
                }
                response.update(extra_data)

            if voluntary_draw_data:
                extra_data = {
                    "voluntaryDrawData": voluntary_draw_data,
                }
                response.update(extra_data)

            if forced_draw_data:
                extra_data = {
                    "forcedDrawData": forced_draw_data,
                }
                response.update(extra_data)
                response['status'] = "forced_draw_card"
                type_of_event = "forced_draw_card"

            await self.channel_layer.group_send(
                self.game_room_id,
                {
                    "type": type_of_event,
                    "text": json.dumps(response)
                }
            )

            if type_of_event == "user.new":
                if self.game.game_type == GameServer.PRIVATE:
                    if self.game.get_count_of_players() == 10:
                        GameServer.PRIVATE.remove(self.game)

    async def user_new(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def time_out(self, event):
        text = json.loads(event['text'])
        data = text['data']
        time_out_data = text['timeOutData']
        if data['username'] != self.me.username:
            time_out_data['drawnCards'] = []
        response = {
            "status": text['status'],
            "message": text['message'],
            "data": text['data'],
            "gameData": text['gameData'],
            "timeOutData": time_out_data,
        }
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(response),
        })
        
    
    async def websocket_disconnect(self, event):
        print("disconnected", event)
        # Leaving current Game
        if self.game is not None:
            me = self.me
            self.game.leave_game(self.player_server_obj)
            del self.player_server_obj
            response = {
                "status": "user_left_room",
                "message": "Disconnecting...",
                "data": {
                    "left_user_username": me.username,
                    "game_room_unique_id": self.game_room_id
                },
                "gameData": json.dumps(self.game.prepare_client_data(), cls=CustomEncoder)
            }
            await self.channel_layer.group_send(
                self.game_room_id,
                {
                    "type": "user_left_room",
                    "text": json.dumps(response)
                }
            )

            await self.channel_layer.group_discard(
                self.game_room_id,
                self.channel_name
            )


    async def user_left_room(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text'],
        })
    async def start_game(self, event):
        text = event.get('text', None)
        if text:
            loaded_dict_data = json.loads(text)
            extra_data = {
                "serializedPlayer": json.dumps(self.player_server_obj, cls=CustomEncoder),
            }
            loaded_dict_data.update(extra_data)
            await self.send({
                "type": "websocket.send",
                "text": json.dumps(loaded_dict_data)
            })
