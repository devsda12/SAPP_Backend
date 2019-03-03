from flask import Flask

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

        #Here in the bottom of the run the actual api is run with flaskapp.
        self.flaskApp.run(host="0.0.0.0")

if __name__ == "__main__":
    flask_Main().run()