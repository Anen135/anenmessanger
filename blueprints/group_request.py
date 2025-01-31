from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import db, User, Group, GroupJoinRequest, GroupMembership

group_requests_bp = Blueprint('group_requests', __name__)

# Отправка запроса на добавление в группу
@group_requests_bp.route('/send_group_request', methods=['POST'])
@login_required
def send_group_request():
    group_id = request.form.get('group_id')
    group = Group.query.get(group_id)

    if not group:
        return jsonify({'success': False, 'message': 'Группа не найдена'})

    # Проверка, что пользователь не является уже участником группы
    membership = GroupMembership.query.filter_by(group_id=group.id, user_id=current_user.id).first()
    if membership:
        return jsonify({'success': False, 'message': 'Вы уже участник этой группы'})

    # Проверка, что запрос уже отправлен
    existing_request = GroupJoinRequest.query.filter_by(group_id=group.id, user_id=current_user.id).first()
    if existing_request:
        return jsonify({'success': False, 'message': 'Запрос уже отправлен'})

    # Создаем запрос на добавление в группу
    group_request = GroupJoinRequest(group_id=group.id, user_id=current_user.id)
    db.session.add(group_request)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Запрос отправлен успешно'})

# Получение запросов на добавление в группу
@group_requests_bp.route('/get_group_requests', methods=['GET'])
@login_required
def get_group_requests():
    # Получаем входящие запросы для групп, где текущий пользователь является создателем
    groups = Group.query.filter_by(creator_id=current_user.id).all()
    group_ids = [group.id for group in groups]

    incoming_requests = GroupJoinRequest.query.filter(GroupJoinRequest.group_id.in_(group_ids)).all()

    incoming_requests_list = [
        {'id': req.id, 'user_username': req.user.username, 'group_name': req.group.name}
        for req in incoming_requests
    ]

    # Получаем исходящие запросы текущего пользователя
    outgoing_requests = GroupJoinRequest.query.filter_by(user_id=current_user.id).all()
    outgoing_requests_list = [
        {'id': req.id, 'group_name': req.group.name}
        for req in outgoing_requests
    ]

    return jsonify({
        'success': True,
        'incoming_requests': incoming_requests_list,
        'outgoing_requests': outgoing_requests_list
    })

# Ответ на запрос (принятие/отклонение)
@group_requests_bp.route('/respond_group_request/<int:request_id>/<action>', methods=['POST'])
@login_required
def respond_group_request(request_id, action):
    group_request = GroupJoinRequest.query.get(request_id)

    if not group_request:
        return jsonify({'success': False, 'message': 'Запрос не найден'})

    # Проверка, что текущий пользователь является создателем группы
    if group_request.group.creator_id != current_user.id:
        return jsonify({'success': False, 'message': 'Вы не можете управлять этим запросом'})

    if action not in ['accept', 'decline']:
        return jsonify({'success': False, 'message': 'Неверное действие'})

    if action == 'accept':
        # Добавляем пользователя в группу
        membership = GroupMembership(group_id=group_request.group_id, user_id=group_request.user_id)
        db.session.add(membership)

        # Обновляем статус запроса
        group_request.status = 'accepted'

    elif action == 'decline':
        # Обновляем статус запроса
        group_request.status = 'declined'

    db.session.commit()

    return jsonify({'success': True, 'message': f'Запрос был {action}.'})
