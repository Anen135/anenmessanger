from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

# Регистрация
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!', 'error')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует!', 'error')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')

        # Вход пользователя сразу после регистрации
        login_user(new_user)
        resp = redirect(url_for('dashboard.dashboard'))

        # Устанавливаем cookie с именем пользователя
        resp.set_cookie('username', new_user.username)
        return resp
    return render_template('register.html')

# Логин
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))  # Если пользователь уже авторизован, перенаправляем его на dashboard

    # Проверка cookie на наличие имени пользователя
    username = request.cookies.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))  # Если cookie есть, автоматически авторизуем пользователя

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Входим в систему через Flask-Login
            login_user(user)

            # Устанавливаем cookie для имени пользователя
            resp = redirect(url_for('dashboard.dashboard'))
            resp.set_cookie('username', user.username)  # Устанавливаем cookie с именем пользователя

            return resp
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    return render_template('login.html')

# Логаут
@auth_bp.route('/logout')
def logout():
    # Выход через Flask-Login
    logout_user()

    # Удаляем cookie
    resp = redirect(url_for('auth.login'))
    resp.delete_cookie('username')  # Удаляем cookie при выходе

    return resp
