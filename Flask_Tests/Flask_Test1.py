from flask import Flask

#Defining the flask app
app = Flask(__name__)

@app.route("/testshake")
def testshake():
    return "Testshake Succesfull"

if __name__ == "__main__":
    app.run(host="0.0.0.0")