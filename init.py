from flask import Flask
from flask_socketio import SocketIO
from os import path as os, makedirs as osmakedirs


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация папки загрузки аватарок
    upload_folder = os.join(app.root_path, 'static', 'uploads')
    osmakedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    return app

# Для WebSocket подключаем SocketIO
socketio = SocketIO(async_mode = 'eventlet')