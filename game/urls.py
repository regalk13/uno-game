from django.urls import path
from . import views

urlpatterns = [
    path('game-now/', views.game_now, name="game-now"),
   
    path('enter_room/<str:game_type>/<str:unique_id>/', views.enter_game, name="enter_game"),
    path('public/enter_room/<str:unique_id>/', views.enter_public_play, name="enter_public_play"),
]
