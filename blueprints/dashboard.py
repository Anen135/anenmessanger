from flask import Blueprint, render_template
from flask_login import current_user, login_required

dashboard_bp = Blueprint('dashboard', __name__)

# Убедимся, что только авторизованный пользователь может получить доступ к данному маршруту
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    friends = current_user.friends.all() # Получаем всех друзей пользователя
    chats = friends # Получаем все чаты, включая друзей
    groups = current_user.groups.all() # Получаем все группы, к которым принадлежит пользователь

    return render_template('dashboard.html', user=current_user, chats=chats, groups=groups)


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
def index():
    return render_template('index.html')

@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)