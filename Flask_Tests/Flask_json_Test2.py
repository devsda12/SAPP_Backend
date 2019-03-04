from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/postjson", methods=['POST'])
def posthandler():
    content = request.get_json()
    print(content)
    return "Json posted"

app.run()