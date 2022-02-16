from django.db import models
from django.conf import settings 
from django.utils import timezone
from home.models import User
import random 
import string


class GameHistory(models.Model):
    PUBLIC, CUSTOM = "public", "custom"
    game_choices = (
        (PUBLIC, "Public"),
        (CUSTOM, "Custom"),
    )

    unique_game_id = models.CharField(max_length=10, verbose_name="Unique ID", unique=True, default=None)

    concluded_at = models.DateTimeField(verbose_name="Concluded At", default=timezone.now)

    game_type = models.CharField(max_length=30, default=PUBLIC, choices=game_choices, verbose_name="Game Type")

    winner_username = models.CharField(max_length=255, verbose_name="Winner Username")

    def __str__(self):
        return f"{self.unique_game_id}"

class Participant(models.Model):
    game_room = models.ForeignKey(GameHistory, verbose_name="Game Room", on_delete=models.CASCADE)
    user = models.ManyToManyField(User, related_name="user", blank=True)
    score = models.IntegerField(default=0, verbose_name="Score")



def id_generator(size):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(size))



class Room(models.Model):
    PUBLIC, PRIVATE = 0, 1
    type_choices = (
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
    )
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default="New Public Game")


    unique_game_id = models.CharField(max_length=10, verbose_name="Unique ID", unique=True, default=None)

    is_game_running = models.BooleanField(default=False, verbose_name="Is Game Running")

    players_count = models.IntegerField(default=0, verbose_name="Joined Player Count")

    type = models.PositiveSmallIntegerField(default=PUBLIC, choices=type_choices, verbose_name="Type")
    
    def save(self, *args, **kwargs):
        if self.unique_game_id is None:
            self.unique_game_id = f"{id_generator(10)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_game_id}-{self.admin.username}"


class Player(models.Model):

    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Player")

    game_room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Game Room")

    is_online = models.BooleanField(default=False, verbose_name="Is Online")

    def __str__(self):
        return f"P:{self.player.username}_G:{self.game_room}"

class Card(models.Model):
    RED = "R"
    BLUE = "B"
    GREEN = "G"
    YELLOW = "Y"
    WILD = "W"
    WILD_FOUR = "WF"

    category_options = (
        (RED, "Red"),
        (BLUE, "Blue"),
        (GREEN, "Green"),
        (YELLOW, "Yellow"),
        (WILD, "Wild"),
        (WILD_FOUR, "Wild Four"),
    )

    category = models.CharField(max_length=2, choices=category_options, verbose_name="Category")

    ZERO, ONE, TWO, THREE, FOUR = 0, 1, 2, 3, 4
    FIVE, SIX, SEVEN, EIGHT, NINE = 5, 6, 7, 8, 9
    SKIP, REVERSE, DRAW_TWO, NONE = 10, 11, 12, 13

    number_option = (
        (NONE, "None"),  # For WILD and WILD_FOUR Cards
        (ZERO, "Zero"), (ONE, "One"), (TWO, "Two"), (THREE, "Three"), (FOUR, "Four"),
        (FIVE, "Five"), (SIX, "Six"), (SEVEN, "Seven"), (EIGHT, "Eight"), (NINE, "Nine"),
        (SKIP, "Skip"), (DRAW_TWO, "Draw Two"), (REVERSE, "Reverse"),
    )
    number = models.PositiveSmallIntegerField(choices=number_option, verbose_name="Number")

    def __str__(self):
        return f"{self.category}_{self.number}"
