from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from models import db, Group, GroupMembership
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

    return render_template('dashboard.html', user=current_user, chats=chats)

@dashboard_bp.route('/')
@dashboard_bp.route('/index')
def index():
    return render_template('index.html')

# API для создания группы
@socketio.on('create_group')
@login_required
def handle_create_group(data):
    group_name = data.get('name')

    # Проверка: авторизован ли пользователь
    if not current_user.is_authenticated:
        emit('create_group_response', {"error": "User is not authenticated"})
        return

    # Проверка: указано ли имя группы
    if not group_name or not group_name.strip():
        emit('create_group_response', {"error": "Group name is required and cannot be empty"})
        return

    # Проверка на дублирование (если требуется уникальность имен групп)
    if Group.query.filter_by(name=group_name.strip()).first():
        emit('create_group_response', {"error": "A group with this name already exists"})
        return

    try:
        # Создаем группу и добавляем создателя как участника
        new_group = Group(name=group_name.strip(), creator_id=current_user.id)
        db.session.add(new_group)
        db.session.commit()

        membership = GroupMembership(group_id=new_group.id, user_id=current_user.id)
        db.session.add(membership)
        db.session.commit()

        # Отправляем успешный ответ
        emit('create_group_response', {
            "success": True,
            "message": "Группа успешно создана!",
            "group": {
                "id": new_group.id,
                "name": new_group.name,
                "creator_id": new_group.creator_id,
                "created_at": new_group.created_at.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        emit('create_group_response', {"error": "An error occurred while creating the group", "details": str(e)})
