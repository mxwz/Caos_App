import os
import random
import shutil
import string
import sys
from datetime import datetime, timedelta
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from argon2 import PasswordHasher
from captcha.image import ImageCaptcha
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, make_response, \
    abort, current_app
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_moment import Moment
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, EmailField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from config import config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# import bcrypt
from flask_bcrypt import Bcrypt

bootstrap = Bootstrap()  # 初始化bootstrap, 用于渲染bootstrap模板
moment = Moment()  # 初始化moment，用于时间格式化
# serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
migrate = Migrate()
ph = PasswordHasher()
mail = Mail()
login_manager = LoginManager()
db = SQLAlchemy()
admin = Admin(name='管理后台', template_mode='bootstrap3')       # 初始化 Flask-Admin
bcrypt = Bcrypt()
socketio = SocketIO()

def create_app(config_name="default"):
    """
    创建工程函数，初始化Flask应用
    :param config_name: 配置
    :return: app本身
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化 Flask-Session
    Session(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # 未登录的情况下直接引导到login函数

    # 配置 APScheduler(定时任务)
    scheduler = BackgroundScheduler()
    # 添加定时任务，每天凌晨一点执行一次
    scheduler.add_job(cleanup_folder, CronTrigger(hour=1, minute=0))
    scheduler.start()



    from Models import User, Role, UserActivity, UserProfile
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # get基于主键查询，利用索引快速定位

    # app.config.update(
    #     SESSION_COOKIE_HTTPONLY=False,  # 防止JavaScript访问cookie，从而减少XSS攻击的风险。
    #     SESSION_COOKIE_secure=False,  # 确保cookie只能通过HTTPS传输。
    # )
    # 用户管理界面
    admin.init_app(app)
    # 添加模型视图
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))
    admin.add_view(UserActivityAdmin(UserActivity, db.session))
    admin.add_view(UserProfileAdmin(UserProfile, db.session))
    # admin.add_view(UserView(name='user_manager'))

    # 文件服务器
    # from flask.ext.admin.contrib.fileadmin import FileAdmin
    # admin.add_view(FileAdmin(config_path, '/file/', name='Config Files'))

    # 增加会话超话时间，配合session.permanent = True使用
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
    # app.permanent_session_lifetime = timedelta(minutes=60)
    # app.permanent_session_lifetime = timedelta(days=1)  # 设置为1天

    if not os.path.exists('captcha'):
        os.makedirs('captcha')

    # 配置session设置
    # app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    # app.config['SESSION_COOKIE_SECURE'] = True  # 确保cookie只通过HTTPS传输

    # 设置应用上下文
    with app.app_context():
        db.create_all()

    # for key, value in app.config.items():
    #     print(f"{key}: {value}")
    register_bp(app)

    return app


def register_bp(app: Flask):
    """
    注册蓝本
    :param app: 加载应用
    :return: None
    """
    from app.main import main as main_blueprint
    from app.page import page as page_blueprint
    from app.manage import manage as manage_blueprint
    from app.chat import chat as chat_blueprint

    # 这里的url_prefix不是views的首页路径，而是蓝本的路径前缀，比如：/home/index
    app.register_blueprint(main_blueprint)
    app.register_blueprint(page_blueprint, url_prefix='/home')
    app.register_blueprint(manage_blueprint, url_prefix='/Management')
    app.register_blueprint(chat_blueprint, url_prefix='/chat')


def role_required(role):
    def decorator(f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role):
                abort(403)  # 禁止访问
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# @app.login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))  # get基于主键查询，利用索引快速定位




# 管理-添加用户(自定义表单，如果需要对表单自行定义可以使用，如若则默认)
class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6, max=256)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    email = EmailField('邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('提交')

# 自定义 ModelView，实现权限控制
class UserModelView(ModelView):
    can_export = True       # 数据导出为 CSV 文件
    name = "用户管理"

    form = UserForm
    column_list = ('id', 'username', 'email', 'password_hash', 'create_time')
    column_searchable_list = ('username', 'email')
    column_filters = ('username', 'email', 'create_time')
    # form_excluded_columns = ('password_hash', 'create_time')

    def is_accessible(self):
        # 只有管理员用户可以访问
        return current_user.is_authenticated and current_user.has_role('admin')
    def inaccessible_callback(self, name, **kwargs):
        # 非管理员用户跳转到登录页面
        return redirect(url_for('main.login'))




# 定义权限名称的选项(提交进去的元素为元组第一个：(value, label))
ROLE_CHOICES = [
    ('user', '普通用户'),
    ('admin', '管理员'),
]
class RoleForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    # name = StringField('权限名称', validators=[DataRequired()])
    name = SelectField('权限名称', choices=ROLE_CHOICES, validators=[DataRequired()])
    description = TextAreaField('Description')


class RoleAdmin(ModelView):
    # 使用自定义表单类
    form = RoleForm

    name = "权限管理"

    column_list = ('id', 'user_id', 'name', 'description')
    column_searchable_list = ('user_id', 'name', 'description')
    column_filters = ('name', 'description')
    # form_excluded_columns = ('user_id')  # 如果你不想在表单中显示 user_id 字段
    # 明确指定表单中显示的字段(如果需要user_id，必须去掉form_excluded_columns并且明示字段)
    form_columns = ('user_id', 'name', 'description')

    can_export = True  # 数据导出为 CSV 文件
    def is_accessible(self):
        # 只有管理员用户可以访问
        return current_user.is_authenticated and current_user.has_role('admin')
    def inaccessible_callback(self, name, **kwargs):
        # 非管理员用户跳转到登录页面
        return redirect(url_for('main.login'))




class UserActivityAdmin(ModelView):
    column_list = (
        'id', 'user_id', 'last_login', 'last_info_change', 'last_password_change', 'last_login_ip',
        'last_login_latitude', 'last_login_longitude', 'last_login_location',
        'last_login_device', 'last_device_info', 'last_login_location_description'
    )
    column_searchable_list = ('user_id', 'last_login_location', 'last_login_device')
    column_filters = ('user_id', 'last_login', 'last_info_change', 'last_password_change')
    # form_excluded_columns = ('last_device_info')  # 如果你不想在表单中显示 last_device_info 字段

    can_create = False  # 禁用创建新数据功能
    can_export = True  # 数据导出为 CSV 文件

    name = "登录信息管理"
    def is_accessible(self):
        # 只有管理员用户可以访问
        return current_user.is_authenticated and current_user.has_role('admin')
    def inaccessible_callback(self, name, **kwargs):
        # 非管理员用户跳转到登录页面
        return redirect(url_for('main.login'))




class UserProfileAdmin(ModelView):
    column_list = (
        'id', 'user_id', 'bio', 'phone_number', 'gender', 'age', 'industry', 'interests', 'location'
    )
    column_searchable_list = ('user_id', 'bio', 'phone_number', 'location')
    column_filters = ('user_id', 'gender', 'age', 'industry', 'location')
    can_export = True  # 数据导出为 CSV 文件
    name = "用户资料管理"

    def is_accessible(self):
        # 只有管理员用户可以访问
        return current_user.is_authenticated and current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        # 非管理员用户跳转到登录页面
        return redirect(url_for('main.login'))

def cleanup_folder(folder_path="captcha"):
    """
    清理指定文件夹内的所有文件和子文件夹。

    :param folder_path: 要清理的文件夹路径
    """
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.rmdir(dir_path)
                print(f"Deleted directory: {dir_path}")
        print(f"Cleaned up {folder_path}.")
        print(f"{len(os.listdir(folder_path))}")
    else:
        print(f"Folder {folder_path} does not exist.")