from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from models import db, Group, GroupMembership, User
from flask_socketio import emit
from init import socketio

dashboard_bp = Blueprint('dashboard', __name__)

# Убедитесь, что только авторизованный пользователь может получить доступ к данному маршруту
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Получаем всех друзей пользователя
    friends = current_user.friends.all()

    # Получаем все чаты, включая друзей
    chats = friends

    # Получаем все группы, к которым принадлежит пользователь
    groups = current_user.groups.all()

    return render_template('dashboard.html', user=current_user, chats=chats, groups=groups)


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
def index():
    return render_template('index.html')

