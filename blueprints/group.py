from flask import Blueprint, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from models import db, User, Message, Group, GroupMembership
from flask_login import current_user, login_required

# Создаем Blueprint для групп
group_bp = Blueprint('group', __name__)

# Для WebSocket подключаем SocketIO
socketio = SocketIO()

# Маршрут для создания группы
@group_bp.route('/create_group', methods=['POST'])
@login_required
def create_group():
    data = request.get_json()
    group_name = data.get('group_name')

    if not group_name:
        return jsonify({'success': False, 'message': 'Название группы не указано'})

    # Проверка на существование группы с таким именем
    existing_group = Group.query.filter_by(name=group_name).first()
    if existing_group:
        return jsonify({'success': False, 'message': 'Группа с таким названием уже существует'})

    # Создаем новую группу
    new_group = Group(name=group_name, creator_id=current_user.id)
    db.session.add(new_group)
    db.session.commit()

    # Добавляем создателя в группу как участника
    membership = GroupMembership(group_id=new_group.id, user_id=current_user.id)
    db.session.add(membership)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Группа успешно создана!', 'group_id': new_group.id})

# Обработчик WebSocket для добавления пользователей в группу
@socketio.on('add_to_group')
def handle_add_to_group(data):
    group_id = data.get('group_id')
    user_id = data.get('user_id')

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group or not user:
        emit('add_to_group_error', {"error": "Группа или пользователь не найдены"})
        return

    # Проверяем, является ли текущий пользователь создателем группы
    if group.creator_id != current_user.id:
        emit('add_to_group_error', {"error": "Вы не являетесь создателем группы"})
        return

    # Добавляем пользователя в группу
    membership = GroupMembership(group_id=group.id, user_id=user.id)
    db.session.add(membership)
    db.session.commit()

    emit('user_added_to_group', {"group_id": group.id, "user_id": user.id, "username": user.username})

# Обработчик WebSocket для отправки сообщений в группу
@socketio.on('send_group_message')
def handle_send_group_message(data):
    group_id = data.get('group_id')
    message_content = data.get('message_content')

    group = Group.query.get(group_id)
    if not group:
        emit('send_group_message_error', {"error": "Группа не найдена"})
        return

    # Проверяем, состоит ли пользователь в группе
    if not any(member.id == current_user.id for member in group.members):
        emit('send_group_message_error', {"error": "Вы не состоите в этой группе"})
        return

    # Сохраняем сообщение в базе данных
    new_message = Message(content=message_content, sender_id=current_user.id, group_id=group.id)
    db.session.add(new_message)
    db.session.commit()

    emit('new_group_message', {
        "group_id": group.id,
        "sender_username": current_user.username,
        "content": message_content,
        "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }, room=f"group_{group.id}")

# Обработчик WebSocket для получения истории сообщений группы
@socketio.on('get_group_chat_history')
def handle_get_group_chat_history(data):
    group_id = data.get('group_id')

    group = Group.query.get(group_id)
    if not group:
        emit('group_chat_history_error', {"error": "Группа не найдена"})
        return

    # Проверяем, состоит ли пользователь в группе
    if not any(member.id == current_user.id for member in group.members):
        emit('group_chat_history_error', {"error": "Вы не состоите в этой группе"})
        return

    # Получаем сообщения группы
    messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp.asc()).all()
    chat_history = [
        {
            "sender_username": message.sender.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for message in messages
    ]

    emit('group_chat_history', {"group_id": group.id, "messages": chat_history})

