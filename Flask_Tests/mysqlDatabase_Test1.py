import mysql.connector

database = mysql.connector.connect(host="localhost", user="root", passwd="SAPP")

cursor = database.cursor()

cursor.execute("SHOW DATABASES")

for x in cursor:
    print(x)