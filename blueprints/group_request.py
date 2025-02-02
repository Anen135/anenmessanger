from flask import Blueprint, request, jsonify
from models import db, User, Group, GroupJoinRequest, GroupMembership

group_requests_bp = Blueprint('group_requests', __name__)

# Отправка запроса на присоединение к группе
@group_requests_bp.route('/send_group_join_request', methods=['POST'])
def send_group_join_request():
    username = request.cookies.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})

    group_id = request.form['group_id']
    group = Group.query.get(group_id)

    if not group:
        return jsonify({'success': False, 'message': 'Группа не найдена'})

    # Проверка, что запрос отправляет создатель группы
    if group.creator_id != user.id:
        return jsonify({'success': False, 'message': 'Только создатель группы может отправить запрос'})

    user_id = request.form['user_id']
    target_user = User.query.get(user_id)

    if not target_user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})

    # Проверка, что запрос уже существует
    existing_request = GroupJoinRequest.query.filter_by(group_id=group_id, user_id=user_id).first()
    if existing_request:
        return jsonify({'success': True, 'message': 'Запрос уже отправлен'})

    # Создаем новый запрос
    new_request = GroupJoinRequest(group_id=group_id, user_id=user_id)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Запрос отправлен'})

# Получение запросов на присоединение (как входящих, так и исходящих)
@group_requests_bp.route('/get_group_requests', methods=['GET'])
def get_group_requests():
    username = request.cookies.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})

    # Входящие запросы (запросы, которые пользователь должен одобрить/отклонить)
    incoming_requests = GroupJoinRequest.query.filter_by(user_id=user.id, status='pending').all()

    # Исходящие запросы (запросы, которые отправил пользователь)
    outgoing_requests = GroupJoinRequest.query.join(Group).filter(Group.creator_id == user.id).all()

    return jsonify({
        'success': True,
        'incoming_requests': [{'id': r.id, 'group_name': r.group.name, 'group_id': r.group_id} for r in incoming_requests],
        'outgoing_requests': [{'id': r.id, 'user_name': r.user.username, 'user_id': r.user_id} for r in outgoing_requests]
    })

# Ответ на запрос (принять/отклонить)
@group_requests_bp.route('/respond_group_request/<int:request_id>/<action>', methods=['POST'])
def respond_group_request(request_id, action):
    group_request = GroupJoinRequest.query.get(request_id)
    if not group_request:
        return jsonify({'success': False, 'message': 'Запрос не найден'})

    if action not in ['accept', 'decline']:
        return jsonify({'success': False, 'message': 'Неверное действие'})

    if action == 'accept':
        # Добавляем пользователя в группу
        new_membership = GroupMembership(group_id=group_request.group_id, user_id=group_request.user_id)
        db.session.add(new_membership)

    # Удаляем запрос
    db.session.delete(group_request)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Запрос {"принят" if action == "accept" else "отклонен"}'})
