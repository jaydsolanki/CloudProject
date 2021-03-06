from pymongo import MongoClient
from bson.son import SON
from bson.objectid import ObjectId
import uuid
import hashlib
import datetime
from .aws import AWS


class MongoQuery:
    def __init__(self, connection_url):
        self.client = None
        self.connection_url = connection_url
        db, client = self.get_connection()
        self.aws_credentials = db.aws_credentials.find_one()
        client.close()

    def get_connection(self):
        client = MongoClient(self.connection_url)
        db = client.street_parking
        return db, client

    def get_aws_credentials(self):
        db, client = self.get_connection()
        obj = db.aws_credentials.find_one()
        result = [obj['access_token'], obj['access_token_secret']]
        client.close()
        return result

    def add_parking_data(self, lat, lng, parking_spots, street_ave_name, between_street_ave, parking_allowed, parking_on):
        db, client = self.get_connection()
        db.parking_data.insert_one({"location": {"lat": float(lat), "lng": float(lng)}, "parking_spots": int(parking_spots), "street_ave_name": street_ave_name, \
                                    "between_street_ave": between_street_ave, "parking_allowed": parking_allowed, "parking_on": parking_on, "parking_spots_available": int(parking_spots)})
        client.close()

    def check_username(self, username):
        db, client = self.get_connection()
        check_username = db.user.find({"_id": username})
        if check_username.count() > 0:
            client.close()
            return_obj = {"success": False, "error_list": ["The username already exists! Please select another username"]}
        else:
            client.close()
            return_obj = {"success": True}
        client.close()
        return return_obj

    def register(self, full_name, email, password, retype_password):
        error_list = []
        if email == "":
            error_list.append("Please enter a n email")
        if password == "":
            error_list.append("Please enter a password")
        if retype_password == "":
            error_list.append("Please retype your password")
        if password != retype_password:
            error_list.append("The passwords do not match")
        if len(error_list) > 0:
            return {"success": False, "error_list": error_list}
        db, client = self.get_connection()
        check_username = db.user.find({"_id": email})
        if check_username.count() > 0:
            client.close()
            return {"success": False, "error_list": ["The email is already registered! Please select another email"]}
        salt = uuid.uuid4().hex
        salt_password = salt + password
        hashed_password = hashlib.sha256(salt_password.encode('ascii')).hexdigest()
        document_to_insert = {"_id": email, "password": hashed_password, "salt": salt}
        if full_name and full_name != "":
            document_to_insert['full_name'] = full_name
        document_to_insert['member_since'] = datetime.datetime.now()
        db.user.insert_one(document_to_insert)
        token = uuid.uuid4().hex
        db.user_login_token.insert_one({"_id": email, "token": token, "active": True})
        client.close()
        return {"success": True, "token": token}

    def login(self, username, password):
        db, client = self.get_connection()
        user = db.user.find({"_id": username})
        if user.count() == 0:
            client.close()
            return {"success": False, "error_list": ["Invalid Credentials"]}
        user = user.next()
        salt = user['salt']
        full_name = user['full_name']
        salt_password = salt + password
        hashed_password = hashlib.sha256(salt_password.encode('ascii')).hexdigest()
        if hashed_password != user['password']:
            client.close()
            return {"success": False, "error_list": ["Invalid Credentials"]}
        db.user_login_token.delete_many({"_id": username})
        token = uuid.uuid4().hex
        db.user_login_token.insert_one({"_id": username, "token": token, "active": True})
        client.close()
        return {"success": True, "token": token, "full_name": full_name}

    def validate_token(self, token):
        db, client = self.get_connection()
        user_login_token = db.user_login_token.find({"token": token, "active": True})
        if user_login_token.count() == 0:
            client.close()
            return {"success": False, "error_list": ["Invalid Request"]}
        user_login_token = user_login_token.next()
        client.close()
        return {"success": True, 'user_login_token': user_login_token}

    def logout(self, token):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        aws = AWS(self.aws_credentials['access_token'], self.aws_credentials['access_token_secret'])
        end_point_arn = list(db.sns_info.find({"_id":token}))
        if end_point_arn and len(end_point_arn)>0:
            aws.delete_sns_endpoint(end_point_arn[0]['end_point_arn'])
        db.user_login_token.delete_many({"token": token})
        client.close()
        return {"success": True}

    def delete_parking_spot(self, lat, lng):
        db, client = self.get_connection()
        db.parking_data.remove({"location": {"lat": float(lat), "lng": float(lng)}})
        client.close()

    def get_parking_locations_web_app(self, lat, lng):
        db, client = self.get_connection()
        # query = {"location": SON([("$near", [float(lng), float(lat)]), ("$maxDistance", 0.003)])}
        query = {"location": SON([("$near", [float(lat), float(lng)]), ("$maxDistance", 0.003)])}
        parking_locations = db.parking_data.find(query)
        parking_spots = []
        for parking_location in parking_locations:
            parking_spots.append([parking_location['location']['lat'], parking_location['location']['lng'], parking_location['parking_spots_available']])
        client.close()
        return parking_spots

    def get_all_parking_locations_web_app(self):
        db, client = self.get_connection()
        parking_locations = list(db.parking_data.find({}))
        client.close()
        return parking_locations

    def get_parking_locations(self, token, lat, lng):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        # query = {"location": SON([("$near", [float(lng), float(lat)]), ("$maxDistance", 0.003)])}
        query = {"location": SON([("$near", [float(lat), float(lng)]), ("$maxDistance", 0.003)])}
        parking_locations = db.parking_data.find(query)
        parking_spots = []
        for parking_location in parking_locations:
            parking_spots.append([parking_location['location']['lat'], parking_location['location']['lng'], parking_location['parking_spots_available']])
        try:
            other_users_query = {"location": SON([("$near", [float(lng), float(lat)]), ("$maxDistance", 0.003)]), "date_time_of_query": {"$gte": datetime.datetime.now() - datetime.timedelta(minutes=15)}}
            others_looking = db.parking_queries.find(other_users_query).count()
        except Exception as e:
            print("ERROR: "+str(e))
            others_looking = -1
        db.parking_queries.insert_one({"user_id": user_id, "coordinates": {"lat": float(lat), "lng": float(lng)}, "date_time_of_query": datetime.datetime.now()})
        client.close()
        return {"success": True, "parking_spots": parking_spots, "other_looking": others_looking}
        # return {"success": True, "parking_spots": parking_spots}

    def upload_profile_pic(self, token, base64_image):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        user = db.user.find({"_id": user_id})
        user = user.next()
        client.close()
        return {"success": True}

    def add_home_coordinates(self, token, lat, lng):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        db.user.find_and_modify({"_id": user_id}, {"$set": {"home_coordinates": {"lat": lat, "lng": lng}}})
        client.close()
        return {"success": True}

    def add_office_coordinates(self, token, lat, lng):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        db.user.find_and_modify({"_id": user_id}, {"$set": {"office_coordinates": {"lat": lat, "lng": lng}}})
        client.close()
        return {"success": True}

    def add_office_timing(self, token, time_obj):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        db.user.find_and_modify({"_id": user_id}, {"$set": {"office_time": time_obj}})
        client.close()
        return {"success": True}

    def park_vehicle(self, token, lat, lng, expected_leave_time):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        query = {"location": SON([("$near", [float(lat), float(lng)]), ("$maxDistance", 0.003)])}
        # query = {"location": SON([("$near", [float(lng), float(lat)]), ("$maxDistance", 0.003)])}
        parking_spot = db.parking_data.find_and_modify(query, {"$inc": {"parking_spots_available": -1}})
        if parking_spot['parking_spots_available'] <= 0:
            db.parking_data.find_and_modify(query, {"$set": {"parking_spots_available": 0}})
        db.parking.insert_one({"user_id": user_id, "parking_spot_id": parking_spot["_id"], "parking_date_time": datetime.datetime.now(), "parked": True, "parking_leave_time": expected_leave_time})
        client.close()
        return {"success": True}

    def unpark_vehicle_by_id(self, token, parking_id):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        parking_obj = db.parking.find_and_modify({"_id": parking_id}, {"$set": {"parked": False, "leave_time": datetime.datetime.now()}})
        db.parking_data.find_and_modify({"_id": parking_obj['parking_spot_id']}, {"$inc": {"parking_spots_available": 1}})
        client.close()
        return {"success": True}

    def unpark_vehicle_by_user(self, token):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        user_id = validated['user_login_token']['_id']
        parking_obj = db.parking.find_and_modify({"user_id": user_id, "parked": True}, {"$set": {"parked": False, "leave_time": datetime.datetime.now()}})
        db.parking_data.find_and_modify({"_id": parking_obj['parking_spot_id']}, {"$inc": {"parking_spots_available": 1}})
        client.close()
        return {"success": True}

    def user_help_request(self, token):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        db, client = self.get_connection()
        client.close()
        return {"success": True}

    def add_to_kafka(self, token, lat, lng, gcm_token):
        validated = self.validate_token(token)
        if not validated['success']:
            return validated
        aws = AWS(self.aws_credentials['access_token'], self.aws_credentials['access_token_secret'])
        response = aws.add_to_kafka(token, lat, lng, gcm_token)
        return response

    def publish_sns_results(self, token, gcm_token, lat, lng):
        db, client = self.get_connection()
        aws = AWS(self.aws_credentials['access_token'], self.aws_credentials['access_token_secret'])
        sns_data = list(db.sns_info.find({"_id": token}))
        if not sns_data or len(sns_data)==0:
            end_point_arn = aws.create_application_endpoint(gcm_token)['end_point_arn']
            db.sns_info.insert_one({"_id": token, "gcm_token": gcm_token, "end_point_arn": end_point_arn})
        else:
            sns_data = sns_data[0]
            if sns_data['gcm_token'] != gcm_token:
                db.sns_info.delete_many({"_id": token})
                aws.delete_sns_endpoint(sns_data['end_point_arn'])
                end_point_arn = aws.create_application_endpoint(gcm_token)['end_point_arn']
                db.sns_info.insert_one({"_id": token, "gcm_token": gcm_token, "end_point_arn": end_point_arn})
            else:
                end_point_arn = sns_data['end_point_arn']
        result = self.get_parking_locations(token, lat, lng)
        aws.publish_sns_results(end_point_arn, result)
        client.close()
        return {"success": True}

    def add_random_data(self, gcm_token, lat, lng, token):
        db, client = self.get_connection()
        db.random_data.insert_one({"gcm_token": gcm_token, "lat": lat, "lng": lng, "token": token})
        client.close()
