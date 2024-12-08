from flask import Flask

app = Flask(__name__)
app.secret_key = "default_secret_key"
