import sys

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import TournamentObject, Match, Team
from .utils import Rounds, calculate_next_round, clear_following_round
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def home(request):
    return render(request, 'Tournament/home.html', {})


# This is a placeholder for testing. Should later be removed
def tourney(request):
    return render(request, 'Tournament/tourney.html', {})


# This is the actual tournament view
def tourney_main(request, tourney_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        # Updates Match
        tourney_id = int(request.POST.get('tourney_id', ''))
        tourney_obj = TournamentObject.objects.get(pk=tourney_id)

        # User Validation
        if tourney_obj.user != request.user:
            raise PermissionDenied("You are not authorized to edit this tournament.")

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
        try:
            print(request.POST.get('match_date', ''))
            match_obj.date = request.POST.get('match_date', '')
            print("Got Date")
        except:
            pass
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

    # User Validation
    if this_tourney.user != request.user and this_tourney.public is False:
        raise PermissionDenied("You are not authorized to view this tournament.")

    # Uses a util to generate the rounds to be displayed
    # Needs to be done here and not in the html file
    rounds = Rounds(this_tourney)

    context = {
        'tourney': this_tourney,
        'rounds': rounds,
    }

    return render(request, 'Tournament/tourney.html', context)


def new_tourney(request):
    if not request.user.is_authenticated:
        return redirect('login')
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
        url = reverse('tourney', kwargs={'tourney_id': created_tourney.id})
        return redirect(url)
    return render(request, 'Tournament/new.html', {})


def tourney_listings(request):

    query = request.GET.get('search')
    if query is None:
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            tourneys = TournamentObject.objects.filter(user=request.user)
            if not tourneys.exists():
                return redirect('new')
    else:
        if request.user.is_authenticated:
            tourneys = TournamentObject.objects.filter(
                (Q(name__icontains=query) |
                 Q(description__icontains=query)) & (
                        Q(user=request.user) |
                        Q(public=True)))
        else:
            tourneys = TournamentObject.objects.filter(
                (Q(name__icontains=query) |
                 Q(description__icontains=query)) & (Q(public=True)))
    paginator = Paginator(tourneys, 12)
    page = request.GET.get('page')
    tourneys = paginator.get_page(page)
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

    date = 0

    try:
        this_match = Match.objects.get(tournament=this_tourney, round=match_not_unique_id)
        if this_match.team1 is not None:
            team1 = this_match.team1.name
            team1_id = this_match.team1.id
        if this_match.team2 is not None:
            team2 = this_match.team2.name
            team2_id = this_match.team2.id
        date = this_match.date
    except Match.DoesNotExist:
        pass

    context = {
        'tourney_id': tourney_id,
        'match_id': match_not_unique_id,
        'team1': team1,
        'team2': team2,
        'team1_id': team1_id,
        'team2_id': team2_id,
        'date': date,
    }
    return render(request, 'Tournament/editmatch.html', context)


def delete_tourney(request, tourney_id):
    tourney_obj = get_object_or_404(TournamentObject, pk=tourney_id)
    if tourney_obj.user == request.user:
        tourney_obj.delete()
        return tourney_listings(request)
    else:
        raise PermissionDenied("You are not authorized to delete this tournament.")


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'Tournament/profile.html', {})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# This is the actual tournament view
def edit_tourney(request, tourney_id):
    if not request.user.is_authenticated:
        return redirect('login')
    tourney_obj = TournamentObject.objects.get(pk=tourney_id)
    if request.method == 'POST':
        tourney_obj.name = request.POST.get('tourney_name', '')
        tourney_obj.description = request.POST.get('desc', '')
        public_choice = request.POST.get('public', '')
        if public_choice == "public":
            tourney_obj.public = True
        else:
            tourney_obj.public = False
        tourney_obj.save()
        url = reverse('tourney', kwargs={'tourney_id': tourney_id})
        return redirect(url)
    else:
        if tourney_obj.user == request.user:
            return render(request, 'Tournament/edittourney.html', {'tourney': tourney_obj})
        else:
            raise PermissionDenied("You are not authorized to edit this tournament.")
