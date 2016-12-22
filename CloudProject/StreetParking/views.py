from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *

from pymongo import MongoClient
from .mongo import MongoQuery
from bson.son import SON
import json
import datetime
from CloudProject.settings import MONGO_URL
#
# Create your views here.

print (MONGO_URL)

def index(request):
    context = {"title": "Home"}
    return render(request, 'index.html', context)


@csrf_exempt
def collect_data(request):
    mongo_query = MongoQuery(MONGO_URL)
    parking_data = mongo_query.get_all_parking_locations_web_app()
    context = {"title": "Collect Data", 'parking_data': parking_data}   
    return render(request, 'collect_data.html', context)


@csrf_exempt
def add_parking_data(request):
    mongo_query = MongoQuery(MONGO_URL)
    lat = request.POST['lat']
    lng = request.POST['lng']
    num_parking = request.POST['num_parking']
    between = request.POST['between']
    street_ave_name = request.POST['street_ave_name']
    parking_allowed = request.POST['parking_allowed']
    parking_allowed = True if parking_allowed == "true" else False
    parking_on = request.POST['parking_on']
    mongo_query.add_parking_data(lat,lng,num_parking,street_ave_name,between,parking_allowed,parking_on)
    return HttpResponse()


@csrf_exempt
def remove_parking_data(request):
    mongo_query = MongoQuery(MONGO_URL)
    lat = request.POST['lat']
    lng = request.POST['lng']
    mongo_query.delete_parking_spot(lat,lng)
    return HttpResponse()


@csrf_exempt
def user_testing(request):
    mongo_query = MongoQuery(MONGO_URL)
    if request.method == "GET":
        context = {'title': "User Testing"}
        return render(request, 'user_testing.html', context)
    else:
        lat = float(request.POST.get('lat'))
        lng = float(request.POST.get('lng'))
        parking_locations = mongo_query.get_parking_locations_web_app(lat, lng)
        return HttpResponse(status=200, content=json.dumps({"lat_longs": parking_locations}), content_type="application/json")


############################################# Mobile App Service Requests #######################################


@csrf_exempt
def check_username(request):
    mongo_query = MongoQuery(MONGO_URL)
    if request.method == "POST":
        user_id = request.POST.get('user_id', '')
        result = mongo_query.check_username(user_id)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def registration(request):
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
def get_parking_locations_kafka(request):
    mongo_query = MongoQuery(MONGO_URL)
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        print ("REQUEST: "+str(json_input))
        token = json_input.get('token')
        lat = json_input.get('lat')
        lng = json_input.get('lng')
        gcm_token = json_input.get('gcm_token', None)
        result = mongo_query.add_to_kafka(token, lat, lng, gcm_token)
        print ("RESPONSE: "+str(result)+"\n")
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def upload_profile_pic(request):
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
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
    mongo_query = MongoQuery(MONGO_URL)
    if request.method == "POST":
        json_input = json.loads(request.body.decode('utf-8'))
        token = json_input.get('token')
        result = mongo_query.user_help_request(token)
        content = json.dumps(result)
        return HttpResponse(status=200, content_type="application/json", content=content)
    else:
        return HttpResponse(status=400, content_type="text/plain", content="Only POST request allowed")


@csrf_exempt
def sns_request(request):
    mongo_query = MongoQuery(MONGO_URL)
    parameters = json.loads(request.GET.get("sns_parameter"))
    gcm_token = parameters['gcm_token']
    lat = float(parameters['lat'])
    lng = float(parameters['lng'])
    token = parameters['token']
    mongo_query.publish_sns_results(token, gcm_token, lat, lng)
    return HttpResponse()



