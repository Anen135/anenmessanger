from flask_login import LoginManager
from init import create_app, socketio
from models import db, User
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.friend_request import friend_requests_bp
from blueprints.chat import chat_bp
from blueprints.group import group_bp
from blueprints.group_request import group_requests_bp
from blueprints.profile import upload_bp
from flask_migrate import Migrate

# Қосымшаның данасын жасаңыз
login_manager = LoginManager()
app = create_app()

# Flask Инициализациясы
db.init_app(app)
login_manager.init_app(app)
socketio.init_app(app)
migrate = Migrate(app, db)

# Пайдаланушыны оның идентификаторы бойынша жүктеу
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Егер ол рұқсат етілмеген болса, пайдаланушыны қайта бағыттау үшін маршрутты көрсетіңіз
login_manager.login_view = 'auth.login'  # Авторизация маршрутына жол

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(friend_requests_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(group_bp)
app.register_blueprint(group_requests_bp)
app.register_blueprint(upload_bp)

# Қолданбаның негізгі іске қосылуы
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Socketio арқылы WebSocket көмегімен серверді іске қосыңыз
        socketio.run(app, debug=True)
    