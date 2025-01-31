from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from init import create_app
from models import db, User
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.friend_request import friend_requests_bp
from blueprints.chat import chat_bp, socketio
from blueprints.group_request import group_requests_bp
from blueprints.group import group_bp, socketio as group_socketio

# Создаем экземпляр приложения
app = create_app()

# Инициализация базы данных
db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
socketio.init_app(app)
group_socketio.init_app(app)

# Загрузка пользователя по его ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Указываем маршрут для перенаправления пользователя, если он не авторизован
login_manager.login_view = 'auth.login'  # Путь к маршруту авторизации

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(friend_requests_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(group_requests_bp)
app.register_blueprint(group_bp)

# Основной запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Запускаем сервер с WebSocket через SocketIO
        socketio.run(app, debug=True)
    