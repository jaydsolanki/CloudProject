from elasticsearch import Elasticsearch

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
                    "sentiment": {
                        "type": "string"
                    }
                }
            }
        }
    }


