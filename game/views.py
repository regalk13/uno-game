from django.shortcuts import render, redirect, reverse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Player, id_generator
from .helper import GameServer
from channels.layers import get_channel_layer
ERROR = "error"
SUCCESS = "success"
MAX_JOINED_PLAYER_COUNT = 10
MINIMUM_ONLINE_PLAYER_REQUIRED = 3

channel_layer = get_channel_layer()

def broadcast_notification(group_name, message):
    """
        Helper Function to Broadcast Notifications in Game Room.
    :param group_name: Name of Group in which event should be broadcast.
    :param message: Notification Message.
    :return:
    """
    text = {
        "status": "broadcast_notification",
        "message": message,
    }
    group_name = f"game_room_{group_name}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "broadcast.notification",
            "text": json.dumps(text)
        }
    )


@login_required(login_url='login')
def game_now(request):
    player = request.user
    game_select = 1
    if not player.is_authenticated:
        message = f"You need to login first!"
        return redirect('login')
    if request.method == 'POST':
        if request.POST.getlist('public'):
            game_select = 0
        else:
            game_select = 1
        name = request.POST.get('name')
        unique_id = id_generator(10)
        return HttpResponseRedirect(
            reverse('enter_game', kwargs={'game_type': game_select, 'unique_id': unique_id})
        )

    if request.method == 'GET':
        unique_id = request.GET.get('unique_id')
        if unique_id:
            for private_game in GameServer.AVAILABLE_PRIVATE_GAMES:
                if unique_id == private_game.unique_id:
                    if private_game.get_count_of_players() < MAX_JOINED_PLAYER_COUNT:
                        if not private_game.is_game_running:
                            return HttpResponseRedirect(
                                reverse('enter_game', kwargs={'game_type': GameServer.PRIVATE, 'unique_id': unique_id}))
            
            for public_game in GameServer.AVAILABLE_PUBLIC_GAMES:
                print(public_game.admin_username)
                if unique_id == public_game.unique_id:
                    if public_game.get_count_of_players() < MAX_JOINED_PLAYER_COUNT:
                        if not public_game.is_game_running:
                            return HttpResponseRedirect(
                                reverse('enter_game', kwargs={'game_type': GameServer.PUBLIC, 'unique_id': unique_id}))
    
    context = {
        "public_rooms": GameServer.AVAILABLE_PUBLIC_GAMES
    }

    return render(request, 'game/game-now.html', context) 

def enter_public_play(request, unique_id):
    player = request.user
    if player.is_authenticated:
        if GameServer.AVAILABLE_PUBLIC_GAMES:
            for public_game in GameServer.AVAILABLE_PUBLIC_GAMES:
                if unique_id == public_game.unique_id:
                    if public_game.get_count_of_players() < MAX_JOINED_PLAYER_COUNT:
                        if not public_game.is_game_running:
                                return HttpResponseRedirect(
                                    reverse('enter_game',
                                            kwargs={'game_type': GameServer.PUBLIC, 'unique_id': unique_id}))
        # If no Public Game Room Available, create new.
        active_unique_id = id_generator(10)
        return HttpResponseRedirect(
            reverse('enter_game', kwargs={'game_type': GameServer.PUBLIC, 'unique_id': active_unique_id}))
    else:
        return redirect('login')

@login_required
def enter_game(request, game_type, unique_id):
    player = request.user
    context = {
        'game_type':game_type,
        'unique_id': unique_id,
    }
    return render(request, 'game/enter_game.html', context)
