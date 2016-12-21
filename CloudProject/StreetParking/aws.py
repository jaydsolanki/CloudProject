import boto3
from kafka import KafkaConsumer, KafkaProducer, SimpleClient
from .mongo import MongoQuery
from CloudProject.settings import MONGO_URL, KAFKA_URL
import json

mongo_query = MongoQuery(MONGO_URL)
access_token, secret_access_token = mongo_query.get_aws_credentials()
topic_name = 'location_requests'
client = SimpleClient(KAFKA_URL)
client.ensure_topic_exists(topic_name)
producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])


def add_to_kafka(token, lat, lng, topic_arn):
    request_data = json.dumps({"token":token, "lat":lat, "lng":lng, "topic_arn": topic_arn})
    producer.send(topic_name, request_data.encode())
    return {"success": True, "topic_arn": topic_arn}


def create_sns_topic(topic_name):
    sns = boto3.resource('sns',aws_access_key_id=access_token, aws_secret_access_key=secret_access_token)
    topic = sns.create_topic(Name=topic_name)
    return topic


def publish_sns_results(topic_arn, results):
    sns = boto3.client('sns',aws_access_key_id=access_token, aws_secret_access_key=secret_access_token)
    sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps({'default':json.dumps(results)})
    )