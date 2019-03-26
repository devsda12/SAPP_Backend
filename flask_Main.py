from flask import Flask
from flask import request
import database_Handlers

class flask_Main:

    def __init__(self):
        #Defining the flask app
        self.flaskApp = Flask(__name__)

        #Defining the dictionary for binding account ID's to device ID's
        self.idBindDict = {}

    #The main run function that runs when the program is started
    def run(self):

        # The testshake function that runs when the app asks if the api is online
        @self.flaskApp.route("/testshake")
        def testshake():
            return "Testshake Succesfull"


        #The first handshake function to give a device an id
        @self.flaskApp.route("/device_identifier", methods=["POST"])
        def device_identifier():
            if request.is_json:
                requestContent = request.get_json()
                identificationResult = database_Handlers.database_Handlers().identifyDevice(requestContent)
                return '{device_Id:"' + identificationResult + '"}'
            else:
                return "Identification Unsuccessful"


        #The login function that checks the send information with the database
        @self.flaskApp.route("/sapp_login", methods=["POST"])
        def sapp_login():
            if request.is_json:
                requestContent = request.get_json()
                loginResult = database_Handlers.database_Handlers().login(requestContent)
                if not loginResult:
                    return "Login Unsuccessful"

                #If the login is succesful the account ID needs to be bound to the device ID for access
                requestedDeviceId = requestContent["device_Id"]
                self.idBindDict[requestedDeviceId] = loginResult   #ID binding turned off for now until you can actually login
                return '{acc_Id:"' + loginResult + '"}'
            else:
                return "Login Unsuccessful"


        #The function to create a new account in the database
        @self.flaskApp.route("/sapp_createAccount", methods=["POST"])
        def sapp_createAccount():
            if request.is_json:
                requestContent = request.get_json()
                createAccountResult = database_Handlers.database_Handlers().create_Account(requestContent)
                if not createAccountResult:
                    return "Account Creation Unsuccessful"

                #If the creation is succesful the account id needs to be returned to the user to store it in the account database
                return '{acc_Id:"' + createAccountResult + '"}'
            else:
                return "Account Creation Unsuccessful"


        #Returning the chats for the conv_select activity
        @self.flaskApp.route("/sapp_getChats", methods=["POST"])
        def sapp_getChats():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        chatResult = database_Handlers.database_Handlers().getChatsV3(requestContent)
                        if not chatResult:
                            return "No chats found"

                        returnstring = "["
                        for item in chatResult:
                            returnstring = returnstring + '{table_Name:"' + item + '", partner_Id:"' + str(chatResult[item][0]) + '", partner_Username:"' + str(chatResult[item][1]) + '", last_Message:"' + str(chatResult[item][2]) + '", message_Sender:"' + str(chatResult[item][3]) + '", message_Date:"' + str(chatResult[item][4]) + '"},'
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        return returnstring

            #Returning string if one of the ifs did not execute
            return "Unsuccessful"


        # Searching for users
        @self.flaskApp.route("/sapp_findUser", methods=["POST"])
        def sapp_findUser():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        userResults = database_Handlers.database_Handlers().findUser(requestContent)
                        if not userResults:
                            return "No users found"

                        returnstring = "["
                        for item in userResults:
                            returnstring = returnstring + '{acc_Username:"' + item + '", acc_Id:"' + userResults[item] + '"},'
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        return returnstring

            # Returning string if one of the ifs did not execute
            return "Unsuccessful"


        # Create new table
        @self.flaskApp.route("/sapp_createTable", methods=["POST"])
        def sapp_createTable():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:

                        tableResults = database_Handlers.database_Handlers().createTable(requestContent)

                        if not tableResults:
                            return "Not Inserted"

                        return '{insertResult:"true"}'

            return "Not Inserted"


        # Removes device and account id's from dictionairy
        @self.flaskApp.route("/sapp_logout", methods=["POST"])
        def sapp_logout():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        del self.idBindDict[requestdevice_id]
                        return '{deleteResult:"true"}'

            return "Unsuccessful"


        # Retrieve messages of a chat
        @self.flaskApp.route("/sapp_getCompleteChat", methods=["POST"])
        def sapp_getCompleteChat():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        chatResult = database_Handlers.database_Handlers().getCompleteChat(requestContent)

                        if not chatResult:
                            return "Error retrieving chat"

                        returnstring = "["
                        for item in chatResult:
                            returnstring = returnstring + '{Sender:"' + item + '", Receiver:"' + str(
                                chatResult[item][0]) + '", Message:"' + str(
                                chatResult[item][1]) + '", DateTime:"' + str(chatResult[item][2]) + '"},'
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        return returnstring

            else:
                return "unsuccessful"


        # Retrieve messages after a given datetime of a chat
        @self.flaskApp.route("/sapp_getPartialChat", methods=["POST"])
        def sapp_getPartialChat():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        chatResult = database_Handlers.database_Handlers().getPartialChat(requestContent)

                        if not chatResult:
                            return "Error retrieving chat"

                        returnstring = "["
                        for item in chatResult:
                            returnstring = returnstring + '{Sender:"' + str(chatResult[item][0]) + '", Receiver:"' + str(
                                chatResult[item][1]) + '", Message:"' + str(
                                chatResult[item][2]) + '", DateTime:"' + str(chatResult[item][3]) + '"},'
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        return returnstring

            else:
                return "unsuccessful"


        # cleat a single chat of all messages
        @self.flaskApp.route("/sapp_clearChat", methods=["POST"])
        def sapp_clearChat():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        result = database_Handlers.database_Handlers().clearChat(requestContent)

                        return result

            else:
                return "unsuccessful"


        @self.flaskApp.route("/sapp_addMessage", methods=["POST"])
        def sapp_addMessage():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id]:
                        result = database_Handlers.database_Handlers().addMessage(requestContent)

                        if result:
                            return '{insertResult:"true"}'
                        else:
                            return "unsuccessful"

            else:
                return "unsuccessful"

        #Here in the bottom of the run the actual api is run with flaskapp.
        self.flaskApp.run(host="0.0.0.0")

if __name__ == "__main__":
    flask_Main().run()