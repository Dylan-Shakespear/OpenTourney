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
        if self.name is None:
            return "Empty"
        return self.name

    name = models.CharField(max_length=100, default="My Tournament")
    description = models.TextField(blank=True)
    num_teams = models.IntegerField(default=16)
    tournament_type = models.CharField(max_length=2, choices=TOURNAMENT_TYPES, default=SINGLE_ELIMINATION)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tourney')
    public = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    winner = models.CharField(max_length=100, default="none")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='team')
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        if self.name is None:
            return "Empty"
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Match(models.Model):
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    date = models.DateTimeField(null=True)
    team1 = models.ForeignKey(Team, related_name='matches_as_team1', on_delete=models.CASCADE, null=True)
    team2 = models.ForeignKey(Team, related_name='matches_as_team2', on_delete=models.CASCADE, null=True)
    tournament = models.ForeignKey(TournamentObject, on_delete=models.CASCADE, related_name='matches')
    round = models.IntegerField()

    class Meta:
        unique_together = (('tournament', 'round'),)

    def __str__(self):
        if self.name is None:
            return "Empty"
        return self.name


class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settings')
    tourney_display = models.CharField(max_length=255, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
