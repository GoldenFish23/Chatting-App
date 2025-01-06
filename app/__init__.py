from flask import Flask
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = "qwerty"
socketio = SocketIO(app)

if __name__ == '__init__':
    socketio.run(app, debug=True)

from app import routes
