from django.shortcuts import render


def home(request):
    return render(request, 'Tournament/home.html', {})


def tourney(request):
    return render(request, 'Tournament/tourney.html', {})