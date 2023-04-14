from .models import Match
from .models import Team


class Rounds:

    def __init__(self, tourney):
        self.rounds = []
        global_round_counter = 1
        round_count = tourney.num_teams
        while round_count > 1:
            round_count //= 2
            self.rounds.append(Round(tourney, round_count, global_round_counter))
            global_round_counter += round_count


class Round:

    def __init__(self, tourney, rounds, count):
        self.matches = []
        for i in range(1, rounds + 1):
            if count < (tourney.num_teams / 2) + 1:
                arg1 = "Team ???"
                arg2 = "Team ???"
            else:
                arg1 = "To Be Determined"
                arg2 = "To Be Determined"

            try:
                this_match = Match.objects.get(tournament=tourney, round=count)
                if this_match.team1 is not None:
                    arg1 = this_match.team1.name
                if this_match.team2 is not None:
                    arg2 = this_match.team2.name

            except Match.DoesNotExist:
                pass

            self.matches.append(TeamNames(arg1, arg2, count))
            count += 1


class TeamNames:

    team_1 = "Error"
    team_2 = "Error"
    match_util_round = -1

    def __init__(self, team_name_1, team_name_2, match_util_round):
        self.team_1 = team_name_1
        self.team_2 = team_name_2
        self.match_util_round = match_util_round


# Returns the next round
def calculate_next_round(round, total):
    if round >= total - 1:
        raise Exception("ERROR: Trying to find next round for final round")
    half_total = total / 2
    current_total = half_total
    while round > current_total:
        half_total /= 2
        current_total += half_total
        print("Round is " + str(round) + " half_total is " + str(half_total) + " current_total is " + str(current_total))
    round -= current_total - half_total
    print("Returning " + str(current_total + (round + 1) // 2))
    return current_total + (round + 1) // 2


# Clears following rounds in case winner was changed and old winner got further in the tourney
def clear_following_round(round, tourney_obj):
    if round < tourney_obj.num_teams - 1:
        next_round = calculate_next_round(round, tourney_obj.num_teams)
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
            if round % 2 == 0:
                # Evens are bottom for next round
                next_match_obj.team2 = None
            else:
                # Odds are top for next round
                next_match_obj.team1 = None
            # If we found a match here, there could be another future match they are in
            next_match_obj.save()
            clear_following_round(next_round, tourney_obj)
        except Match.DoesNotExist:
            pass
