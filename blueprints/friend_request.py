from flask import Blueprint, request, jsonify
from models import db, User, FriendRequest, Friendship

friend_requests_bp = Blueprint('friend_requests', __name__)

# Отправка запроса на дружбу
@friend_requests_bp.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    username = request.cookies.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})

    friend_username = request.form['friend_username']
    friend = User.query.filter_by(username=friend_username).first()
    
    if not friend:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})

    # Проверка, что пользователь не пытается добавить себя в друзья
    if user.id == friend.id:
        return jsonify({'success': False, 'message': 'Нельзя добавить самого себя в друзья'})

    # Проверка, что уже есть друзья
    if friend in user.friends:
        return jsonify({'success': False, 'message': 'Вы уже в друзьях с этим пользователем'})

    # Проверка, что запрос уже был отправлен
    existing_request = FriendRequest.query.filter_by(sender_id=user.id, receiver_id=friend.id).first()
    if existing_request:
        return jsonify({'success': False, 'message': 'Запрос уже отправлен'})

    new_request = FriendRequest(sender_id=user.id, receiver_id=friend.id)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'success': True})

# Получение запросов на дружбу
@friend_requests_bp.route('/get_friend_requests', methods=['GET'])
def get_friend_requests():
    username = request.cookies.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})

    # Получаем входящие запросы
    incoming_requests = FriendRequest.query.filter_by(receiver_id=user.id).all()
    outgoing_requests = FriendRequest.query.filter_by(sender_id=user.id).all()

    # Формируем список запросов для отображения в интерфейсе
    incoming_requests_list = [{'id': r.id, 'sender_username': User.query.get(r.sender_id).username} for r in incoming_requests]
    outgoing_requests_list = [{'id': r.id, 'receiver_username': User.query.get(r.receiver_id).username} for r in outgoing_requests]

    return jsonify({
        'success': True,
        'incoming_requests': incoming_requests_list,
        'outgoing_requests': outgoing_requests_list
    })

# Ответ на запрос дружбы (принять/отклонить)
@friend_requests_bp.route('/respond_friend_request/<int:request_id>/<action>', methods=['GET'])
def respond_friend_request(request_id, action):
    # Находим запрос по ID
    friend_request = FriendRequest.query.get(request_id)
    if not friend_request:
        return jsonify({'success': False, 'message': 'Запрос не найден!'})

    if action not in ['accept', 'decline']:
        return jsonify({'success': False, 'message': 'Неверное действие!'})

    if action == 'accept':
        # Проверка, что пользователи не являются друзьями
        user1 = friend_request.sender
        user2 = friend_request.receiver

        if user2 in user1.friends:
            return jsonify({'success': False, 'message': 'Вы уже в друзьях с этим пользователем'})

        # Добавляем в таблицу Friendship (связь многие ко многим)
        friendship1 = Friendship(user1_id=user1.id, user2_id=user2.id)
        friendship2 = Friendship(user1_id=user2.id, user2_id=user1.id)  # Дублируем для обратной связи

        db.session.add(friendship1)
        db.session.add(friendship2)

        # Удаляем запрос на дружбу
        db.session.delete(friend_request)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Запрос на дружбу принят!'})

    elif action == 'decline':
        # Просто удаляем запрос
        db.session.delete(friend_request)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Запрос на дружбу отклонен.'})
