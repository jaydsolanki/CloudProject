from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    context = {"title": "Home"}
    return render(request, 'index.html', context)


def collect_data(request):
    context = {"title": "Collect Data"}
    return render(request, 'collect_data.html', context)
