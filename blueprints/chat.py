from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit, join_room
from models import db, User, Message, Friendship, Group
from flask_login import current_user
from init import socketio
from html import escape
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from flask import current_app

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt', 'mp4', 'zip'}

# Сөйлесу үшін Blueprint 
chat_bp = Blueprint('chat', __name__)
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(current_user.id)
        print(f"User {current_user.username} joined room {current_user.id}")
    else:
        print("User not authenticated")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@chat_bp.route('/upload', methods=['POST'])
def upload_file():
    # Определяем папку для загрузки относительно static
    upload_folder = os.path.join('static', 'uploads')
    full_upload_path = os.path.join(current_app.root_path, upload_folder)
    
    # Создаем папку, если она не существует
    os.makedirs(full_upload_path, exist_ok=True)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        # Создаем безопасное имя файла
        filename = secure_filename(file.filename)
        
        # Генерируем уникальное имя файла
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{unique_id}_{filename}"
        
        # Полный путь для сохранения
        save_path = os.path.join(full_upload_path, unique_filename)
        
        # Сохраняем файл
        file.save(save_path)
        
        # Путь для хранения в БД (относительно static)
        db_file_path = os.path.join('uploads', unique_filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'file_path': db_file_path,  # 'uploads/filename.ext'
            'file_type': file.mimetype,
            'file_size': os.path.getsize(save_path)
        })
        
    except Exception as e:
        current_app.logger.error(f"File upload error: {str(e)}")
        return jsonify({
            'error': 'File upload failed',
            'message': str(e)
        }), 500

# Чат бетіне арналған Маршрут
@chat_bp.route('/chat')
def chat():
    return render_template('dashboard.html')  # Чат беті

# Пайдаланушының дос екенін тексеру
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
    chat_history = []
    for message in messages:
        message_data = {
            "sender_username": message.sender.username,
            "sender_avatar": message.sender.avatar_url,
            "sender_about": message.sender.about,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "id": message.id
        }

        # Добавляем информацию в зависимости от типа сообщения
        if message.content:
            # Текстовое сообщение
            message_data["content"] = message.content
            message_data["is_file"] = False
        elif message.file_path:
            # Файловое сообщение
            message_data.update({
                "is_file": True,
                "file_name": message.file_name,
                "file_path": message.file_path,
                "file_type": message.file_type,
                "file_size": message.file_size
            })

        chat_history.append(message_data)
    
    emit('chat_history', {"messages": chat_history})

