from pymongo import MongoClient, GEO2D
import json
import hashlib
import sys

if len(sys.argv)<2:
	print ("usage python add_data_to_db.py <server of mongo>")
	exit()
client = MongoClient(sys.argv[1])
client.drop_database("street_parking")
# client = MongoClient()
db = client.street_parking


f = open("parking_data.json",'r')
id = 1
print ("Dumping Parking Data")
for line in f:
	if line=="":
		continue
	json_data = json.loads(line)
	json_data["_id"] = id
	# json_data["parking_spots_available"] = json_data['parking_spots']
	inserted_record = db.parking_data.insert_one(json_data)
	id+=1
print ("Creting Geospatial Index")
db.parking_data.create_index([("location", GEO2D)])
f.close()

f = open("user_profiles.json",'r')
print ("Adding user data")
for line in f:
	if line=="":
		continue
	json_data = json.loads(line)
	# print (json_data)
	json_data["_id"] = json_data['email']
	json_data["password"] = json_data['salt']+json_data['password']
	json_data["password"] = hashlib.sha256(json_data["password"].encode('ascii')).hexdigest()
	json_data.pop("email", None)
	# json_data["parking_spots_available"] = json_data['parking_spots']
	inserted_record = db.user.insert_one(json_data)
print ("Added User Data")

print ("Adding amazon credentials to db")
f = open("/Users/jaysolanki/.aws/credentials",'r')
d = f.read().split("\n")

db.aws_credentials.insert_one({"access_token":d[1].split("=")[1].strip(), "access_token_secret":d[2].split("=")[1].strip()})
