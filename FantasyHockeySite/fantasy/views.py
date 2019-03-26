from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    # return HttpResponse("Hello, world. You're at the views index.")
    return render(request, 'fantasy/index.html')


def nhl_players(request):
    return HttpResponse("Hello, world. You're at the nhl players.")
