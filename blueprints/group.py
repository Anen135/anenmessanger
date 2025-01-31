from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from models import db, Group, GroupMembership, User
from flask_socketio import emit
from init import socketio

# Создаем Blueprint для групп
group_bp = Blueprint('group', __name__)

# API для создания группы

@group_bp.route('/get_groups', methods=['GET'])
def get_groups():
    # Получаем все группы, к которым принадлежит текущий пользователь
    groups = current_user.groups.all()
    return jsonify([{"id": group.id, "name": group.name} for group in groups])

@group_bp.route('/get_users_for_group', methods=['GET'])
@login_required
def get_users_for_group():
    group_id = request.args.get('group_id')
    group = Group.query.get(group_id)

    if not group or group.creator_id != current_user.id: return jsonify({'success': False, 'message': 'Вы не являетесь создателем этой группы'})

    # Получаем всех пользователей, которые не являются участниками этой группы
    try: users_to_add = User.query.filter(User.id != current_user.id).all()
    except Exception as e: return jsonify({'success': False, 'message': f'Произошла ошибка при получении списка пользователей! {e}'})
    
    return jsonify({ 'success': True, 'users': [{'id': user.id, 'username': user.username} for user in users_to_add] })

@group_bp.route('/add_users_to_group', methods=['POST'])
@login_required
def add_users_to_group():
    group_id = request.form.get('group_id')
    user_ids = request.form.getlist('users[]')  # Список пользователей, которых нужно добавить

    # Получаем группу по ID
    group = Group.query.get(group_id)

    if not group:
        return jsonify({"success": False, "message": "Группа не найдена"})

    # Проверяем, является ли текущий пользователь создателем группы
    if group.creator_id != current_user.id:
        return jsonify({"success": False, "message": "Только создатель группы может добавлять участников"})

    # Проверяем каждого пользователя, которого мы добавляем в группу
    added_users = []
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user and user_id != current_user.id:  # Не добавляем самого себя
            # Проверяем, не является ли пользователь уже участником группы
            existing_membership = GroupMembership.query.filter_by(group_id=group.id, user_id=user.id).first()
            if not existing_membership:
                # Добавляем пользователя в группу
                new_membership = GroupMembership(group_id=group.id, user_id=user.id)
                db.session.add(new_membership)
                added_users.append(user.username)

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Пользователи успешно добавлены в группу",
            "added_users": added_users
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Ошибка при добавлении пользователей: {str(e)}"
        })

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