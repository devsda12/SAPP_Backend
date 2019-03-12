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
                #self.idBindDict[requestedDeviceId] = loginResult   #ID binding turned off for now until you can actually login
                return '{acc_Id:"' + loginResult + '"}'
            else:
                return "Login Unsuccessful"

        @self.flaskApp.route("/", methodes=["POST"])
        def sapp_chats():
            if request.is_json:
                requestContent = request.get_json()
                requestedevice_id = requestContent["device_id"]
                if requestedevice_id in self.idBindDict:

                    chatResult = database_Handlers.database_Handlers().chats(requestContent)

            else:
                return "Unsuccessful"

        #Here in the bottom of the run the actual api is run with flaskapp.
        self.flaskApp.run(host="0.0.0.0"


if __name__ == "__main__":
    flask_Main().run()