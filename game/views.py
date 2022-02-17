from django.shortcuts import render, redirect, reverse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Player, id_generator
from .helper import GameServer

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

def enter_public_play(request):
    player = request.user
    if player.is_authenticated:
        if GameServer.AVAILABLE_PUBLIC_GAMES:
            for public_game in GameServer.AVAILABLE_PUBLIC_GAMES:
                if public_game.get_count_of_players() < MAX_JOINED_PLAYER_COUNT:
                    if not public_game.is_game_running:
                        active_unique_id = public_game.unique_id
                        return HttpResponseRedirect(
                            reverse('enter_game',
                                    kwargs={'game_type': GameServer.PUBLIC, 'unique_id': active_unique_id}
                                    ))
        active_unique_id = id_generator(10)
        return HttpResponseRedirect(
            reverse('enter_game', kwargs={'game_type': GameServer.PUBLIC, 'unique_id': active_unique_id}))
    
    else:
        return redirect('login')


def proceed_enter_game(request, game_type, unique_id):

    context = {
        "game_type": game_type,
        "unique_id": unique_id,
    }

    return render(request, 'game/info.html', context)


@login_required
def enter_game(request, game_type, unique_id):
    player = request.user
    context = {
        'game_type':game_type,
        'unique_id': unique_id,
    }
    return render(request, 'game/enter_game.html', context)
