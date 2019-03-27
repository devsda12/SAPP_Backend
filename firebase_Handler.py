import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

class firebase_Handler:

    def __init__(self):
        #Declaring the global firebase variables
        self.creds = credentials.Certificate("/home/back-end/sapp-firebase-notifications-firebase-adminsdk-bcjvu-cdca8ff155.json")
        self.sapp_app = firebase_admin.initialize_app(self.creds)


    #Function to send an "notification" to the firebase api which in turn sends it through to the given device registration ID
    def sendRefreshRequest(self, registrationId, conv_Id):
        #First making the message
        tempMessage = messaging.Message(
            data={
                "conv_Id":conv_Id
            },
            token=registrationId
        )

        #Now sending the message to the device with the corresponding ID
        response = messaging.send(tempMessage)
        print(response)