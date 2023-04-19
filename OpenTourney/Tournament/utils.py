import math
from django.core.exceptions import ObjectDoesNotExist
from .models import Match


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
                # Round 1, these teams need to be named
                arg1 = "Team " + str((count - 1) * 2 + 1)
                arg2 = "Team " + str(count * 2)
            else:
                # After round 1, these teams will be determined by winners of old rounds
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


class LosersRounds:

    def __init__(self, tourney):
        self.rounds = []
        global_round_counter = tourney.num_teams
        round_count = tourney.num_teams // 2
        # In the loser's bracket, the number of games only decreases every other round.
        # For example, if there are 16 total teams the games per round in the loser's bracket would follow the order:
        # 8, 8, 4, 4, 2, 2
        second_round = True
        while round_count > 0:
            if second_round:
                round_count //= 2
                second_round = False
            else:
                second_round = True
            self.rounds.append(Round(tourney, round_count, global_round_counter))
            global_round_counter += round_count
        self.grand_final = GrandFinal(tourney, global_round_counter)


class LoserRound:

    def __init__(self, tourney, rounds, count):
        self.matches = []
        for i in range(1, rounds + 1):
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


class GrandFinal:

    def __init__(self, tourney, count):
        self.team_1 = "To Be Determined"
        self.team_2 = "To Be Determined"
        self.match_util_round = count

        try:
            this_match = Match.objects.get(tournament=tourney, round=count)
            if this_match.team1 is not None:
                self.team_1 = this_match.team1.name
            if this_match.team2 is not None:
                self.team_2 = this_match.team2.name
        except Match.DoesNotExist:
            pass


class TeamNames:

    team_1 = "Error"
    team_2 = "Error"
    match_util_round = -1

    def __init__(self, team_name_1, team_name_2, match_util_round):
        self.team_1 = team_name_1
        self.team_2 = team_name_2
        self.match_util_round = match_util_round


# Updates the next round where the winner appears
def single_tourney_update_future_rounds(match_id, tourney_obj, winner, team1_obj, team2_obj):
    # If this is the last round, nothing is done
    if match_id < tourney_obj.num_teams - 1 and winner != "none":

        next_round = calculate_next_round(match_id, tourney_obj.num_teams)
        next_match_obj = get_or_create_match(tourney_obj, next_round)

        if match_id % 2 == 0:
            next_match_obj.team2 = team2_obj if winner == "team2" else team1_obj
        else:
            next_match_obj.team1 = team2_obj if winner == "team2" else team1_obj
        next_match_obj.save()
        clear_following_round(next_round, tourney_obj)


# Updates the next round where the winner and loser appear
def double_tourney_update_future_rounds(match_id, tourney_obj, winner, team1_obj, team2_obj):
    # If this is the last round, nothing is done
    if match_id < get_double_elim_max(tourney_obj.num_teams) and winner != "none":
        # Calculates the match_id for the next round the winning team will be in
        next_round = calculate_double_next_round(match_id, tourney_obj.num_teams)
        next_match_obj = get_or_create_match(tourney_obj, next_round)
        if is_condense_round(match_id, tourney_obj.num_teams):
            # Normal round in winner's bracket
            # Or condensing round in loser's bracket
            if (match_id > tourney_obj.num_teams and match_id % 2 == 1) or (
                    match_id <= tourney_obj.num_teams and match_id % 2 == 0):
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
        else:
            # The winner of this match won in the loser's bracket
            # Next round will play a recent loser in the winner's bracket
            # Will always be bottom
            if winner == "team2":
                next_match_obj.team2 = team2_obj
            else:
                next_match_obj.team2 = team1_obj
        next_match_obj.save()

        # Going to Loser Bracket?
        loser_next_round = calculate_loser_next_round(match_id, tourney_obj.num_teams)

        if loser_next_round != -1:
            loser_match_obj = get_or_create_match(tourney_obj, loser_next_round)

            # Winners Bracket -> Losers Bracket is always top except in round 1
            if match_id <= tourney_obj.num_teams / 2:
                # Round 1
                if match_id % 2 == 0:
                    # Evens are bottom for Winners Bracket -> Losers Bracket in round 1
                    if winner == "team2":
                        loser_match_obj.team2 = team1_obj
                    else:
                        loser_match_obj.team2 = team2_obj
                else:
                    # Odds are top for Winners Bracket -> Losers Bracket in round 1
                    if winner == "team2":
                        loser_match_obj.team1 = team1_obj
                    else:
                        loser_match_obj.team1 = team2_obj
            else:
                # Other Rounds that aren't round 1
                if winner == "team2":
                    loser_match_obj.team1 = team1_obj
                else:
                    loser_match_obj.team1 = team2_obj
            loser_match_obj.save()
            clear_following_round_winning(next_round, tourney_obj)
            clear_following_round_losing(next_round, tourney_obj)


