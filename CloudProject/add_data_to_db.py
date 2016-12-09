from pymongo import MongoClient, GEO2D
import json
client = MongoClient()
client.drop_database("street_parking")
# client = MongoClient()
db = client.street_parking


f = open("parking_data.json",'r')
id = 1
for line in f:
	json_data = json.loads(line)
	json_data["_id"] = id
	json_data["parkings_available"] = json_data['parking_spots']
	inserted_record = db.parking_data.insert_one(json_data)
	id+=1
	print(inserted_record.inserted_id)
db.parking_data.create_index([("location", GEO2D)])
f.close()
