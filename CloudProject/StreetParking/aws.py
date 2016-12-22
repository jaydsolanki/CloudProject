# Native libs import
import boto3
import json
from kafka import KafkaProducer, SimpleClient

# Project imports
from CloudProject.settings import KAFKA_TOPIC_NAME, SNS_APPLICATION_ARN, KAFKA_URL

client = SimpleClient(KAFKA_URL)
# This ensures that the topic is created on Kafka
client.ensure_topic_exists(KAFKA_TOPIC_NAME)
# This is the actual producer which wiill push the topics to Kafka
producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])


class AWS:
    def __init__(self, access_token, access_token_secret):
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def add_to_kafka(self, token, lat, lng, gcm_token):
        request_data = json.dumps({"token": token, "lat": lat, "lng": lng, "gcm_token": gcm_token})
        producer.send(KAFKA_TOPIC_NAME, request_data.encode())
        return {"success": True}

    def publish_sns_results(self, end_point_arn, results):
        sns = boto3.client('sns', aws_access_key_id=self.access_token, aws_secret_access_key=self.access_token_secret)
        sns.publish(
            TargetArn=end_point_arn,
            Message=json.dumps(results)
        )

    def create_application_endpoint(self, gcm_token):
        client = boto3.client('sns', aws_access_key_id=self.access_token, aws_secret_access_key=self.access_token_secret)
        end_point_result = client.create_platform_endpoint(
            PlatformApplicationArn=SNS_APPLICATION_ARN,
            Token=gcm_token
        )
        return {"success": True, 'end_point_arn': end_point_result['EndpointArn']}

    def delete_sns_endpoint(self, end_point_arn):
        client = boto3.client('sns', aws_access_key_id=self.access_token, aws_secret_access_key=self.access_token_secret)
        client.delete_endpoint(EndpointArn=end_point_arn)
        return {"success": True}
