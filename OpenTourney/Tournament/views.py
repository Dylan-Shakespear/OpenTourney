import sys
from django.shortcuts import render
from .models import TournamentObject
from .utils import Rounds


def home(request):
    return render(request, 'Tournament/home.html', {})


# This is a placeholder for testing. Should later be removed
def tourney(request):
    return render(request, 'Tournament/tourney.html', {})


# This is the actual tournament view
def tourney_main(request, tourney_id):
    # Retrieves the Tournament selected
    this_tourney = TournamentObject.objects.get(pk=tourney_id)
    # Uses a util to generate the rounds to be displayed
    # Needs to be done here and not in the html file
    rounds = Rounds(this_tourney)

    context = {
        'tourney': this_tourney,
        'rounds': rounds,
    }

    return render(request, 'Tournament/tourney.html', context)


def new_tourney(request):
    if request.method == 'POST':
        # Creates a new tournament object with form
        name = request.POST.get('name', '')
        tournament_type = request.POST.get('type', '')
        teams = request.POST.get('teams', '')
        desc = request.POST.get('desc', '')
        public_choice = request.POST.get('public', '')

        # Gets choice from the radio buttons
        if public_choice == "public":
            public = True
        else:
            public = False

        created_tourney = TournamentObject(name=name, tournament_type=tournament_type, num_teams=teams,
                                           description=desc, public=public, user=request.user)
        created_tourney.save()
    return render(request, 'Tournament/new.html', {})


def tourney_listings(request):
    tourneys = (TournamentObject.objects.filter(user=request.user))
    return render(request, 'Tournament/listings.html', {'tourneys': tourneys})
