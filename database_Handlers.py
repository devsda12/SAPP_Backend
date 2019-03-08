import string
import random
import mysql.connector
from flask import request

class database_Handlers:

    def __init__(self):

        #Declaring the global database handler and its cursor
        self.sapp_database = mysql.connector.connect(host="localhost", user="sapp_user", passwd="SAPP-PASSWORD_F0R-YOU", database="SAPP_Backend")
        self.sapp_cursor = self.sapp_database.cursor()

    #The device identification database function
    def identifyDevice(self, requestContent):
        requestedId = requestContent["device_Id"]

        if requestedId != "0":
            self.sapp_cursor.execute('SELECT device_Id FROM Device_Table WHERE device_Id = "' + requestedId + '";')
            result = self.sapp_cursor.fetchall()
            if len(result) > 0:
                return result[0][0]

        inserted = False
        while not inserted:
            new_id = self.id_generator()
            self.sapp_cursor.execute('SELECT device_Id FROM Device_Table WHERE device_Id = "' + new_id + '";')
            result = self.sapp_cursor.fetchall()
            if len(result) == 0:
                self.sapp_cursor.execute('INSERT INTO Device_Table (device_Id) VALUES ("' + new_id + '");')
                self.sapp_database.commit()
                inserted = True

        return new_id


    #The login database function
    def login(self, requestContent):
        requestedUsername = requestContent["acc_Username"]
        requestedPassword = requestContent["acc_Password"]

        #Using query on the database
        self.sapp_cursor.execute('SELECT acc_Id FROM Acc_Table WHERE acc_Username = "' + requestedUsername + '" AND acc_Password = "' + requestedPassword + '";')
        result = self.sapp_cursor.fetchall()

        if len(result) == 0:
            return False
        else:
            requestedId = result[0][0]
            return requestedId


    #The create account database function
    def create_Account(self, requestContent):
        requestedUsername = requestContent["acc_Username"]
        requestedPassword = requestContent["acc_Password"]

        #Querying the database to see if username already exists
        self.sapp_cursor.execute('SELECT acc_Id FROM Acc_Table WHERE acc_Username = "' + requestedUsername + '";')
        result = self.sapp_cursor.fetchall()

        #If this username exists it is rejected
        if len(result) > 0:
            return False

        #If the username does not yet exist it is inserted into the database
        newAcc_Id = self.id_generator()
        self.sapp_cursor.execute('INSERT INTO Acc_Table (acc_Id, acc_Username, acc_Password) VALUES ("' + newAcc_Id + '", "' + requestedUsername + '", "' + requestedPassword + '");')
        self.sapp_database.commit()
        return newAcc_Id

    #NON-database functions

    #Function to generate 10 digit ID
    def id_generator(self, size=10, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))