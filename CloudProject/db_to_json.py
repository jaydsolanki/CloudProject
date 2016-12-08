import sqlite3

def db_to_json(file_name, output_file_name):
    conn = sqlite3.connect(file_name)
    cursor = conn.cursor()
    cursor.execute("select * from parking_data")
    records = cursor.fetchall()
    f = open(output_file_name,'w')
    for record in records:
        parking_allowed = 'true' if record[6]==1 else 'false'
        json_record = '{"location":{"lat":'+str(record[1])+', "lng":'+str(record[2])+'}, "parking_spots":'+str(record[3])+', "street_ave_name":"'+str(record[4])+'", "between_street_ave":"'+str(record[5])+'", "parking_allowed":'+parking_allowed+', "parking_on":"'+record[7]+'"}'
        f.write(json_record+"\n")
    f.close()
    cursor.close()
    conn.close()

db_to_json('db.sqlite3','parking_data.json')
