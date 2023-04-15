import sys

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import TournamentObject, Match, Team
from .utils import Rounds, calculate_next_round, clear_following_round


def home(request):
    return render(request, 'Tournament/home.html', {})


# This is a placeholder for testing. Should later be removed
def tourney(request):
    return render(request, 'Tournament/tourney.html', {})


# This is the actual tournament view
def tourney_main(request, tourney_id):

    if request.method == 'POST':
        # Updates Match
        # TODO: Validate User
        tourney_id = int(request.POST.get('tourney_id', ''))
        tourney_obj = TournamentObject.objects.get(pk=tourney_id)

        # Team 1 - Create/Edit - Name
        team1 = request.POST.get('edit-names-1', '')
        team1_id = int(request.POST.get('team1_id', ''))
        if team1_id != -1:
            team1_obj = Team.objects.get(pk=team1_id)
            team1_obj.name = team1
        else:
            team1_obj = Team(name=team1, tournament=tourney_obj)
        team1_obj.save()

        # Team 2 - Create/Edit - Name
        team2 = request.POST.get('edit-names-2', '')
        team2_id = int(request.POST.get('team2_id', ''))
        if team2_id != -1:
            team2_obj = Team.objects.get(pk=team2_id)
            team2_obj.name = team2
        else:
            team2_obj = Team(name=team2, tournament=tourney_obj)
        team2_obj.save()

        # Match - Create/Edit
        match_id = int(request.POST.get('match_id', ''))
        try:
            match_obj = Match.objects.get(tournament=tourney_obj, round=match_id)
        except Match.DoesNotExist:
            match_obj = Match(tournament=tourney_obj, round=match_id)
        match_obj.team1 = team1_obj
        match_obj.team2 = team2_obj
        match_obj.save()

        # Update Next Round
        # If this is the last round, nothing is done
        if match_id < tourney_obj.num_teams - 1:
            winner = request.POST.get('winner', '')
            if winner != "none":
                # Calculates the match_id for the next round the winning team will be in
                next_round = calculate_next_round(match_id, tourney_obj.num_teams)
                try:
                    next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
                except Match.DoesNotExist:
                    next_match_obj = Match(tournament=tourney_obj, round=next_round)

                if match_id % 2 == 0:
                    # Evens are bottom for next round
                    if winner == "team2":
                        next_match_obj.team2 = team2_obj
                    else:
                        next_match_obj.team2 = team1_obj
                else:
                    # Odds are top for next round
                    if winner == "team2":
                        next_match_obj.team1 = team2_obj
                    else:
                        next_match_obj.team1 = team1_obj
                next_match_obj.save()
                # Clears following round(s) in case winner was changed and old winner got further in the tourney
                clear_following_round(next_round, tourney_obj)

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

        return tourney_main(request, created_tourney.id)
    return render(request, 'Tournament/new.html', {})


def tourney_listings(request):
    tourneys = TournamentObject.objects.filter(user=request.user)
    query = request.GET.get('search')
    if query != '' and query is not None:
        tourneys = TournamentObject.objects.filter(
            (Q(name__icontains=query) |
             Q(description__icontains=query)) & (
                    Q(user=request.user) |
                    Q(public=True)))

    return render(request, 'Tournament/listings.html', {'tourneys': tourneys})


def edit_match(request, match_not_unique_id, tourney_id):

    this_tourney = TournamentObject.objects.get(pk=tourney_id)
    team1_id = "-1"
    team2_id = "-1"

    # TODO: This copies from util.py. May be a better way to do this without duplicated code
    if match_not_unique_id < (this_tourney.num_teams / 2) + 1:
        team1 = "Team ???"
        team2 = "Team ???"
        # Figures out if user should be able to edit names
        # Names can only be edited from the first round, then they are auto-filled via winners
    else:
        team1 = "To Be Determined"
        team2 = "To Be Determined"

    try:
        this_match = Match.objects.get(tournament=this_tourney, round=match_not_unique_id)
        if this_match.team1 is not None:
            team1 = this_match.team1.name
            team1_id = this_match.team1.id
        if this_match.team2 is not None:
            team2 = this_match.team2.name
            team2_id = this_match.team2.id
    except Match.DoesNotExist:
        pass

    context = {
        'tourney_id': tourney_id,
        'match_id': match_not_unique_id,
        'team1': team1,
        'team2': team2,
        'team1_id': team1_id,
        'team2_id': team2_id,
    }
    return render(request, 'Tournament/editmatch.html', context)


def delete_tourney(request, tourney_id):
    tourney_obj = get_object_or_404(TournamentObject, pk=tourney_id)
    if tourney_obj.user == request.user:
        tourney_obj.delete()
        return tourney_listings(request)
