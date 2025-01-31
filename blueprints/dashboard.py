from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import User

dashboard_bp = Blueprint('dashboard', __name__)

# Убедитесь, что только авторизованный пользователь может получить доступ к данному маршруту
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Получаем всех друзей пользователя
    friends = current_user.friends.all()

    # Получаем все группы, в которых состоит пользователь
    groups = current_user.groups

    # Формируем общий список чатов: друзей и групп
    chats = \
    [ {"id": friend.id, "name": friend.username, "type": "friend"} for friend in friends ] + \
    [ {"id": group.id, "name": group.name, "type": "group"} for group in groups ]

    return render_template('dashboard.html', user=current_user, chats=chats)


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
def index():
    return render_template('index.html')
