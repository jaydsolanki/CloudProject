import multiprocessing
import os
import time
from kafka import KafkaConsumer, SimpleClient
import urllib2

django_project_url = ""
topic_name = 'location_requests'

client = SimpleClient('localhost')
client.ensure_topic_exists(topic_name)
consumer = KafkaConsumer(topic_name, bootstrap_servers=['localhost'])
queue_obj = multiprocessing.Queue()


def worker_main(queue):
    while True:
        item = queue.get(True)
        print ("Received request: "+str(item))
        try:
            urllib2.urlopen(django_project_url+"/sns_request?sns_parameter="+str(item.response))
        except Exception as e:
            print(e)
pool_obj = multiprocessing.Pool(20, worker_main,(queue_obj,))

for msg in consumer:
    queue_obj.put(msg)
