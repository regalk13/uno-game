from django.urls import path

from .consumers import GameRoomConsumer




ws_urlpatterns = [
    path('game/enter_room/<str:game_type>/<str:unique_id>/', GameRoomConsumer.as_asgi())
]
