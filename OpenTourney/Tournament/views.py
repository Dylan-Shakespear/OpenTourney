import sys
from django.shortcuts import render
from .models import TournamentObject
from .utils import Rounds


def home(request):
    return render(request, 'Tournament/home.html', {})


def tourney(request):
    return render(request, 'Tournament/tourney.html', {})


def tourney_main(request, tourney_id):
    this_tourney = TournamentObject.objects.get(pk=tourney_id)
    rounds = Rounds(this_tourney)
    context = {
        'tourney': this_tourney,
        'rounds': rounds,
    }
    return render(request, 'Tournament/tourney.html', context)


def new_tourney(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        tournament_type = request.POST.get('type', '')
        teams = request.POST.get('teams', '')
        desc = request.POST.get('desc', '')
        created_tourney = TournamentObject(name=name, tournament_type=tournament_type, num_teams=teams,
                                           description=desc)
        created_tourney.save()
    return render(request, 'Tournament/new.html', {})
