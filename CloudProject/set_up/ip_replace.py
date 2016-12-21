import sys
import urllib, json

def get_public_ip():
	data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
	return str(data["ip"])

file = open(sys.argv[1],'r')
data = file.read().split("\n")
for i in range(len(data)):
	if "#advertised.listeners=PLAINTEXT://your.host.name:9092" in data[i]:
		data[i] = data[i].replace("your.host.name",get_public_ip()).replace("#adv","adv")

file.close()
file = open(sys.argv[1],'w')
for d in data:
	file.write(d+"\n")
file.close()
