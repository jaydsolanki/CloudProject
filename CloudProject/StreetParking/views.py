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
    num_parking = request.POST['num_parking']
    between = request.POST['between']
    street_ave_name = request.POST['street_ave_name']
    parking_allowed = request.POST['parking_allowed']
    parking_allowed = True if parking_allowed == "true" else False
    print("PARKING ALLOWED: "+str(parking_allowed)+"; TYPE: "+str(type(parking_allowed)))
    pd = ParkingData(latitude=lat, longitude=lng, parking_allowed=parking_allowed, parking_spots=num_parking, between_street_ave= between, street_ave_name=street_ave_name)
    pd.save()
    return HttpResponse()


@csrf_exempt
def remove_parking_data(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    ParkingData.objects.filter(latitude=lat, longitude=lng).delete()
    return HttpResponse()
