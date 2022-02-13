from django.urls import path
from . import views

urlpatterns = [
    path('game-now/', views.game_now, name="game-now"),
    

]
