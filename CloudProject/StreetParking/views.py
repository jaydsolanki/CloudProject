from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *


# Create your views here.


def index(request):
    context = {"title": "Home"}
    return render(request, 'index.html', context)


@csrf_exempt
def collect_data(request):
    lat_long_list = list(ParkingData.objects.all().values_list('latitude', 'longitude'))
    for i in range(len(lat_long_list)):
        lat_long_list[i] = list(lat_long_list[i])
    context = {"title": "Collect Data", 'lat_long_list': lat_long_list}
    return render(request, 'collect_data.html', context)


@csrf_exempt
def add_parking_data(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    pd = ParkingData(latitude=lat, longitude=lng)
    pd.save()
    return HttpResponse()


@csrf_exempt
def remove_parking_data(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    ParkingData.objects.filter(latitude=lat, longitude=lng).delete()
    return HttpResponse()
