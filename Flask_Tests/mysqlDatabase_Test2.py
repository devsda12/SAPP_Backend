import mysql.connector

database = mysql.connector.connect(host="localhost", user="sapp_user", passwd="SAPP-PASSWORD_F0R-YOU", database="SAPP_Backend")
cursor = database.cursor()

cursor.execute('SELECT device_Id FROM Device_Table WHERE device_Id = "' + "1234567890" + '";')

result = cursor.fetchall()

if len(result) == 0:
    print("Length is 0")
else:
    print(result[0])