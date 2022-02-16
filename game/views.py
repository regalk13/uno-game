from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room

ERROR = "error"
SUCCESS = "success"
MAX_JOINED_PLAYER_COUNT = 10
MINIMUM_ONLINE_PLAYER_REQUIRED = 3


@login_required(login_url='login')
def game_now(request):
    player = request.user
    if not player.is_authenticated:
        message = f"You need to login first!"
        return redirect('login')
   
    public_rooms =  Room.objects.filter(type=0)
    
    context = {
        "public_rooms": public_rooms
    }
    return render(request, 'game/game-now.html', context) 


