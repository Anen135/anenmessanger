import os
import uuid
from flask import Blueprint, request, redirect, url_for, render_template, flash, send_from_directory, current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
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
