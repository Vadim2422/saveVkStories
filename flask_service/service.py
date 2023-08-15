from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def index():
    return 'Ok'


def thread_flask():
    flask_thread = Thread(target=run_flask)
    flask_thread.start()


def run_flask():
    app.run(host='localhost', port=80)

