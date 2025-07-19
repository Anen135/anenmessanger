from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from models import db, Group, GroupMembership, User, Friendship, GroupJoinRequest
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

    # Получаем всех пользователей, которые не являются участниками этой группы и в друзях текущего пользователя
    try: 
        users_to_add = db.session.query(User).join(Friendship, 
    (Friendship.user1_id == current_user.id) | (Friendship.user2_id == current_user.id)
).filter(
    User.id != current_user.id  # Исключаем самого себя
).filter(
    # Пользователь должен быть другом current_user
    ((Friendship.user1_id == current_user.id) & (User.id == Friendship.user2_id)) |
    ((Friendship.user2_id == current_user.id) & (User.id == Friendship.user1_id))
).filter(
    ~User.groups.any(Group.id == group_id)  # Пользователь не должен быть в группе с group_id
).all()
    except Exception as e: return jsonify({'success': False, 'message': f'Произошла ошибка при получении списка пользователей! {e}'})
    
    return jsonify({ 'success': True, 'users': [{'id': user.id, 'username': user.username} for user in users_to_add] })

@group_bp.route('/get_users_in_group', methods=['GET'])
@login_required
def get_users_in_group():
    group_id = request.args.get('group_id')
    group = Group.query.get(group_id)
    
    if not group or group.creator_id != current_user.id: return jsonify({'success': False, 'message': 'Вы не являетесь создателем этой группы'})

    # Получаем всех пользователей, которые являются участниками этой группы
    try:
        users_in_group = db.session.query(User).join(GroupMembership, GroupMembership.user_id == User.id).filter(GroupMembership.group_id == group_id).all()
    except Exception as e: return jsonify({'success': False, 'message': f'Произошла ошибка при получении списка пользователей! {e}'})

    return jsonify({ 'success': True, 'users': [{'id': user.id, 'username': user.username} for user in users_in_group] })

# Обработчик для удаления пользователей из группы
@group_bp.route('/remove_users_from_group', methods=['POST'])
@login_required
def remove_users_from_group():
    data = request.get_json()  # Получаем данные как JSON
    group_id = data.get('group_id')
    user_ids = data.get('users')  # Список ID пользователей, которых нужно удалить

    # Проверка: указано ли ID группы
    if not group_id:
        return jsonify({"success": False, "error": "Group ID is required"})

    # Получаем группу по ID
    group = Group.query.get(group_id)
    
    if not group:
        return jsonify({"success": False, "error": "Group not found"})

    # Проверяем, является ли текущий пользователь создателем группы
    if group.creator_id != current_user.id:
        return jsonify({"success": False, "error": "Only the creator can remove users"})

    # Удаляем каждого пользователя
    removed_users = []
    for user_id in user_ids:
        membership = GroupMembership.query.filter_by(group_id=group.id, user_id=user_id).first()
        if membership:
            db.session.delete(membership)
            removed_users.append(user_id)
    try:
        db.session.commit()
        msg = f'Пользователи были удалены из группы {group.name}'
        if current_user.id in user_ids: 
            handle_delete_group(group)
            return jsonify({
                "success": True,
                "message": "Ваша группа была удалена. Все пользователи были удалены из группы.",
                "removed_users": removed_users
            })
        return jsonify({
            "success": True,
            "message": msg,
            "removed_users": removed_users
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Error removing users",
            "details": str(e)
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
        
@socketio.on('leave_group')
@login_required
def handle_leave_group(data):
    group_id = data.get('group_id')

    # Проверка: авторизован ли пользователь
    if not current_user.is_authenticated:
        emit('leave_group_response', {"error": "User is not authenticated"})
        return

    # Проверка: указано ли ID группы
    if not group_id:
        emit('leave_group_response', {"error": "Group ID is required and cannot be empty"})
        return

    try:
        # Ищем группу по ID
        group = Group.query.get(group_id)

        if not group:
            emit('leave_group_response', {"error": "Group not found"})
            return

        # Проверяем, является ли текущий пользователь создателем группы
        if group.creator_id == current_user.id:
            emit('leave_group_response', {"error": "You cannot leave your own group"})
            return

        # Ищем участника группы
        membership = GroupMembership.query.filter_by(group_id=group.id, user_id=current_user.id).first()

        if not membership:
            emit('leave_group_response', {"error": "You are not a member of this group"})
            return

        # Удаляем участника из группы
        db.session.delete(membership)
        db.session.commit()

        # Отправляем успешный ответ
        emit('leave_group_response', {"success": True, "message": "Вы успешно покинули группу"})
    except Exception as e:
        db.session.rollback()
        emit('leave_group_response', {"error": "An error occurred while leaving the group", "details": e})

def handle_delete_group(group):
    try:
        if not group:
            return "Group not found"

        # Проверяем, является ли текущий пользователь создателем группы
        if group.creator_id != current_user.id:
            return "Only the creator can remove groups"

        # Удаляем группу
        db.session.delete(group)
        db.session.commit()

        # Отправляем успешный ответ
        return True
    except Exception as e:
        db.session.rollback()
        return False, e