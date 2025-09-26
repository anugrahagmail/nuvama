from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    host = request.host
    if host == "app.theriskdiary.com":
        return "Hello from APP subdomain"
    else:
        return "This is the main site content"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

