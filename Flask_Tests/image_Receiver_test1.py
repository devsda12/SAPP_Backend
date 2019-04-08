from flask import Flask
from flask import request

#Defining the flask app
app = Flask(__name__)

@app.route("/imageUpload", methods=["POST"])
def imageUpload():
    if "image" not in request.files:
        print("No file present")
        return "Upload unsuccessful"

    print(request.form.get("otherParam"))

    image = request.files["image"]
    print(image.read())
    print(type(image.read()))
    image.save("/home/jasper/Documents/uploaded_image.png")

    return "Upload successful"

if __name__ == "__main__":
    app.run(host="0.0.0.0")