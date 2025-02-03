from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit
from models import db, User, Message, Friendship, Group
from flask_login import current_user
from init import socketio

# Создаем Blueprint для чата
chat_bp = Blueprint('chat', __name__)


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
            "avatar": message.sender.avatar_url,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Преобразуем datetime в строку
        }
        for message in messages
    ]
    
    # Возвращаем историю чата в формате JSON
    return jsonify({"chat_history": chat_history})

# Обработчик WebSocket для получения истории чата
@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    if 'chat_id' not in data or 'chat_type' not in data:
        return
    
    chat_id = data['chat_id']
    chat_type = data['chat_type']  # personal или group

    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        emit('chat_history', {"error": "Пользователь не авторизован"})
        return

    # Если это личный чат
    if chat_type == 'personal':
        friend = User.query.get(chat_id)
        if not friend or not is_friend_with(current_user, friend):
            emit('chat_history', {"error": "Нет доступа к чату с этим пользователем"})
            return

        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == friend.id)) |
            ((Message.sender_id == friend.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.asc()).all()

    # Если это групповой чат
    elif chat_type == 'group':
        group = Group.query.get(chat_id)
        if not group or current_user not in group.members:
            emit('chat_history', {"error": "Нет доступа к этой группе"})
            return

        messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp.asc()).all()

    # Формируем историю сообщений для ответа
    chat_history = [
        {
            "sender_username": User.query.get(message.sender_id).username,
            "sender_avatar": User.query.get(message.sender_id).avatar_url,
            "sender_about": User.query.get(message.sender_id).about,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for message in messages
    ]
    
    emit('chat_history', {"messages": chat_history})

# Обработчик WebSocket для отправки сообщений
def handle_message_creation(receiver_id, message_content, chat_type):
    if chat_type == 'personal':
        receiver = User.query.get(receiver_id)
        if not receiver or not is_friend_with(current_user, receiver):
            return False, "Вы не можете отправить сообщение этому пользователю"

        new_message = Message(content=message_content, sender_id=current_user.id, receiver_id=receiver.id)
    elif chat_type == 'group':
        group = Group.query.get(receiver_id)
        if not group or current_user not in group.members:
            return False, "Вы не можете отправить сообщение в эту группу"

        new_message = Message(content=message_content, sender_id=current_user.id, group_id=group.id)
    else:
        return False, "Неверный тип чата"

    db.session.add(new_message)
    db.session.commit()

    emit('new_message', {
        "sender_username": current_user.username,
        "sender_avatar": User.query.get(new_message.sender_id).avatar_url,
        "sender_about": User.query.get(new_message.sender_id).about,
        "content": message_content,
        "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })
    return True, None

# Обработчик WebSocket для отправки сообщений
@socketio.on('send_message')
def handle_send_message(data):
    if not current_user.is_authenticated:
        emit('new_message', {"error": "Пользователь не авторизован"})
        return

    receiver_id = data.get('receiver_id')
    message_content = data.get('message_content')
    chat_type = data.get('chat_type')  # Тип чата: 'personal' или 'group'

    if not receiver_id or not message_content:
        emit('new_message', {"error": "Не указаны получатель или сообщение"})
        return

    success, error_message = handle_message_creation(receiver_id, message_content, chat_type)

    if not success:
        emit('new_message', {"error": error_message})

# Добавляем метод к классу User
def is_friend_with(user, friend):
    """Проверка, является ли два пользователя друзьями."""
    if not user.is_authenticated:
        return False
    return friend in user.friends.all()

User.is_friend_with = is_friend_with
