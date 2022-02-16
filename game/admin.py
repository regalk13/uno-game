from django.contrib import admin
from .models import GameHistory, Participant, Room, Player, Card
# Register your models here

admin.site.register(GameHistory)
admin.site.register(Participant)
admin.site.register(Room)
admin.site.register(Player)
admin.site.register(Card)
