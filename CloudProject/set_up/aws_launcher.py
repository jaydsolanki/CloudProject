import boto3
import time
from botocore.exceptions import ClientError
image_id = 'ami-b7a114d7' #Ubuntu 64 bit
instance_type = "t2.micro"
key_name = "jds797_bigdata"
sec_group_name = 'CloudProjectGroup'
sec_group_description = 'Group Created for Cloud Project'
ec2 = boto3.resource("ec2")

user_data_mongo = \
"""#cloud-config

runcmd:
 - sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 -y
 - echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
 - sudo apt-get --allow-unauthenticated update
 - sudo apt-get install --allow-unauthenticated -y mongodb-org
 - sudo service mongod start
"""
 # - sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 -y
 # - echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
 # - sudo apt-get --allow-unauthenticated update
 # - sudo apt-get install --allow-unauthenticated -y mongodb-org
 # - sudo service mongod start

conn_args = {
    'aws_access_key_id': 'YOURKEY',
    'aws_secret_access_key': 'YOUSECACCESSKEY',
    'region_name': 'us-east-1'
}

try:
    response = ec2.create_security_group(GroupName=sec_group_name,Description=sec_group_description)
    response.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
    response.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=27017,ToPort=27017)
except ClientError as e:
    if "already exists" in e.response['Error']['Message']:
        pass # Ignore the Group already exists
    else:
        raise (e)
except Exception as e:
    raise (e)


instances = ec2.create_instances(ImageId=image_id,
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=instance_type,
                    UserData=user_data_mongo,
                    KeyName=key_name,
                    SecurityGroups=[sec_group_name])

instance = instances[0]
instance.wait_until_running()
instance.reload()
ip_address_mongo_server = instance.public_ip_address
print ("Mongo Instance\n\tssh -i jds797_bigdata.pem ubuntu@"+str(ip_address_mongo_server))

'''
sec_group_name = 'CloudProjectAws'
sec_group_description = 'Group Created for Cloud Project AWS '
instance_type = "t2.medium"

user_data_kafka = \
"""#cloud-config

runcmd:
 - sudo apt-get update -y
 - sudo apt-get install default-jre -y
 - sudo apt-get install zookeeperd -y
 - cd /home/ubuntu
 - wget http://apache.claz.org/kafka/0.10.1.0/kafka_2.10-0.10.1.0.tgz
 - sudo mkdir /opt/Kafka
 - sudo tar -xvf kafka_2.10-0.10.1.0.tgz -C /opt/Kafka/
 - cd /opt/Kafka/kafka_2.10-0.10.1.0/config
 - sudo wget https://s3-us-west-1.amazonaws.com/jds797/ip_replace.py
 - sudo chmod +x ip_replace.py
 - cd /home/ubuntu
 - sudo apt-get install python-pip -y
 - sudo pip install kafka-python
 - wget https://s3-us-west-1.amazonaws.com/jds797/consumer_worker.py
 - sudo chmod +x consumer_worker.py
"""
# cd /opt/Kafka/kafka_2.10-0.10.1.0/config/
# sudo python ip_replace.py server.properties
# sudo nohup /opt/Kafka/kafka_2.10-0.10.1.0/bin/kafka-server-start.sh /opt/Kafka/kafka_2.10-0.10.1.0/config/server.properties > /tmp/kafka.log 2>&1 &
# sudo nohup python consumer_worker.py > /tmp/consumer_worker.log 2>&1 &
try:
    response = ec2.create_security_group(GroupName=sec_group_name,Description=sec_group_description)
    response.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
    response.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=9092,ToPort=9092)
except ClientError as e:
    if "already exists" in e.response['Error']['Message']:
        pass # Ignore the Group already exists
    else:
        raise (e)
except Exception as e:
    raise (e)


instances = ec2.create_instances(ImageId=image_id,
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=instance_type,
                    UserData=user_data_kafka,
                    KeyName=key_name,
                    SecurityGroups=[sec_group_name])

instance = instances[0]
instance.wait_until_running()
instance.reload()
ip_address_kafka_server = instance.public_ip_address
print ("Kafka Instance\n\tssh -i jds797_bigdata.pem ubuntu@"+str(ip_address_kafka_server))
'''
