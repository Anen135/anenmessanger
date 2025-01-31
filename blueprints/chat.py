from flask import Blueprint, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from models import db, User, Message, Friendship
from flask_login import current_user

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


# Обработчик WebSocket для получения истории чата
@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    if 'chat_id' not in data:
        return
    friend_id = data['chat_id']

    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        emit('chat_history', {"error": "Пользователь не авторизован"})
        return

    # Проверяем, являются ли два пользователя друзьями
    friend = User.query.get(friend_id)
    
    if not friend or not is_friend_with(current_user, friend):
        emit('chat_history', {"error": "Нет доступа к чату с этим пользователем"})
        return

    # Получаем все сообщения между текущим пользователем и выбранным другом
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == friend.id)) |
        ((Message.sender_id == friend.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    # Форматируем сообщения для отправки на клиент
    chat_history = [
        {
            "sender_username": User.query.get(message.sender_id).username,  # Получаем имя отправителя по sender_id
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Преобразуем datetime в строку
        }
        for message in messages
    ]
    
    emit('chat_history', chat_history)


# Обработчик WebSocket для отправки сообщений
@socketio.on('send_message')
def handle_send_message(data):
    # Получаем receiver_id и message_content из данных
    receiver_id = data.get('receiver_id')
    message_content = data.get('message_content')
    
    # Проверка, авторизован ли пользователь
    if not current_user.is_authenticated:
        emit('new_message', {"error": "Пользователь не авторизован"})
        return
    
    # Проверка на наличие receiver_id и message_content
    if not receiver_id or not message_content:
        emit('new_message', {"error": "Не указаны получатель или сообщение"})
        return

    # Получаем получателя сообщения
    receiver = User.query.get(receiver_id)
    if not receiver:
        emit('new_message', {"error": "Получатель не найден"})
        return

    # Проверяем, что текущий пользователь является другом получателя
    if not is_friend_with(current_user, receiver):
        emit('new_message', {"error": "Вы не можете отправить сообщение этому пользователю"})
        return

    # Сохраняем новое сообщение в базе данных
    new_message = Message(content=message_content, sender_id=current_user.id, receiver_id=receiver.id)
    db.session.add(new_message)
    db.session.commit()
    
    # Отправляем новое сообщение всем участникам чата
    emit('new_message', {
        "sender_username": current_user.username,
        "content": message_content,
        "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })


# Добавляем метод к классу User
def is_friend_with(user, friend):
    """Проверка, является ли два пользователя друзьями."""
    if not user.is_authenticated:
        return False
    return friend in user.friends.all()

User.is_friend_with = is_friend_with
