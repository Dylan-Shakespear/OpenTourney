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
                arg1 = this_match.team1.name
                arg2 = this_match.team2.name
            except Match.DoesNotExist:
                pass

            self.matches.append(TeamNames(arg1, arg2))
            count += 1


class TeamNames:

    team_1 = "Error"
    team_2 = "Error"

    def __init__(self, team_name_1, team_name_2):
        self.team_1 = team_name_1
        self.team_2 = team_name_2
