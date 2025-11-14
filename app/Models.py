from flask_login import UserMixin
from sqlalchemy import event

from datetime import datetime

from app import db


# UserMixin 是 Flask-Login 提供的一个帮助类，包含了一些实现用户会话管理所需的方法。\
# is_authenticated：如果用户已经登录，则返回 True。
# is_active：如果用户的账户是活跃的，则返回 True。对于大多数应用来说，这意味着用户的账户没有被禁用。
# is_anonymous：对于普通用户，这应该返回 False，因为匿名用户通常是指那些没有登录的用户。
# get_id：返回用户的唯一标识符，通常是一个用户 ID。Flask-Login 使用这个标识符来在会话中识别用户。
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)            # 用户ID
    username = db.Column("name", db.String(64), unique=True, nullable=False)    # 用户名(唯一标识)
    password_hash = db.Column(db.String(256), nullable=False)                   # 用户密码(哈希值加密)
    email = db.Column(db.String(150), unique=True, nullable=False)              # 邮箱(唯一标识)
    create_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), nullable=False)      # 创建时间

    # Relationships
    activities = db.relationship('UserActivity', back_populates='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    profile = db.relationship('UserProfile', uselist=False, back_populates='user')
    roles = db.relationship('Role', back_populates='user', cascade='all, delete-orphan')
    gpt = db.relationship('GPTConversation', back_populates='user')
    def is_admin(self):
        # 假设Role表中有一个字段name用来标识角色名称
        return any(role.name == 'admin' for role in self.roles)

    # 添加一个方法来检查用户是否有特定的角色
    def has_role(self, role_name):
        # 确保加载用户的角色，这里假设角色已经被预加载
        return any(role.name == role_name for role in self.roles)

    def is_authenticated(self):
        return True

    # def __repr__(self):
    #     return f'<User {self.username}>'

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)                     # 评论ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)           # 用户ID
    content = db.Column(db.Text, nullable=False)                                         # 评论内容
    timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())       # 评论时间
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'))  # 指定外键删除行为

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                              lazy=True, cascade='all, delete-orphan')  # 确保子评论随父评论删除
    # 设置反向关系，让User模型可以访问其相关的评论
    user = db.relationship('User', back_populates='comments')

    # def __repr__(self):
    #     return f'<Comment {self.content[:20]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'replies': [reply.to_dict() for reply in self.replies],
            'username': self.user.username
        }

class UserActivity(db.Model):
    __tablename__ = 'user_activity'

    id = db.Column(db.Integer, primary_key=True)        # 主键，活跃表ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)      # 用户ID
    last_login = db.Column(db.DateTime, nullable=True)              # 最后登录时间
    last_info_change = db.Column(db.DateTime, nullable=True)        # 最后信息更改时间
    last_password_change = db.Column(db.DateTime, nullable=True)    # 最后密码修改时间

    last_login_ip = db.Column(db.String(45), nullable=True)
    last_login_latitude = db.Column(db.Float, nullable=True)        # 最后登录位置的纬度
    last_login_longitude = db.Column(db.Float, nullable=True)       # 最后登录位置的经度
    last_login_location = db.Column(db.String(255), nullable=True)  # 最后登录位置描述
    last_login_device = db.Column(db.String(100), nullable=True)    # 最后登录的设备
    last_device_info = db.Column(db.JSON, nullable=True)
    last_login_location_description = db.Column(db.String(255), nullable=True)  # 最后登录位置描述

    # 设置反向关系，让用户模型可以访问其相关的活动记录
    user = db.relationship('User', back_populates='activities')

    # def __repr__(self):
    #     return f'<UserActivity {self.user_id}>'

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)        # 用户信息ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)     # 用户ID
    bio = db.Column(db.String(255), nullable=True)                          # 个性签名
    phone_number = db.Column(db.String(20), nullable=True)                  # 手机号
    gender = db.Column(db.String(10), nullable=True)                        # 性别
    age = db.Column(db.Integer, nullable=True)                              # 年龄
    industry = db.Column(db.String(50), nullable=True)                      # 行业
    interests = db.Column(db.String(200), nullable=True)                    # 兴趣
    location = db.Column(db.String(100), nullable=True)                     # 所在地区
    photo = db.Column(db.String(255))                                       # 存储头像的文件路径

    # 设置反向关系，让用户模型可以访问其相关的个人资料
    user = db.relationship('User', back_populates='profile')

    # def __repr__(self):
    #     return f'<UserProfile {self.user_id}>'



class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)                # 用户权限ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)      # 用户ID
    name = db.Column(db.String(50), nullable=False, default='user')                 # 权限名称(admin，user)
    description = db.Column(db.String(255), nullable=True)                          # 权限描述(例如星级用户，管理层，普通用户)

    # 反向关系，允许从Role访问关联的User
    user = db.relationship('User', back_populates='roles')


# # 监听User模型的after_insert事件
# @event.listens_for(User, 'after_insert')
# def create_default_role(mapper, connection, target):
#     # 创建一个默认的角色
#     role = Role(user_id=target.id, name='default', description='Default role for new users')
#     db.session.add(role)
#     db.session.flush()  # 确保角色被立即添加到数据库中


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.String(648), primary_key=True)
    data = db.Column(db.LargeBinary)
    expiry = db.Column(db.DateTime)

    def __init__(self, sid, data, expiry):
        self.id = sid
        self.data = data
        self.expiry = expiry

    def __repr__(self):
        return f'<Session {self.id}>'

    @classmethod
    def extend_existing(cls):
        return True



class GPTConversation(db.Model):
    __tablename__ = 'gpt'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.String(1024), nullable=False)
    answer_reasoning = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 设置反向关系，让用户模型可以访问其相关的GPT对话记录
    user = db.relationship('User', back_populates='gpt')

    def __repr__(self):
        return f'<GPTConversation {self.id}>'