from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# "Достар" кестесінің моделі-көптеген адамдармен байланыс
class Friendship(db.Model, UserMixin):
    __tablename__ = 'friendship'

    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Пайдаланушы моделі
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
    

    # Достар тізімі үшін көптеген байланыстар
    friends = db.relationship('User',
                              secondary='friendship',
                              primaryjoin=(id == Friendship.user1_id),
                              secondaryjoin=(id == Friendship.user2_id),
                              backref=db.backref('friends_of', lazy='dynamic'),
                              lazy='dynamic')
    
    # Login manager
    def get_id(self):
        return str(self.id)

# Достықты сұрауға арналған Модель (қабылданғаннан немесе қабылданбағаннан кейін жойылады)
class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])  
    receiver = db.relationship('User', foreign_keys=[receiver_id])

# Топқа қосу сұрауларына арналған Модель
class GroupJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, declined

    user = db.relationship('User', foreign_keys=[user_id])
    group = db.relationship('Group', foreign_keys=[group_id])


# Топтық чаттарға арналған Модель
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

# Топтар мен пайдаланушылар арасындағы көп-көп байланысқа арналған аралық кесте
class GroupMembership(db.Model):
    __tablename__ = 'group_membership'
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

# Топтық хабарламаларды қолдау үшін хабарлама үлгісін өзгерту
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Жеке хабарламалар үшін
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)  # Топтағы хабарламалар үшін
    content = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Новые поля для хранения файлов
    file_name = db.Column(db.String(255), nullable=True)  # Оригинальное имя файла
    file_path = db.Column(db.String(512), nullable=True)  # Путь к файлу на сервере
    file_type = db.Column(db.String(50), nullable=True)  # MIME-тип файла
    file_size = db.Column(db.Integer, nullable=True)  # Размер файла в байтах

    # Жіберуші мен алушы үшін байланыс
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    group = db.relationship('Group', foreign_keys=[group_id])
