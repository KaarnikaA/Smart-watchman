# import required modules
from twilio.rest import Client
import keys
client=Client(keys.acc_sid,keys.acc_token)
import mysql.connector
default_count=3
safe_duration=30
# create connection object
con = mysql.connector.connect(
host="localhost", user="root",
password="root@2023", database="personal_details",port=3306)

# create cursor object
cursor = con.cursor()
cursor = con.cursor(buffered=True)


# updating danger varoable

def update_danger(name,permitted,duration_min):
		print(name,permitted,duration_min)
		if(duration_min>=safe_duration):
			if(not(permitted)):
				#cursor.execute("update person set d_count=d_count+1 ")
				message= client.messages.create(
    			body="DANGER and not permitted",
    			from_=keys.from_no,
    			to=keys.to_no)
				#print("DANGER and not permitted")
			else:
				message= client.messages.create(
    			body="DANGER but permitted",
    			from_=keys.from_no,
    			to=keys.to_no)
				
		else:
			#print("SAFE")
			message= client.messages.create(
    			body="SAFE",
    			from_=keys.from_no,
    			to=keys.to_no)

# # display all records
cursor.execute("select name,permitted,duration_min from person")
table = cursor.fetchall()

# # traversing table
for name,permitted,duration_min in table:
	update_danger(name,permitted,duration_min)
	#print(row)
	#msg()
	
	
	
# closing cursor connection
cursor.close()

# closing connection object
con.close()

