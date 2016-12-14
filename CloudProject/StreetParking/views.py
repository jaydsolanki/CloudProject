from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import boto3
from pymongo import MongoClient
from bson.son import SON
import json


# Create your views here.


def index(request):
    context = {"title": "Home"}
    return render(request, 'index.html', context)


@csrf_exempt
def collect_data(request):
    parking_data = list(ParkingData.objects.all().values_list('latitude', 'longitude', 'street_ave_name', 'parking_spots', 'between_street_ave', 'parking_on'))
    # for i in range(len(lat_long_list)):
    #     lat_long_list[i] = list(lat_long_list[i])
    context = {"title": "Collect Data", 'parking_data': parking_data}
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
    parking_on = request.POST['parking_on']
    print("PARKING ALLOWED: " + str(parking_allowed) + "; TYPE: " + str(type(parking_allowed)))
    pd = ParkingData(latitude=lat, longitude=lng, parking_allowed=parking_allowed, parking_spots=num_parking, between_street_ave=between, street_ave_name=street_ave_name, parking_on=parking_on)
    pd.save()
    return HttpResponse()


@csrf_exempt
def remove_parking_data(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    ParkingData.objects.filter(latitude=lat, longitude=lng).delete()
    return HttpResponse()


@csrf_exempt
def user_testing(request):
    if request.method == "GET":
        context = {'title': "User Testing"}
        return render(request, 'user_testing.html', context)
    else:
        client = MongoClient()
        db = client.street_parking
        lat = float(request.POST.get('lat'))
        lng = float(request.POST.get('lng'))
        query = {"location": SON([("$near", [lng, lat]), ("$maxDistance", 0.003)])}
        parking_locations = db.parking_data.find(query)
        response = []
        for parking_location in parking_locations:
            print(parking_location)
            response.append([parking_location['location']['lat'], parking_location['location']['lng'], parking_location['parking_spots_available']])
            # break
        return HttpResponse(status=200, content=json.dumps({"lat_longs":response}), content_type="application/json")


############################################# Mobile App Service Requests #######################################

@csrf_exempt
def registration(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        salt = create_salt()
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        content = {"information": "Succesfully created user"}
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def login(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        content = {"information": "Login Successful"}
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def search_parking(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        if not is_authenticated(user_id, password):
            return HttpResponse(status=400, content_type="text/plain", content="Incorrect login credentials")
        # Search here for geopoints
        user_lat = request.POST.get('latitude')
        user_lng = request.POST.get('longitude')
        # The above variables would be used in search query
        content = {"coordinates": [{"street_ave_name": "21st street", "lat": -72.343434, "lng": 40.454534, "parking_spots": 20}]}  # this will come form database
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def park_vehicle(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        if not is_authenticated(user_id, password):
            return HttpResponse(status=400, content_type="text/plain", content="Incorrect login credentials")
        # Search here for geopoints
        expected_time = request.POST.get('expected_time')
        # The above will be updated in database
        content = {"information": "parked_successfully"}
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def leave_parking_spot(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        if not is_authenticated(user_id, password):
            return HttpResponse(status=400, content_type="text/plain", content="Incorrect login credentials")
        # Search here for geopoints
        user_lat = request.POST.get('latitude')
        user_lng = request.POST.get('longitude')
        # The above will be updated in database
        content = {"information": "parked_successfully"}
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def logout(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        if not is_authenticated(user_id, password):
            return HttpResponse(status=400, content_type="text/plain", content="Incorrect login credentials")
        content = {"information": "logged out successfully"}
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def update_profile(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        if not is_authenticated(user_id, password):
            return HttpResponse(status=400, content_type="text/plain", content="Incorrect login credentials")

        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        password = request.POST.get('password', None)
        home_location = request.POST.get('home_location', None)
        work_location = request.POST.get('work_location', None)
        work_time = request.POST.get('work_time', None)
        profile_image = request.POST.get('profile_image', None)
        if first_name:
            pass  # Change first Name
        if last_name:
            pass  # change last name
        if password:
            pass  # change password
        if home_location:
            pass  # change home location
        if work_location:
            pass  # change work location
        if work_time:
            pass  # change work time
        if profile_image:
            pass  # change work time

        content = {"information": "logged out successfully"}
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


def is_authenticated(user_id, password):
    salt = get_salt()
    return True


def create_salt():
    return "salt"


def get_salt(user_id):
    return "salt"
