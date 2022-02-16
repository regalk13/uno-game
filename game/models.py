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

