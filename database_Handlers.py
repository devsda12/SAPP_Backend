import mysql.connector

class database_Handlers:

    def __init__(self):

        #Declaring the global database handler and its cursor
        self.sapp_database = mysql.connector.connect(host="localhost", user="sapp_user", passwd="SAPP-PASSWORD_F0R-YOU")
        self.sapp_cursor = self.sapp_database.cursor()

    #The login database function
    def login(self):
        dummy = ""