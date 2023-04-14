"""OpenTourney URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Tournament import views as tournament_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tournament_views.home, name="index"),
    path('tourney/', tournament_views.tourney),
    path('tourney/<int:tourney_id>', tournament_views.tourney_main, name="tourney"),
    path('tourney/new', tournament_views.new_tourney, name="new"),
    path('tourney/tournaments', tournament_views.tourney_listings, name="listings"),
    path('tourney/edit_match/<int:match_not_unique_id>/<int:tourney_id>', tournament_views.edit_match, name="editmatch"),
]
