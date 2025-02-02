from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# Модель для таблицы "друзья" - связь многие ко многим
class Friendship(db.Model, UserMixin):
    __tablename__ = 'friendship'

    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    avatar_url = db.Column(db.String(150), nullable=False, default='uploads/default.png')
    email = db.Column(db.String(150), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    about = db.Column(db.String(500), nullable=True)
    email_notification = db.Column(db.Boolean, nullable=False, default=True)
    popup_notification = db.Column(db.Boolean, nullable=False, default=True)
    sms_notification = db.Column(db.Boolean, nullable=False, default=True)
    

    # Связь многие ко многим для списка друзей
    friends = db.relationship('User',
                              secondary='friendship',
                              primaryjoin=(id == Friendship.user1_id),
                              secondaryjoin=(id == Friendship.user2_id),
                              backref=db.backref('friends_of', lazy='dynamic'),
                              lazy='dynamic')
    
    # Login manager
    def get_id(self):
        return str(self.id)

# Модель для запроса на дружбу (удаляется после принятия или отклонения)
class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])  
    receiver = db.relationship('User', foreign_keys=[receiver_id])

# Модель для запросов на добавление в группу
class GroupJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, declined

    user = db.relationship('User', foreign_keys=[user_id])
    group = db.relationship('Group', foreign_keys=[group_id])


# Модель для групповых чатов
class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Связь между группой и её участниками
    members = db.relationship('User',
                              secondary='group_membership',
                              backref=db.backref('groups', lazy='dynamic'))

# Промежуточная таблица для связи "многие ко многим" между группами и пользователями
class GroupMembership(db.Model):
    __tablename__ = 'group_membership'
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

# Изменение модели сообщений для поддержки групповых сообщений
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Для личных сообщений
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)  # Для сообщений в группе
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь для отправителя и получателя
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    group = db.relationship('Group', foreign_keys=[group_id])
