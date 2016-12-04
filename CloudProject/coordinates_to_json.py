import sys
print ("Enter Information. At any time press Ctrl-C to exit...")
filename = "street_ave_info.json"
f = open(filename,'a')
if sys.version_info[0]==3:
    raw_input = input
while True:
    try:
        street_ave_name = raw_input("Enter Street Ave Name: ")
        between1 = raw_input("Between 1st name: ")
        between2 = raw_input("Between 2nd name: ")
        parking_allowed = "true"
        lat_long = raw_input("Latitude, Longitude: ")
        lat = lat_long.split(",")[0].strip()
        lon = lat_long.split(",")[1].strip()
        json_entry = '{"street_ave_name": "'+street_ave_name+'", "between": "'+between1+','+between2+'", parking_allowed: "'+parking_allowed+'", "location":{"lat":'+lat+', "lon":'+lon+'}}'
        print("Added: "+json_entry)
        f = open(filename,'a')
        f.write(json_entry+"\n")
        f.close()
    except:
        break
