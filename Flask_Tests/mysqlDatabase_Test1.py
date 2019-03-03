import mysql.connector

database = mysql.connector.connect(host="localhost", user="sapp_user", passwd="SAPP-PASSWORD_F0R-YOU")

cursor = database.cursor()

cursor.execute("SHOW TABLES")

for x in cursor:
    print(x)