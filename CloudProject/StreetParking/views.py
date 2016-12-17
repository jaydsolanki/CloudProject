from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import boto3
from pymongo import MongoClient
from .mongo import MongoQuery
from bson.son import SON
import json
import datetime


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


# @csrf_exempt
# def add_parking_data(request):
#     lat = request.POST['lat']
#     lng = request.POST['lng']
#     num_parking = request.POST['num_parking']
#     between = request.POST['between']
#     street_ave_name = request.POST['street_ave_name']
#     parking_allowed = request.POST['parking_allowed']
#     parking_allowed = True if parking_allowed == "true" else False
#     parking_on = request.POST['parking_on']
#     print("PARKING ALLOWED: " + str(parking_allowed) + "; TYPE: " + str(type(parking_allowed)))
#     pd = ParkingData(latitude=lat, longitude=lng, parking_allowed=parking_allowed, parking_spots=num_parking, between_street_ave=between, street_ave_name=street_ave_name, parking_on=parking_on)
#     pd.save()
#     return HttpResponse()
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
    client = MongoClient()
    db = client.street_parking
    db.parking_data.insert_one({"location": {"lng": float(lng), "lat": float(lat)}, "parking_spots_available": num_parking})
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
        return HttpResponse(status=200, content=json.dumps({"lat_longs": response}), content_type="application/json")


############################################# Mobile App Service Requests #######################################
mongo_query = MongoQuery('localhost')


@csrf_exempt
def check_username(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id', '')
        result = mongo_query.check_username(user_id)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def registration(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        print ("REQUEST: "+str(json_input))
        password = json_input.get('password', '')
        re_password = json_input.get('re_password', '')
        full_name = json_input.get('full_name', '')
        email = json_input.get('email', '')
        result = mongo_query.register(full_name, email, password, re_password)
        print ("RESPONSE: "+str(result)+"\n")
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def login(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        print ("REQUEST: "+str(json_input))
        user_id = json_input.get('email')
        password = json_input.get('password')
        result = mongo_query.login(user_id, password)
        print ("RESPONSE: "+str(result)+"\n")
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def logout(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        print ("REQUEST: "+str(json_input))
        token = json_input.get('token')
        result = mongo_query.logout(token)
        print ("RESPONSE: "+str(result)+"\n")
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def get_parking_locations(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        print ("REQUEST: "+str(json_input))
        token = json_input.get('token')
        lat = json_input.get('lat')
        lng = json_input.get('lng')
        result = mongo_query.get_parking_locations(token, lat, lng)
        print ("RESPONSE: "+str(result)+"\n")
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def upload_profile_pic(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        image = json_input.get('image')
        result = mongo_query.upload_profile_pic(token, image)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def add_home_coordinates(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        lat = json_input.get('lat')
        lng = json_input.get('lng')
        result = mongo_query.add_home_coordinates(token, lat, lng)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def add_office_coordinates(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        lat = json_input.get('lat')
        lng = json_input.get('lng')
        result = mongo_query.add_office_coordinates(token, lat, lng)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def add_office_timing(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        time = json_input.get('time').split(":")
        time_obj = datetime.time(int(time[0]), int(time[1]), int(time[2]))
        result = mongo_query.add_office_timing(token, time_obj)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def park_vehicle(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        lat = json_input.get('lat')
        lng = json_input.get('lng')
        expected_leave_time = json_input.get('expected_leave_time')
        time_obj = datetime.datetime.now() + datetime.timedelta(minutes=int(expected_leave_time))
        result = mongo_query.park_vehicle(token, lat, lng, time_obj)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def unpark_vehicle_by_user(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        result = mongo_query.unpark_vehicle_by_user(token)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def user_help_request(request):
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        result = mongo_query.user_help_request(token)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")
