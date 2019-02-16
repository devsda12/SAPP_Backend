from flask import Flask

#Defining the flask app
app = Flask(__name__)

@app.route("/testshake")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    app.run()