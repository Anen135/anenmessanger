from flask import Blueprint, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from models import db, User, Message, Group
from flask_login import current_user, login_required

# Создаем Blueprint для чата
chat_bp = Blueprint('chat', __name__)

# Для WebSocket подключаем SocketIO
socketio = SocketIO()

# Маршрут для страницы чата
@chat_bp.route('/chat')
def chat():
    return render_template('dashboard.html')  # Страница чата

# Проверка, является ли пользователь другом
def is_friend_with(user, friend):
    """Проверка, является ли два пользователя друзьями."""
    if not user.is_authenticated:
        return False
    return friend in user.friends.all()

@chat_bp.route('/get_chat_history/<int:friend_id>', methods=['GET'])
def handle_get_chat_history(friend_id):
    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        return jsonify({"error": "Пользователь не авторизован"}), 401
    
    # Получаем друга из базы данных
    friend = User.query.get(friend_id)
    
    # Проверяем, что друг существует и что текущий пользователь является другом
    if not friend or not is_friend_with(current_user, friend):
        return jsonify({"error": "Дружбы не существует"}), 403

    # Получаем историю чата между текущим пользователем и другом
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == friend.id)) |
        ((Message.sender_id == friend.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    # Формируем историю сообщений для ответа
    chat_history = [
        {
            "sender": message.sender.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Преобразуем datetime в строку
        }
        for message in messages
    ]
    
    # Возвращаем историю чата в формате JSON
    return jsonify({"chat_history": chat_history})


@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    chat_id = data.get('chat_id')
    chat_type = data.get('chat_type')  # friend или group

    if chat_type == "friend":
        # Получаем историю сообщений между двумя пользователями
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == chat_id)) |
            ((Message.sender_id == chat_id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.asc()).all()
    elif chat_type == "group":
        # Получаем историю сообщений группы
        messages = Message.query.filter_by(group_id=chat_id).order_by(Message.timestamp.asc()).all()
    else:
        emit('chat_history_error', {"error": "Некорректный тип чата"})
        return

    # Формируем историю чата
    chat_history = [
        {
            "sender_username": message.sender.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for message in messages
    ]

    emit('chat_history', {"chat_id": chat_id, "messages": chat_history})


# Обработчик WebSocket для отправки сообщений
@socketio.on('send_message')
@login_required
def handle_send_message(data):
    chat_id = data.get('chat_id')
    chat_type = data.get('chat_type')  # friend или group
    message_content = data.get('message_content')

    if chat_type == "friend":
        # Отправка личного сообщения
        receiver = User.query.get(chat_id)
        if not receiver:
            emit('send_message_error', {"error": "Получатель не найден"})
            return

        new_message = Message(content=message_content, sender_id=current_user.id, receiver_id=receiver.id)
        db.session.add(new_message)
        db.session.commit()

        emit('new_message', {
            "sender_username": current_user.username,
            "content": message_content,
            "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }, room=f"user_{receiver.id}")

    elif chat_type == "group":
        # Отправка сообщения в группу
        group = Group.query.get(chat_id)
        if not group:
            emit('send_message_error', {"error": "Группа не найдена"})
            return

        if not any(member.id == current_user.id for member in group.members):
            emit('send_message_error', {"error": "Вы не состоите в этой группе"})
            return

        new_message = Message(content=message_content, sender_id=current_user.id, group_id=group.id)
        db.session.add(new_message)
        db.session.commit()

        emit('new_message', {
            "sender_username": current_user.username,
            "content": message_content,
            "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }, room=f"group_{group.id}")

    else:
        emit('send_message_error', {"error": "Некорректный тип чата"})


User.is_friend_with = is_friend_with
