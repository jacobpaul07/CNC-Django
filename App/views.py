from django.shortcuts import render
import pymongo
# Create your views here.


def index(request):
    return render(request, 'room.html')

