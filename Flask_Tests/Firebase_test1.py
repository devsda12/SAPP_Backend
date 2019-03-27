import firebase_admin
from firebase_admin import credentials

creds = credentials.Certificate("D:\Downloads\sapp-firebase-notifications-firebase-adminsdk-bcjvu-cdca8ff155.json")
app = firebase_admin.initialize_app(creds)
print(app.name)