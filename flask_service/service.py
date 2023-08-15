from flask import Flask
from threading import Thread
app = Flask(__name__)


@app.route('/')
def index():
    return 'Ok'


def run_flask_in_thread():
    flask_thread = Thread(target=app.run)
    flask_thread.start()