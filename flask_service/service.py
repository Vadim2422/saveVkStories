from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def index():
    return 'Ok'


def start_thread_flask():
    flask_thread = Thread(target=run_flask)
    flask_thread.start()


def run_flask():
    app.run(host='0.0.0.0', port=8080)