# Gets or creates a match object for the given tournament and round
def get_or_create_match(tournament, round):
    try:
        return Match.objects.get(tournament=tournament, round=round)
    except Match.DoesNotExist:
        return Match(tournament=tournament, round=round)


# Returns the next round for single elimination
def calculate_next_round(match_number, total):
    if match_number >= total - 1:
        raise Exception("ERROR: Trying to find next round for final round")
    half_total = total / 2
    current_total = half_total
    while match_number > current_total:
        half_total /= 2
        current_total += half_total
    match_number -= current_total - half_total
    return current_total + (match_number + 1) // 2


# Returns the next round for a loser in double elimination
# Returns -1 if that was their final round
def calculate_double_next_round(match_number, total):
    if match_number < total - 1:
        # Winner's Bracket
        return calculate_next_round(match_number, total)
    if match_number == total - 1:
        # Winner of Winner's
        return get_double_elim_max(total)
    if match_number >= get_double_elim_max(total):
        raise Exception("ERROR: Trying to find next round for final round")

    # Loser's Bracket
    half_total = total / 4
    current_total = half_total + total
    past_total = total

    # Does this because number of matches in a round repeats in loser's bracket
    odd_round = True

    while match_number > current_total:
        if odd_round:
            odd_round = False
        else:
            half_total /= 2
            odd_round = True
        past_total = current_total
        current_total += half_total

    if odd_round:
        # If the next round has the same number of rounds, we can just add the match number to the number of matches in
        # a round
        return match_number + half_total
    else:
        # If the next round has half the number of rounds, we have to add the position of this match in the round // 2
        # to the match number of the first match in the next round
        return current_total + ((match_number - past_total) // 2)


# Returns the next round for a loser in double elimination
# Returns -1 if that was their final round
def calculate_loser_next_round(match_number, total):
    if match_number >= get_double_elim_max(total):
        raise Exception("ERROR: Trying to find loser's round for final round")
    if match_number >= total:
        # Loser's Bracket
        return -1
    if match_number == total - 1:
        # Special Case
        return get_double_elim_max(total) - 1

    # Winner's Bracket
    # First Round
    half_total = total / 2
    if match_number - 1 < half_total:
        return (match_number - 1) // 2 + total

    # Later Rounds
    current_total = half_total
    half_total /= 2
    current_total += half_total
    offset = -1
    while match_number > current_total:
        half_total /= 2
        current_total += half_total
        offset += half_total

    return match_number - total / 4 + offset + total


# Clears following rounds in case winner was changed and old winner got further in the tourney
def clear_following_round(match_id, tourney_obj):
    if match_id < tourney_obj.num_teams - 1:
        next_round = calculate_next_round(match_id, tourney_obj.num_teams)
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
        except ObjectDoesNotExist:
            # No next match object found, so we can't update it
            return
        if match_id % 2 == 0:
            # Evens are bottom for next round
            next_match_obj.team2 = None
        else:
            # Odds are top for next round
            next_match_obj.team1 = None
        # If we found a match here, there could be another future match they are in
        next_match_obj.save()
        clear_following_round(next_round, tourney_obj)


def clear_following_round_winning(match_id, tourney_obj):
    """
        Updates the next match object for a given round in the tournament.
        If the winner of the current round was changed and the old winner
        got further in the tourney, clears the team(s) in the next match object.
    """
    if match_id < get_double_elim_max(tourney_obj.num_teams):
        next_round = calculate_double_next_round(match_id, tourney_obj.num_teams)
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
        except ObjectDoesNotExist:
            # No next match object found, so we can't update it
            return
        if match_id == tourney_obj.num_teams - 1:
            next_match_obj.team1 = None
        elif match_id == get_double_elim_max(tourney_obj.num_teams) - 1:
            next_match_obj.team2 = None
        elif is_condense_round(next_round, tourney_obj.num_teams):
            # Normal round in winner's bracket or condensing round in loser's bracket
            if (match_id > tourney_obj.num_teams and match_id % 2 == 1) or (
                    match_id <= tourney_obj.num_teams and match_id % 2 == 0):
                # Evens are bottom for next round
                next_match_obj.team2 = None
            else:
                # Odds are top for next round
                next_match_obj.team1 = None
        else:
            # The winner of this match won in the loser's bracket
            # Next round will play a recent loser in the winner's bracket
            # Will always be bottom
            next_match_obj.team2 = None
        next_match_obj.save()
        # If we found a match here, there could be another future match they are in
        clear_following_round_winning(next_round, tourney_obj)
        clear_following_round_losing(next_round, tourney_obj)


# Clears following rounds in case loser was changed and old loser got further in the tourney
def clear_following_round_losing(match_id, tourney_obj):
    if match_id < get_double_elim_max(tourney_obj.num_teams):
        next_round = calculate_loser_next_round(match_id, tourney_obj.num_teams)
        try:
            loser_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
        except ObjectDoesNotExist:
            # No next match object found, so we can't update it
            return
        # Winners Bracket -> Losers Bracket is always top except in round 1
        if match_id <= tourney_obj.num_teams / 2:
            # Round 1
            if match_id % 2 == 0:
                loser_match_obj.team2 = None
            else:
                # Odds are top for next round
                loser_match_obj.team1 = None
        else:
            # Other Rounds
            loser_match_obj.team1 = None
        loser_match_obj.save()
        # Has to Clear the winning from here to use proper last round match id
        try:
            next_match_obj = Match.objects.get(tournament=tourney_obj, round=next_round)
            if match_id == tourney_obj.num_teams - 1:
                next_match_obj.team1 = None
            elif match_id == get_double_elim_max(tourney_obj.num_teams) - 1:
                next_match_obj.team2 = None
            elif not is_condense_round(next_round, tourney_obj.num_teams):
                # Normal round in winner's bracket
                # Or condensing round in loser's bracket
                if (match_id > tourney_obj.num_teams and match_id % 2 == 1) or (
                        match_id <= tourney_obj.num_teams and match_id % 2 == 0):
                    # Evens are bottom for next round
                    next_match_obj.team2 = None
                else:
                    # Odds are top for next round
                    next_match_obj.team1 = None
            else:
                # The winner of this match won in the loser's bracket
                # Next round will play a recent loser in the winner's bracket
                # Will always be bottom
                next_match_obj.team2 = None
            next_match_obj.save()
        except ObjectDoesNotExist:
            pass
        # If we found a match here, there could be another future match they are in
        clear_following_round_losing(next_round, tourney_obj)
        clear_following_round_winning(next_round, tourney_obj)


def get_double_elim_max(size):
    n = math.log2(size)
    return double_elim_max_sequence(n) + 1


def double_elim_max_sequence(n):
    if n == 1:
        return 2
    elif n == 2:
        return 5
    else:
        return 2*double_elim_max_sequence(n-1) + 3


def is_condense_round(match_number, total):
    if match_number <= total:
        # Winner's Bracket
        return True
    if match_number >= get_double_elim_max(total):
        raise Exception("ERROR: Invalid match number. The input was too high.")
    # Loser's Bracket
    quarter_total = total / 4
    current_total = quarter_total + total
    even_round = False
    while match_number >= current_total:
        if not even_round:
            even_round = True
        else:
            quarter_total /= 2
            even_round = False
        current_total += quarter_total

    return even_round
