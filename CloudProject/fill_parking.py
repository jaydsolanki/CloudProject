from pymongo import MongoClient
import random

server = 'localhost'
server = '54.244.188.248'

server = 'localhost'

client = MongoClient(server)

db = client.street_parking




def reset_parking_spots():
    parking_objs = db.parking_data.find()
    total_parking_spots=db.parking_data.aggregate([{"$group":{"_id":None, "total":{"$sum":"$parking_spots_available"}}}])
    total_parking_spots = total_parking_spots.next()
    total_parking_spots = total_parking_spots['total']
    count = 250
    mark = 0
    for parking_obj in parking_objs:
        db.parking_data.update_one({"_id":parking_obj["_id"]},{"$set":{"parking_spots_available":parking_obj['parking_spots']}})
        count -= 1
        mark+=parking_obj['parking_spots']
        if count==0:
            count=250
            print ("Work Done: "+str((mark*1.0)/total_parking_spots*100.0))



def fill_parking(percent, max_fill=None):
    total_parking_spots=db.parking_data.aggregate([{"$group":{"_id":None, "total":{"$sum":"$parking_spots_available"}}}])
    total_parking_spots = total_parking_spots.next()
    total_parking_spots = total_parking_spots['total']
    spots_to_fill = int(total_parking_spots*percent/100)
    count = 500
    spots_to_fill_bk = spots_to_fill
    spots_filled = 0
    while spots_to_fill > 0:
        print("starting to fill parking")
        parking_objs = list(db.parking_data.find())
        random.shuffle(parking_objs)
        for parking_obj in parking_objs:
            if max_fill:
                remove_spots = random.randint(0,max_fill)
            else:
                remove_spots = 1
            if remove_spots>spots_to_fill:
                remove_spots = spots_to_fill
            if remove_spots>parking_obj['parking_spots_available']:
                remove_spots = parking_obj['parking_spots_available']
            spots_to_fill -= remove_spots
            if spots_to_fill<=0:
                break
            spots_filled += remove_spots
            count -=1
            if count==0:
                count = 500
                print ("Work done: "+str((spots_filled*1.0)/spots_to_fill_bk*100.0))
            db.parking_data.update_one({"_id": parking_obj['_id']},{"$inc":{"parking_spots_available": (-1)*remove_spots}})
