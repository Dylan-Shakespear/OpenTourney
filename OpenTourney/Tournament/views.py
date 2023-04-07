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
    rounds = Rounds(this_tourney.num_teams)
    print(Rounds.rounds)
    context = {
        'tourney': this_tourney,
        'rounds': rounds,
    }
    return render(request, 'Tournament/tourney.html', context)