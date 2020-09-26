from django.shortcuts import render
from django.http import HttpResponse



def index(request):
    if request.method == 'GET':
        return HTTpResponse("Go away.")
    elif request.method == 'POST':
        return HttpResponse(str(request.body))