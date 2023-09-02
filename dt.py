import mysql.connector
import datetime as datetime
con = mysql.connector.connect(
host="localhost", user="root",
password="root@2023", database="personal_details",port=3306)
cursor = con.cursor()
cursor = con.cursor(buffered=True)
cursor.execute("select date_time from person")
table = cursor.fetchall()
cursor.execute("select p_id from person")
p_id=cursor.fetchall()

def calculate_duration(start_time, end_time):
    duration = end_time - start_time
    return duration.total_seconds()

# Example list of face detection timestamps
face_detection_timestamps =list(str(table))
# Convert timestamps to datetime objects
datetime_format = "%d-%m-%Y %H:%M"
timestamps = [datetime.datetime.strptime(ts, datetime_format) for ts in face_detection_timestamps]

# Calculate total duration
if len(timestamps) >= 2:
    start_time = timestamps[0]
    end_time = timestamps[-1]
    total_duration = calculate_duration(start_time, end_time)
    cursor.execute("update table personal_details set duration={} where p_id={}".format(total_duration,p_id))
    #print(f"Total face duration: {total_duration:.2f} seconds")
else:
    print("Not enough timestamps to calculate duration.")
