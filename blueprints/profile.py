import os
import uuid
from flask import Blueprint, request, redirect, url_for, render_template, flash, send_from_directory, current_app, send_file, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db  # Импортируем объект БД и модель User, если потребуется

upload_bp = Blueprint('upload', __name__, template_folder='templates')

# Разрешённые расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Проверка расширения файла."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/profile/avatar/upload', methods=['POST'])
@login_required
def upload_file():
    # Проверяем, присутствует ли в запросе файл с ключом 'avatar'
    if 'avatar' not in request.files:
        flash('Файл не найден в запросе!')
        return redirect(request.url)
    
    file = request.files['avatar']
    
    # Если пользователь не выбрал файл, браузер отправляет пустое имя файла
    if file.filename == '':
        flash('Не выбран файл для загрузки!')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Безопасно формируем имя файла и добавляем уникальный префикс
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Обновляечм информацию об аватаре для залогиненного пользователя
        current_user.avatar_url = f"uploads/{unique_filename}"
        db.session.commit()
        
        flash('Файл успешно загружен!')
        # Перенаправляем, например, на страницу профиля или туда, где отображается аватар
        return redirect(url_for('upload.uploaded_file', filename=unique_filename))
    else:
        flash('Недопустимый формат файла!')
        return redirect(request.url)

@upload_bp.route('/avatars/uploads/<filename>')
def uploaded_file(filename):
    """
    Отдаёт загруженный файл.
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Обновление личных данных
@upload_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.form
    current_user.username = data.get('fullName', current_user.username)
    current_user.email = data.get('email', current_user.email)
    current_user.about = data.get('about', current_user.about)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Профиль обновлён успешно!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ошибка при сохранении данных: {str(e)}'})

# Смена пароля
@upload_bp.route('/profile/password/update', methods=['POST'])
@login_required
def update_password():
    data = request.form
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    # Проверка текущего пароля
    if not check_password_hash(current_user.password, current_password):
        return jsonify({'success': False, 'error': 'Неверный текущий пароль!'})

    # Проверка длины нового пароля
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': 'Пароль должен содержать не менее 6 символов!'})

    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Пароль успешно обновлён!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ошибка при обновлении пароля: {str(e)}'})

# Настройки уведомлений
@upload_bp.route('/profile/notifications/update', methods=['POST'])
@login_required
def update_notifications():
    data = request.form
    email_notifications = data.get('emailNotifications') == 'true'
    push_notifications = data.get('pushNotifications') == 'true'

    current_user.email_notifications = email_notifications
    current_user.push_notifications = push_notifications

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Настройки уведомлений обновлены!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ошибка при сохранении настроек: {str(e)}'})
