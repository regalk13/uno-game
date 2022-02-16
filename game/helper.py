import json
import math
import string
from json import JSONEncoder
import random
from django.conf import settings

def delete(objetc_)
    del object_

class Card:
    RED, BLUE, GREEN, YELLOW = "R", "B", "G", "Y"
    WILD, WILD_FOUR = "W", "WF"

    ZERO, ONE, TWO, THREE, FOUR = 0, 1, 2, 3, 4
    FIVE, SIX, SEVEN, EIGHT, NINE = 5, 6, 7, 8, 9
    SKIP, REVERSE, DRAW_TWO, NONE = 10, 11, 12, 13

    WILD_SCORE, ACTION_SCORE = 50, 20

    def __init__(self, category, number):
        self.category = category
        self.number = number

    def is_equivalent(self, card):
        return self.category == card.category and self.number == card.number

    def get_category(self):
        return self.category

    
    def get_number(self):
        return self.number

    def is_number_card(self):
        return self.number < 10  # 0 - 9 are number cards.

    def is_skip(self):
        return self.number == Card.SKIP

    def is_reverse(self):
        return self.number == Card.REVERSE

    def is_draw_two(self):
        return self.number == Card.DRAW_TWO

    def is_wild(self):
        return self.category == Card.WILD

    def is_wild_four(self):
        return self.category == Card.WILD_FOUR

    def show(self):
        return f"{self.number} of {self.category}"


class Deck:

        def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        """
        Method to build the Deck of Cards or Populate the Deck with Cards.
        :return:
        """
        for category in [Card.BLUE, Card.GREEN, Card.YELLOW, Card.RED]:
            self.cards.append(Card(category=category, number=Card.ZERO))

            for number in [Card.ONE, Card.TWO, Card.THREE, Card.FOUR, Card.FIVE, Card.SIX, Card.SEVEN, Card.EIGHT,
                           Card.NINE, Card.SKIP, Card.REVERSE, Card.DRAW_TWO]:
                self.cards.append(Card(category=category, number=number))
                self.cards.append(Card(category=category, number=number))

        for i in range(4):
            self.cards.append(Card(category=Card.WILD, number=Card.NONE))
            self.cards.append(Card(category=Card.WILD_FOUR, number=Card.NONE))

    def shuffle(self, times=1):
        """
        Method to Shuffle the Cards present in the Deck using Fisher Yates Shuffle algorithm.
        :return:
        """
        for _ in range(int(times)):
            for i in range(int(len(self.cards)) - 1, 0, -1):
                r = random.randint(0, i)
                self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def deal(self):
        """
        Method to draw a card
        :return:
        """
        return self.cards.pop()

    def show(self):
        for card in self.cards:
            card.show()
            
    def back_to_deck(self, card):
        self.cards.insert(0, card)


class PlayerServer:
    def __init__(self, username, rating_before_start):
               self.username = username
        self.rating_before_start = rating_before_start
        self.hand = []

        self.score = 0
        # self.rating_change = 0

        self.yelled_uno = False
        # self.seed = 0.0
        self.actual_rank = 0

    def draw(self, deck):
        drawn_card = deck.deal()
        self.hand.append(drawn_card)
        return drawn_card

    def get_hand_size(self):
        count = 0
        for card in self.hand:
            if card is not None:
                count += 1
        return count

    
    def __str__(self):
        return f"{self.username}"

    def get_hand(self):
        return self.hand

    def empty_hand(self, deck):
        for card in self.hand:
            if card is not None:
                deck.back_to_deck(card=card)
        self.hand = []

class GameServer:
    PUBLIC, PRIVATE = 0, 1
    PUBLIC_ROOM_LIMIT = 2
    AVAILABLE_PRIVATE_GAMES = []
    AVAILABLE_PUBLIC_GAMES = []



    def __init__(self, unique_id, player, game_type, league=None):
        self.unique_id = unique_id
        self.game_type = game_type
        self.admin_username = player.username
        self.players = []
        self.player_usernames = []
        self.players.append(player)
        self.player_usernames.append(player.username)
        self.deck = Deck()
        self.top_card = None
        self.top_color = None
        self.is_game_running = False
        self.direction = "+"
        self.current_player_index = 0
        self.previous_player_index = -1
        self.winner = None
    
    def __del__(self):
        print(f"Game with unique ID {self.unique_id} is deleted.")

    @classmethod
    def create_new_game(cls, unique_id, player, game_type):
        if game_type == cls.PUBLIC:
            for public_game in cls.AVAILABLE_PUBLIC_GAMES:
                if public_game.unique_id == unique_id:
                    if public_game.get_count_of_players() < 10:
                           print("Returning Existing Public Game.")
                        public_game.players.append(player)
                        public_game.player_usernames.append(player.username)
                        return public_game
                    return None
            print("Creating New Public Game.")
            new_public_game = GameServer(unique_id, player=player, game_type=game_type, league=league)
            cls.AVAILABLE_PUBLIC_GAMES.append(new_public_game)
            return new_public_game
