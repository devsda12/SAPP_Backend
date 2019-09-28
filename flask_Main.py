from flask import Flask
from flask import request
import database_Handlers
import firebase_Handler

import firebase_admin
from firebase_admin import credentials

class flask_Main:

    def __init__(self):
        #Defining the flask app
        self.flaskApp = Flask(__name__)

        #Defining the dictionary for binding account ID's to device ID's
        self.idBindDict = {}

        #Defining dictionary for storing acc_Id's where firebase requests went wrong
        self.pendingFirebaseRequests = {}

        #Defining a list to store profilepic id's that may be requested for a short period of time
        self.profilePicsToBeRequested = []

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

                #Now corresponding the profile picture id's if this was send
                newProfilePictureId = database_Handlers.database_Handlers().checkProfilePictureIdAfterLogin(requestContent, loginResult[0])

                #If the login is succesful the account ID needs to be bound to the device ID for access
                requestedDeviceId = requestContent["device_Id"]

                requestedFirebaseToken = requestContent["device_FirebaseToken"]
                self.idBindDict[requestedDeviceId] = [loginResult[0], requestedFirebaseToken]
                print("LoginPrint: " + str(self.idBindDict))

                database_Handlers.database_Handlers().addStat('logins')

                if not newProfilePictureId or newProfilePictureId == None:
                    return '{acc_Id:"' + loginResult[0] + '", profilePicId:"null", acc_Quote:"' + loginResult[1] + '"}'
                else:
                    self.profilePicsToBeRequested.append(newProfilePictureId)
                    return '{acc_Id:"' + loginResult[0] + '", profilePicId:"' + newProfilePictureId + '", acc_Quote:"' + loginResult[1] + '"}'
            else:
                return "Login Unsuccessful"


        #Function to update a given and bound firebase token of a user
        @self.flaskApp.route("/sapp_updateFirebaseToken", methods=["POST"])
        def sapp_updateFirebaseToken():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                requestfirebase_token = requestContent["newToken"]
                if requestdevice_id in self.idBindDict:
                    print("UpdateFirebaseTokenPrint: " + str(self.idBindDict[requestdevice_id][0]))
                    print("UpdateFirebaseTokenPrint: " + requestaccount_id)
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        self.idBindDict[requestdevice_id][1] = requestfirebase_token
                        print("Firebase Token: " + requestfirebase_token)
                        print("UpdateFirebaseTokenPrint: " + str(self.idBindDict))

                        #Now checking if there was an previous unsuccesful push for a new message
                        if requestaccount_id in self.pendingFirebaseRequests:
                            for conv in self.pendingFirebaseRequests[requestaccount_id]:
                                firebase_Handler.firebase_Handler().sendRefreshRequest(requestfirebase_token, conv)
                            del self.pendingFirebaseRequests[requestaccount_id]


                        return '{insertedToken:"' + requestfirebase_token + '"}'
            return "Unsuccessful"


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
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        chatResult = database_Handlers.database_Handlers().getChatsV4(requestContent)
                        if not chatResult:
                            return "No chats found"

                        returnstring = "["
                        for item in chatResult:
                            returnstring = returnstring + '{table_Name:"' + item + '", partner_Id:"' + str(chatResult[item][0]) + '", partner_Username:"' + str(chatResult[item][1]) + '", partner_Quote:"' + str(chatResult[item][2]) + '", last_Message:"' + str(chatResult[item][3]) + '", message_Sender:"' + str(chatResult[item][4]) + '", message_Date:"' + str(chatResult[item][5]) + '", newProfilePictureId:"' + str(chatResult[item][6]) + '"},'
                            if chatResult[item][5] != "null":
                                self.profilePicsToBeRequested.append(chatResult[item][6])
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        return returnstring

            #Returning string if one of the ifs did not execute
            return "Unsuccessful"


        # Retrieve a needed profile picture from the database when it was enabled in getChats
        @self.flaskApp.route("/sapp_getProfilePic/<profilePicId>", methods=["GET"])
        def sapp_getProfilePic(profilePicId):
            #First checking if the profilePicId is in the current list of profile pic id's that may be requested
            if profilePicId in self.profilePicsToBeRequested:
                #First removing it from the list
                self.profilePicsToBeRequested.remove(profilePicId)

                #Now calling a function in database handler to fetch the image from the database
                imageBytes = database_Handlers.database_Handlers().fetchProfilePic(profilePicId)

                return imageBytes

            #The requested profile picture is not currently present
            return "The requested profile picture is not currently present"


        # Searching for users
        @self.flaskApp.route("/sapp_findUser", methods=["POST"])
        def sapp_findUser():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        userResults = database_Handlers.database_Handlers().findUser(requestContent)
                        if not userResults:
                            return "No users found"

                        returnstring = "["
                        for item in userResults:
                            returnstring = returnstring + '{acc_Username:"' + item + '", acc_Id:"' + userResults[item][0] + '", acc_Quote:"' + userResults[item][1] + '"},'
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
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:

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
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
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
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        chatResult = database_Handlers.database_Handlers().getCompleteChat(requestContent)

                        if not chatResult:
                            return "Error retrieving chat"

                        returnstring = "["
                        for item in chatResult:
                            returnstring = returnstring + '{Sender:"' + str(
                                chatResult[item][0]) + '", Receiver:"' + str(
                                chatResult[item][1]) + '", Message:"' + str(
                                chatResult[item][2]) + '", DateTime:"' + str(chatResult[item][3]) + '"},'
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        print("GetCompleteChatPrint: " + returnstring)
                        return returnstring

            return "unsuccessful"


        # Retrieve messages after a given datetime of a chat
        @self.flaskApp.route("/sapp_getPartialChat", methods=["POST"])
        def sapp_getPartialChat():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
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

            return "unsuccessful"


        # cleat a single chat of all messages
        @self.flaskApp.route("/sapp_clearChat", methods=["POST"])
        def sapp_clearChat():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        result = database_Handlers.database_Handlers().clearChat(requestContent)

                        return result

            return "unsuccessful"


        #Add a single message to the database
        @self.flaskApp.route("/sapp_addMessage", methods=["POST"])
        def sapp_addMessage():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]
                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        result = database_Handlers.database_Handlers().addMessage(requestContent)

                        if result:
                            #Firebase message part under here (first checking if the targeted acc id is bound)
                            targetedId = database_Handlers.database_Handlers().fetchAccIdByUsername(requestContent["Receiver"])
                            for item in self.idBindDict:
                                if targetedId == self.idBindDict[item][0]:
                                    targetedFirebaseId = self.idBindDict[item][1]

                                    #Now calling the firebase handler and if unsuccesful adding the details to the pendingFirebaseRequests dict
                                    try:
                                        firebase_Handler.firebase_Handler().sendRefreshRequest(targetedFirebaseId, requestContent["conv_Id"])
                                    except:
                                        print("AddMessage Print: Firebase handler caused exception, storing the targeted acc_Id in dict")
                                        if targetedId in self.pendingFirebaseRequests:
                                            if requestContent["conv_Id"] not in self.pendingFirebaseRequests[targetedId]:
                                                self.pendingFirebaseRequests[targetedId].append(requestContent["conv_Id"])
                                        else:
                                            self.pendingFirebaseRequests[targetedId] = [requestContent["conv_Id"]]


                            database_Handlers.database_Handlers().addStat('messages')
                            return '{insertResult:"true"}'
                        else:
                            return "unsuccessful"

            return "unsuccessful"


        # Request the statistical data from the database handler and send it to the application
        @self.flaskApp.route("/sapp_requestStats", methods=["POST"])
        def sapp_requestStats():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent[0]["device_Id"]
                requestaccount_id = requestContent[0]["acc_Id"]

                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        result = database_Handlers.database_Handlers().requestStats()

                        if not result:
                            return "Error retrieving chat"

                        returnstring = "["
                        for item in result:
                            returnstring = returnstring + '{logins:"' + str(result[item][0]) + '", messages:"' + str(result[item][1]) + '", weekday:"' + str(item) + '"},'
                        returnstring = returnstring[:-1]
                        returnstring = returnstring + "]"
                        print("RequestStatsStringPrint: " + returnstring)
                        return returnstring

            else:
                return "unsuccessful"


        # Function to change the users password
        @self.flaskApp.route("/sapp_changePass", methods=["POST"])
        def sapp_changePass():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]

                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        result = database_Handlers.database_Handlers().changePass(requestContent)
                        if result:
                            print("it works")
                            return '{insertResult:"true"}'
            print("it doesnt work")
            return "unsuccessful"


        #Function to change the users profile picture
        @self.flaskApp.route("/sapp_changeProfilePic", methods=["POST"])
        def sapp_changeProfilePic():
            #Checking if the new profile picture is present in the files
            if "profilePic" not in request.files:
                print("Change profile pic print: There was no profile picture send")
                return "Upload unsuccessful"

            #Checking the device and acc id
            if str(request.form.get("device_Id")) in self.idBindDict:
                if str(request.form.get("acc_Id")) == self.idBindDict[str(request.form.get("device_Id"))][0]:
                    profile_Pic = request.files["profilePic"]
                    profile_PicBytes = profile_Pic.read()
                    insertResult = database_Handlers.database_Handlers().changeProfilePic(profile_PicBytes, str(request.form.get("acc_Id")))

                    if not insertResult:
                        return "Upload unsuccessful"
                    else:
                        return "Upload successful"

            print("Change profile pic print: User not logged in or inserting went wrong")
            return "Upload unsuccessful"


        @self.flaskApp.route("/sapp_changeQuote", methods=["POST"])
        def sapp_changeQuote():
            if request.is_json:
                requestContent = request.get_json()
                requestdevice_id = requestContent["device_Id"]
                requestaccount_id = requestContent["acc_Id"]

                if requestdevice_id in self.idBindDict:
                    if requestaccount_id == self.idBindDict[requestdevice_id][0]:
                        result = database_Handlers.database_Handlers().changeQuote(requestContent)
                        if result:
                            print("it works")
                            return '{insertResult:"true"}'
            print("it doesnt work")
            return "unsuccessful"

        #For now defined here, this could be changed in the future if needed. Caused errors in the init function of the firebase handler
        creds = credentials.Certificate("/home/sapp/sapp-firebase-notifications-firebase-adminsdk-bcjvu-cdca8ff155.json")
        sapp_app = firebase_admin.initialize_app(creds)

        #Here in the bottom of the run the actual api is run with flaskapp.
        self.flaskApp.run(host="0.0.0.0")



if __name__ == "__main__":
    flask_Main().run()