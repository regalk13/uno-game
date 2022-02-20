from django.urls import path

from .consumers import WSConsumer




ws_urlpatterns = [
    path('game/enter_room/<str:game_type>/<str:unique_id>/', WSConsumer.as_asgi())
]
