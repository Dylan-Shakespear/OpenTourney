from django.db import models
from django.contrib.auth.models import User


class TournamentObject(models.Model):
    SINGLE_ELIMINATION = 'SE'
    DOUBLE_ELIMINATION = 'DE'
    TOURNAMENT_TYPES = [
        (SINGLE_ELIMINATION, 'Single Elimination'),
        (DOUBLE_ELIMINATION, 'Double Elimination'),
    ]

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    num_teams = models.IntegerField()
    tournament_type = models.CharField(max_length=2, choices=TOURNAMENT_TYPES, default=SINGLE_ELIMINATION)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='team')
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE, related_name='teams')
    position = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        # The position (aka seed) must be unique for a Team within a given Tournament
        # Ex. There can't be 2 #1 seeds
        unique_together = (('tournament', 'position'),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Match(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    team1 = models.ForeignKey(Team, related_name='matches_as_team1', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='matches_as_team2', on_delete=models.CASCADE)
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE, related_name='matches')
    round = models.IntegerField()

    class Meta:
        unique_together = (('tournament', 'round'),)

    def __str__(self):
        return self.name

