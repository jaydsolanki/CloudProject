1. make sure you have the latest copy of https://s3-us-west-1.amazonaws.com/jds797/consumer_worker.py
2. run aws_launcher.py
3. In settings.py add the ip addresses of Kafka and Mongo
4. SSH both mongo and kafka instances
5. Go to the Mongo Instance then change the bind_ip parameter to 0.0.0.0 by `sudo nano /etc/mongod.conf`
6. do `sudo server mongodrestart`. Run the file `python add_data_to_db.py` which will dump all the data to mongo server
7. For the Kafka instance follow the instructions in aws_launcher
8. In Kafka Instance make sure the file in /ubuntu/consumer_worker.py you add the elastic beanstalk url of the project
