from flask import Flask
from flask import request
import database_Handlers

class flask_Main:

    def __init__(self):
        #Defining the flask app
        self.flaskApp = Flask(__name__)

    #The main run function that runs when the program is started
    def run(self):

        #The testshake function that runs when the app asks if the api is online
        @self.flaskApp.route("/testshake")
        def testshake():
            return "Testshake Succesfull"

        #The login function that checks the send information with the database
        @self.flaskApp.route("/sapp_login", methods=["POST"])
        def login():
            if request.is_json:
                requestContent = request.get_json()
                loginResult = database_Handlers.database_Handlers().login(requestContent)
                if not loginResult:
                    return "Login Unsuccessful"
            else:
                return "Login Unsuccessful"

        #Here in the bottom of the run the actual api is run with flaskapp.
        self.flaskApp.run(host="0.0.0.0")

if __name__ == "__main__":
    flask_Main().run()