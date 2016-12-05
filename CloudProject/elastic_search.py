from elasticsearch import Elasticsearch
import json

mapping = \
    {
        "mappings": {
            "parking": {
                "properties": {
                    "street_ave_name": {
                        "type": "string"
                    },
                    "between":{
                        "type": "string"
                    },
                    "parking_allowed": {
                        "type":  "string"
                    },
                    "location": {
                        "type": "geo_point"
                    },
                }
            }
        }
    }

index_name = "street_parking"
es = Elasticsearch()
es.indices.create(index=index_name, body=mapping, ignore=400)
file_name = "street_ave_info.json"
f = open(file_name, 'r')
data = f.read().split("\n")
for d in data:
    if d.strip()!="":
        es.index(index=index_name, doc_type="parking", body=json.loads(d))
        print (d)
print("\n\n")
lat = str(40.746701)
lng = str(-73.992072)
hits = es.search(index=index_name,body={"from":0, "size":5000 ,"query":{"match_all":{}},"filter":{"geo_distance":{"distance":str(100)+"km","location":{"lat":lat, "lon":lng}}}})


print(hits['hits'])