@socketio.on('delete_message')
def handle_delete_message(data):
    message_id = data['message_id']
    chat_type = data['chat_type']
    message = Message.query.get(message_id)
    if not message or message.sender_id != current_user.id:
        return False
    db.session.delete(message)
    db.session.commit()
    if chat_type == 'personal':
        emit('message_deleted', {"message_id": message_id}, room=message.receiver_id)
        emit('message_deleted', {"message_id": message_id}, room=message.sender_id)
    elif chat_type == 'group':
        group = Group.query.get(message.group_id)
        if group:
            for member in group.members:
                emit('message_deleted', {"message_id": message_id}, room=member.id)
    return True

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

    # Подготовка сообщения для отправки всем участникам чата (включая отправителя)
    message_data = {
        "chat_id": receiver_id,
        "chat_type": chat_type,
        "sender_username": current_user.username,
        "sender_avatar": current_user.avatar_url,
        "sender_about": current_user.about,
        "content": message_content,
        "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Если это личный чат, отправляем сообщение обоим участникам (отправителю и получателю)
    if chat_type == 'personal':
        emit('new_message', message_data, room=receiver_id)
        message_data["self_send"] = True
        emit('new_message', message_data, room=current_user.id)

    # Если это групповой чат, отправляем сообщение всем участникам группы
    elif chat_type == 'group':
        group = Group.query.get(receiver_id)
        if group:
            for member in group.members:
                emit('new_message', message_data, room=member.id)
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
    usejs = data.get('usejs')
    
    if not usejs:
        message_content = escape(message_content)

    if not receiver_id or not message_content:
        emit('new_message', {"error": "Не указаны получатель или сообщение"})
        return

    success, error_message = handle_message_creation(receiver_id, message_content, chat_type)

    if not success:
        emit('new_message', {"error": error_message})

# Добавляем новый обработчик для файлов
def handle_file_message_creation(receiver_id, file_data, chat_type):
    if chat_type == 'personal':
        receiver = User.query.get(receiver_id)
        if not receiver or not is_friend_with(current_user, receiver):
            return False, "Вы не можете отправить файл этому пользователю"

        new_message = Message(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            file_name=file_data['filename'],
            file_path=file_data['file_path'],
            file_type=file_data['file_type'],
            file_size=file_data['file_size']
        )
    elif chat_type == 'group':
        group = Group.query.get(receiver_id)
        if not group or current_user not in group.members:
            return False, "Вы не можете отправить файл в эту группу"

        new_message = Message(
            sender_id=current_user.id,
            group_id=group.id,
            file_name=file_data['filename'],
            file_path=file_data['file_path'],
            file_type=file_data['file_type'],
            file_size=file_data['file_size']
        )
    else:
        return False, "Неверный тип чата"

    db.session.add(new_message)
    db.session.commit()

    # Подготовка сообщения для отправки
    message_data = {
        "chat_id": receiver_id,
        "chat_type": chat_type,
        "sender_username": current_user.username,
        "sender_avatar": current_user.avatar_url,
        "sender_about": current_user.about,
        "file_name": file_data['filename'],
        "file_path": file_data['file_path'],
        "file_type": file_data['file_type'],
        "file_size": file_data['file_size'],
        "timestamp": new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "is_file": True  # Флаг, что это файловое сообщение
    }

    # Отправка файлового сообщения
    if chat_type == 'personal':
        emit('new_message', message_data, room=receiver_id)
        message_data["self_send"] = True
        emit('new_message', message_data, room=current_user.id)
    elif chat_type == 'group':
        group = Group.query.get(receiver_id)
        if group:
            for member in group.members:
                emit('new_message', message_data, room=member.id)
    
    return True, None


# Обработчик WebSocket для отправки файлов
@socketio.on('send_file')
def handle_send_file(data):
    if not current_user.is_authenticated:
        emit('new_message', {"error": "Пользователь не авторизован"})
        return

    receiver_id = data.get('receiver_id')
    file_data = data.get('file_data')
    chat_type = data.get('chat_type')

    if not receiver_id or not file_data:
        emit('new_message', {"error": "Не указаны получатель или файл"})
        return

    success, error_message = handle_file_message_creation(receiver_id, file_data, chat_type)

    if not success:
        emit('new_message', {"error": error_message})

@socketio.on('remove_friend')
def handle_remove_friend(data):
    friend_id = data.get('friend_id')
    if not friend_id:
        emit('remove_friend_response', {"error": "Friend ID is required"})
        return

    friend = User.query.get(friend_id)
    if not friend:
        emit('remove_friend_response', {"error": "Friend not found"})
        return

    if not is_friend_with(current_user, friend):
        emit('remove_friend_response', {"error": "You are not friends with this user"})
        return

    # Удаляем все возможные записи о дружбе в обоих направлениях
    friendships = Friendship.query.filter(
        ((Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id)) |
        ((Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id))
    ).all()

    if not friendships:
        emit('remove_friend_response', {"error": "Friendship not found"})
        return

    try:
        # Удаляем записи о дружбе
        for friendship in friendships:
            db.session.delete(friendship)

        db.session.commit()  # Явное завершение транзакции
        emit('remove_friend_response', {"success": True})

    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        emit('remove_friend_response', {"error": f"Error removing friend: {str(e)}"})

# Добавляем метод к классу User
def is_friend_with(user, friend):
    """Проверка, является ли два пользователя друзьями."""
    if not user.is_authenticated:
        return False
    return friend in user.friends.all()

User.is_friend_with = is_friend_with
