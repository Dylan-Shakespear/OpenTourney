from django.contrib import admin
from .models import TournamentObject, Match, Team, UserSettings

admin.site.register(TournamentObject)
admin.site.register(Match)
admin.site.register(Team)
admin.site.register(UserSettings)
