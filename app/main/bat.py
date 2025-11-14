# 隐私政策 √
# 不切换页面 √
# 提示闪回 √
# session缓存 √
# 换界面 √
# 自动填充信息 √
# 添加邮箱验证功能，发送验证码的同时可以点击邮件里的链接进行验证
# 邮箱验证需求增加时间核验，五分钟过期 √
# 管理session，去除一切不必要且繁琐的参数
# 忘记密码 √
# 保持登录cookie
# 跟踪器
# https，申请Let’s Encrypt（https://www.cnblogs.com/88223100/p/Generate-free-SSL-certificates-through-Let_s-Encrypt.html）
# 因素认证（设备）
# 如何进行会话管理，设置httponly和secure，还有如何进行轮换会话id
# 自动刷新验证码（HTML中） √
# 更改主页（导航栏人物下拉栏）
# 提示闪回消失
# 日夜模式切换
# 记住登录名和密码
# 自动登录
# 日志记录
import json
import logging

# FLASK_RUN_CERT=C:\Users\yang\localhost.pem;FLASK_RUN_KEY=C:\Users\yang\localhost-key.pem;FLASK_DEBUG=0;FLASK_HOST=0.0.0.0;FLASK_PORT=5036

import re
# <li><a href="https://www.china.com" target="_blank">中华网</a></li>，如果去掉target则实现不新开页面切换

# session.pop('email_code', None)
# session.pop('email_sent_time', None)

# redirect(url_for("register"))比render_template好处在刷新不会提示重新提交表单

# 第一次访问是get请求，提交表单时使用render_template，需要处理每一个网页对于get的请求，否则会访问频繁且死循环访问

# <form action="">可以重定向到指定路径

# @login_required用于保护路由，确保只有经过身份验证的用户才能访问，意味着该函数只能由已经登录的用户访问。\
# 如果未登录的用户尝试访问这个视图，Flask-Login 会拦截请求，并将用户重定向到一个登录页面。\
# @login_required 装饰器检查当前是否有用户登录。这通常是通过检查 Flask 的会话来完成的，Flask-Login 在用户登录时会将会话标记为已登录。\
# 如果用户未登录，@login_required 会自动将用户重定向到登录视图。默认情况下，这个视图的端点是 'login'，但您可以通过配置 Flask-Login 来更改它。

# 删除当前会话的所有内容  session.clear()，然后再重新使用session['xxx']=''即可重新创建会话ID

# readonly字段只读，required字段必填

# 如果<form>元素没有定义action属性，那么表单提交时默认会提交到当前页面所在的URL

# 多个浏览器标签或窗口：如果用户在提交位置信息后，打开了另一个浏览器标签或窗口访问例如/3D_map，那么新的标签或窗口将不会拥有之前的session数据。

# user_activity = UserActivity.query.filter_by(user_id=current_user.id).first()中current_user.id可以获取登录状态的用户id

import secrets
import shutil
import signal
import sys
import time
from functools import wraps

import pytz
import requests
from flask_cors import CORS, cross_origin
from flask_debugtoolbar import DebugToolbarExtension

# 这两种一种是flask_jwt_extended，一种是pyjwt，还有一种是jwt
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
# JWT(签名) 是一种开放标准 (RFC 7519)，用于在各方之间安全地传输信息作为 JSON 对象。JWT 通常用于身份验证和信息交换。
import jwt

from flask_login import LoginManager, login_manager, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, make_response, \
    abort
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from captcha.image import ImageCaptcha
from flask_mail import Mail, Message
import os

# 相比bcrypt加盐(第一种)，scrypt提高更高的内存和计算成本(第二种)
import bcrypt
# from flask_bcrypt import Bcrypt

import random
import string
from datetime import timedelta, datetime
from flask_wtf import FlaskForm
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import DataRequired
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


logging.basicConfig(level=logging.DEBUG)

if not os.path.exists('test4/captcha'):
    os.makedirs('test4/captcha')
app = Flask(__name__, template_folder='templates', static_folder='static')
bootstrap = Bootstrap(app)
# app.secret_key = os.getenv('FLASK_SECRET_KEY')
# app.secret_key = secrets.token_hex(256)  # 生成一个32字符的随机密钥

# 生成一个256位的十六进制字符串，字节数是256位/4 = 64字节，可以直接用作字符串，无需进行编码转换。可以用于JWT签名
# 通常128位或192位就已经足够安全
app.config['SECRET_KEY'] = secrets.token_hex(192)  # 全局秘钥
app.config['JWT_SECRET_KEY'] = os.urandom(24).hex()
# 生成一个24字节的随机字节串，在使用前可能需要将其转换为一个适合作为密钥的格式（例如，转换为十六进制字符串）
# app.config['SECRET_KEY'] = os.urandom(24)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# 配置会话存储类型为Redis
# app.config['SESSION_TYPE'] = 'redis'
# 会话不会在浏览器关闭后持续
app.config['SESSION_PERMANENT'] = False
# 对会话ID进行签名
app.config['SESSION_USE_SIGNER'] = False
# Redis会话键的前缀
# app.config['SESSION_KEY_PREFIX'] = 'session:'

# 开启 GZIP 压缩
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31557600  # 缓存静态文件一年
# app.config['PROPAGATE_EXCEPTIONS'] = True

# 调试模式
# app.config['DEBUG'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# toolbar = DebugToolbarExtension(app)

# 避免太多警告用False
# app.config['PROPAGATE_EXCEPTIONS'] = False
# app.config['TRAP_HTTP_EXCEPTIONS'] = False

# jwt = JWTManager(app)
# bcrypt = Bcrypt(app)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:2207150132@localhost/flask_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        # 避免不必要的警告
db = SQLAlchemy(app)
# 迁移数据库
migrate = Migrate(app, db)

ph = PasswordHasher()
moment = Moment(app)

from Models import User, Comment, UserActivity, UserProfile, Role

# 设置应用上下文
with app.app_context():
    db.create_all()

# 邮件设置（用于邮件验证码）
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True  # 对于587端口
app.config['MAIL_USE_SSL'] = False  # 对于587端口
app.config['MAIL_USERNAME'] = '1822983135@qq.com'
app.config['MAIL_PASSWORD'] = 'ydkmpvdgbvchcehh'
mail = Mail(app)

# 限制每个邮箱地址在一定时间内发送验证码的次数
EMAIL_CODE_LIMIT = 5  # 每个邮箱5分钟内最多发送的验证码次数
EMAIL_CODE_INTERVAL = timedelta(minutes=5)

# 设置会话持久性
# app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)  # 设置记住我功能有效期为？天

# 增加会话超话时间，配合session.permanent = True使用
app.permanent_session_lifetime = timedelta(minutes=60)
# app.permanent_session_lifetime = timedelta(days=1)  # 设置为1天


# 设置允许的来源域名
ALLOWED_ORIGINS = ['http://127.0.0.1:5000', 'http://localhost:5000', 'https://127.0.0.1:5000', 'https://localhost:5000', ]
# CORS(app, supports_credentials=True)
# # CORS 是一种机制，它使用额外的 HTTP 头来告诉浏览器允许一个域上的 web 应用程序访问另一个域上的资源。默认情况下，浏览器出于安全原因会阻止跨域请求。
# # CORS 提供了一种标准的方法来允许跨域请求。
# # 配置CORS，仅允许特定源访问，并支持凭证
# cors_options = {
#     "origins": ["http://localhost:5000", "http://localhost:3000", "http://localhost:443"],  # 替换为实际的前端地址
#     "supports_credentials": True
# }
# CORS(app, **cors_options)  # 这将启用所有源的CORS

# 如果您想要更精细的控制，可以指定特定的来源
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# 允许特定来源的跨域请求
# cors = CORS(app, resources={
#     r"/api/*": {
#         "origins": ["http://example.com", "https://sub.example.com"]
#     }
# })
#
# # 或者使用装饰器来指定CORS策略
# @app.route('/api/submit_location', methods=['POST'])
# @cross_origin(origins=["http://example.com", "https://sub.example.com"],
#               allow_headers=['Content-Type', 'Authorization'])
# def submit_location():
#     data = request.get_json()
#     position = data.get('position')
#     response = jsonify({'status': 'success', 'message': 'Location received'})
#     response.set_cookie('position', value=position, path='/', httponly=True, secure=True, samesite='Lax')
#     return response
# 代替CORS（跨源资源共享），使用CORS头部
# @app.after_request
# def after_request(response):
#     # 获取请求的来源
#     origin = request.headers.get('Origin')
#
#     # 如果请求的来源在允许的列表中，则设置CORS头部
#     if origin in ALLOWED_ORIGINS:
#         response.headers.add('Access-Control-Allow-Origin', origin)
#         response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#         response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#         response.headers.add('Access-Control-Allow-Credentials', 'true')
#
#     return response


# 以下两种方法都可以用，用于权限认证
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

@app.route('/123')
@role_required('admin')
def admin():
    return 'Admin page'

@app.route('/1234')
@login_required
def admin2():
    if not current_user.is_admin():
        abort(403)
    return 'Admin page'

# 缺少了user_loader或request_loader回调函数。Flask-Login需要这些函数来加载当前登录的用户。
# 未登录状态尝试登录需要认证的网页时触发
# 用于单个应用，创建实例的同时直接初始化，简单操作
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'      # 直接引导到login函数
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))       # get基于主键查询，利用索引快速定位


# 用于多个应用（app赋值），需要手动初始化，两种方法都是等价的
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'      # 未登录的情况下直接引导到login函数

# @login_manager.user_loader
# def load_user(email):
#     return User.query.filter_by(email=email).first()        # 任意字段查询，如无索引则效率慢

# 用户加载函数，从会话中存储的用户ID中加载用户对象，作用是告诉Flask-Login如何获取用户实例，以便在请求之间保持用户的登录状态。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))       # get基于主键查询，利用索引快速定位


# 配置cookie HTTPOnly和Secure标志（需要配置https）
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,     # 防止JavaScript访问cookie，从而减少XSS攻击的风险。
    SESSION_COOKIE_secure=False,        # 确保cookie只能通过HTTPS传输。
)

# 会话更新和迁移数据操作
# 这个方法依赖于Flask的会话机制，它通常使用签名cookie来存储会话数据。而不是服务器端会话存储（如Redis或数据库）
@app.route('/update_session_id')
def update_session_id():
    # 步骤 1: 保存当前会话数据
    current_session_data = dict(session)
    # 步骤 2: 重置会话来生成新的会话ID
    session.clear()
    # 步骤 3: 恢复会话数据
    for key, value in current_session_data.items():
        session[key] = value

    # 可以返回一些信息表示会话ID已更新
    return 'Session ID updated successfully.'

# 管理员验证

# 是否超出电子邮件代码发送限制
def is_email_code_send_limit_exceeded(email):
    if 'email_send_counts' not in session:
        session['email_send_counts'] = {}

    send_counts = session['email_send_counts'].get(email, 0)
    last_send_time = session.get(f'{email}_last_send_time', None)

    if last_send_time and datetime.utcnow() - datetime.fromisoformat(last_send_time) < EMAIL_CODE_INTERVAL:
        send_counts += 1
    else:
        send_counts = 1
        session[f'{email}_last_send_time'] = datetime.utcnow().isoformat()

    session['email_send_counts'][email] = send_counts

    return send_counts > EMAIL_CODE_LIMIT

# 关闭后自动清理验证码，并且重新创建验证码页
# 需要改进：验证码夹内超过100个及时删除避免堆积
def save_data(signum, frame):
    print("程序正在关闭，执行删除操作...")
    file_path = "test4/captcha"
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
        print("删除成功")
    else:
        print("无此文件夹")
    if not os.path.exists('test4/captcha'):
        os.makedirs('test4/captcha')
    sys.exit(0)


def cleanup_folder(folder_path="test4/captcha"):
    """
    清理指定文件夹内的文件，保留最新的100个文件。

    :param folder_path: 要清理的文件夹路径
    """
    # 获取文件夹内所有文件和文件夹的列表
    entries = os.listdir(folder_path)
    # 过滤出所有文件
    files = [entry for entry in entries if os.path.isfile(os.path.join(folder_path, entry))]
    # 获取文件数量
    file_count = len(files)
    # 如果文件数量超过100，则清理
    if file_count > 100:
        # 按最后修改时间排序文件
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
        # 计算需要删除的文件数量
        files_to_delete = files[:-100]  # 保留最后100个文件
        # 删除文件
        for file_name in files_to_delete:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
            print(f"Deleted: {file_name}")
        print(f"Cleaned up {len(files_to_delete)} files, {len(files) - len(files_to_delete)} files remaining.")
    else:
        print(f"{file_count} files found, no cleanup needed.")

# 初始化数据库，新版本弃用了，直接使用db.create_all()即可
# @app.before_first_request
# def create_tables():
#     db.create_all()


# def ip_address():
#     def IP():
#         res = requests.get('http://myip.ipip.net', timeout=5).text
#         print(res)
#         # 使用正则表达式匹配IP地址
#         ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
#         match = re.search(ip_pattern, res)
#         # if match:
#         #     ip_address = match.group(0)
#         #     return ip_address
#         # else:
#         #     return None
#         return match and match.group(0)
#
#     ip = IP() or "未找到IP地址"
#     if ip:
#         L_json = requests.get(f"https://restapi.amap.com/v3/ip?ip={ip}&output=json&key=c617d9f467708db4f7fd97f31a37adbd").json()



# 哈希密码函数
def hash_password(password):
    # password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    # return password
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# 验证密码
def check_password(stored_password, provided_password):
    # return bcrypt.check_password_hash(provided_password, stored_password)
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

# 生成验证码图像
def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = ImageCaptcha()
    image_file = os.path.join(r'test4\\captcha', f"{captcha_text}.png")
    image.write(captcha_text, image_file)
    return captcha_text


def send_email_verification(recipient, code):
    html_body = f'''  
    <html>  
    <head>  
        <title>邮箱验证码</title>  
        <style>  
            body {{  
                background-color: #f0f0f0; /* 设置背景颜色为浅灰色 */  
                margin: 0;  
                padding: 20px;  
                font-family: Arial, sans-serif;  
            }}  
            .container {{  
                background-color: #ffffff; /* 设置内容区域背景颜色为白色 */  
                padding: 20px;  
                border-radius: 8px;  
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);  
                max-width: 600px;  
                margin: auto;  
            }}  
            h1 {{  
                color: #333333; /* 设置标题颜色 */  
                margin-top: 0;  
            }}  
            p {{  
                color: #666666; /* 设置段落文字颜色 */  
                line-height: 1.6;  
            }}  
            .code {{  
                font-size: 1.5em;  
                font-weight: bold;  
                color: #ff5733; /* 设置验证码文字颜色 */  
                margin: 10px 0;  
            }}  
        </style>  
    </head>  
    <body>  
        <div class="container">  
            <h1>您的邮箱验证码是:</h1>  
            <p class="code">{code}</p>  
            <p>请点击下面的链接或复制验证码进行验证。如果您没有请求此验证码，请忽略此邮件。</p>  
        </div>  
    </body>  
    </html>  
    '''
    msg = Message('[混沌新城]邮箱验证码', sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.html = html_body
    mail.send(msg)


# 会话ID轮换（手动）
# 一般来说这是不需要的，flask框架会自动处理会话。用于处理会话劫持，重新生成会话ID
@app.route('/rotate_session')
def rotate_session():
    # 删除旧的会话
    session.clear()
    # 创建一个新的会话ID
    session['session_id'] = os.urandom(24)
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    user_id = session.get('user_id')
    user_name = session.get('username')
    email = session.get('email')

    # 查询用户配置文件
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        # 如果用户没有 UserProfile 记录，则创建一个新的 UserProfile 实例
        user_profile = UserProfile(user_id=user_id)
        db.session.add(user_profile)
        db.session.commit()  # 提交会话以保存新创建的记录到数据库
    else:
        # 如果用户已经有 UserProfile 记录，则使用现有的 UserProfile 实例
        user_profile = profile

    return render_template('home.html',
                           email=email,
                           username=user_name,
                           phone_number=user_profile.phone_number,
                           gender=user_profile.gender,
                           age=user_profile.age,
                           industry=user_profile.industry,
                           bio=user_profile.bio,
                           interests=user_profile.interests,
                           location=user_profile.location)



@app.route('/')
def index():
    if 'username' in session:
        # return render_template('profile.html', username=session['username'])
        # 获取当前登录用户的UserActivity记录，或者创建一个新的
        # Browser = session.get('Browser_Detection')
        # user_activity = UserActivity.query.filter_by(user_id=current_user.id).first()
        # if not user_activity:
        #     user_activity = UserActivity(user_id=current_user.id)
        #     db.session.add(user_activity)
        # # 更新UserActivity记录
        # user_activity.last_login_device = Browser['平台类型']
        # # 提交数据库更改
        # db.session.commit()
        return render_template('index.html', username=session['username'])
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 提取输入的登录账号、密码、验证码
        login_name = request.form['login_name']
        session['login_name'] = login_name
        password = request.form['password']
        captcha_input = request.form['captcha']

        # 验证图像验证码，小写转大写可以优化用户个人输入习惯，减少了验证难度
        if captcha_input.upper() != session.get('captcha_text'):
            flash('验证码错误!')
            return redirect(url_for('login'))

        # 根据用户提供的登录账号，在users表中的username与mail中索引，查找是否存在，不存在返回None(user和email是返回的json)
        # user = User.query.filter((User.username == login_name) | (User.email == login_name)).first()
        # 使用 or_ 优化查询
        user = User.query.filter(or_(User.username == login_name, User.email == login_name)).first()

        logging.debug("开始验证登录……")
        # user = User.query.filter_by(username=login_name).first()
        # email = User.query.filter_by(email=login_name).first()
        # 用户名登录
        if user and check_password_hash(user.password_hash, password):
        # if user and ph.verify(user.password_hash, password):
            logging.debug("登录验证成功！")
            # 更新用户的登录时间
            # 用于检查user对象的activities属性是否已经存在，如果存在则直接使用，如果不存在则创建一个新的UserActivity实例
            # 检查user对象的activities属性是否已经存在
            if not user.activities:
                # 如果不存在则创建一个新的UserActivity实例
                user_activity = UserActivity(user_id=user.id)
                db.session.add(user_activity)
            else:
                # 如果存在，则获取第一个UserActivity实例
                user_activity = user.activities[0]
            Browser = session.get('Browser_Detection')
            if not Browser:
                logging.debug("获取浏览器参数……")
                browser_json_str = request.cookies.get('Browser_Detection')
                print(browser_json_str)
                Browser = json.loads(browser_json_str)
            last_login_utc = datetime.utcnow()
            # 定义本地时区
            local_tz = pytz.timezone('Asia/Shanghai')  # 对于中国标准时间
            # 将 UTC 时间转换为本地时间
            last_login_local = last_login_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            user_activity.last_login = last_login_local
            user_activity.last_login_device = Browser['平台类型']
            db.session.commit()
            logging.debug("提交完毕！")

            # 删除当前会话的所有内容，防止会话劫持，但是会把之前的session全部删除
            # session.clear()

            session.permanent = True  # 设置会话为持久性
            session['username'] = user.username
            session['email'] = user.email
            session['user_id'] = user.id
            # remember参数用于保持登录状态
            # login_user(user)  # 登录用户
            login_user(user, remember=True)  # 登录用户
            flash('登录成功!')

            # if 'remember_me' in request.form:
            if 'automatic_login' in request.form:
                # 创建JWT令牌
                token = jwt.encode({
                    'user_id': user.id,
                    'exp': last_login_utc + timedelta(days=7)
                }, app.config['JWT_SECRET_KEY'], algorithm='HS256')

                # 将令牌存储在cookie中
                resp = make_response(redirect(url_for('index')))
                # httponly和secure是https加密参数
                # secure = True确保cookie只能通过HTTPS传输，而httponly = True确保cookie不能通过客户端脚本访问
                resp.set_cookie('jwt', token, httponly=False, secure=True)
                resp.set_cookie('user_id', user.id, httponly=False, secure=True)
                resp.set_cookie('username', user.username, httponly=False, secure=True)
                resp.set_cookie('email', user.email, httponly=False, secure=True)
                logging.debug("登陆成功")
                return resp
            return redirect(url_for('index'))
        # 用户不存在/密码错误
        else:
            flash('用户名或密码错误!')      # 为防止sql注入风险，不提示密码错误和账户不存在
        session['captcha_text'] = generate_captcha()
        # request.args.get('login_name', '')中从http://xxx/login.bat.html?login_name=获取数据，如果填写了则有，未填写则为''
        return redirect(url_for('login', username=request.args.get('login_name', '')))

    else:
        session['captcha_text'] = generate_captcha()
        if session.get('login_name'):
            username = session.get('login_name')
        else:
            username = ""
        return render_template('login.bat.html', username=username)
        # return render_template('login.bat.html')


# class NameForm(FlaskForm):
#     name = StringField("What is your name?", validators=[DataRequired()])
#     submit = SubmitField('Submit')

# 定义表单模型
class UserProfileForm(FlaskForm):
    # DataRequired：一个验证器，确保字段不能为空。
    # bio = StringField('个性签名', validators=[DataRequired()])
    bio = StringField('个性签名')
    phone_number = StringField('电话号码')
    gender = StringField('性别')
    age = IntegerField('年龄')
    industry = StringField('行业')
    interests = StringField('兴趣')
    location = StringField('地址')
    submit = SubmitField('提交')


@app.route('/input/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user_id = session.get('user_id')
    name = session.get('username')
    email = session.get('email')


    user = User.query.get_or_404(user_id)
    form = UserProfileForm(obj=user.profile)

    if form.validate_on_submit():
        if user.profile:
            user.profile.bio = form.bio.data
            user.profile.phone_number = form.phone_number.data
            user.profile.gender = form.gender.data
            user.profile.age = form.age.data
            user.profile.industry = form.industry.data
            user.profile.interests = form.interests.data
            user.profile.location = form.location.data
        else:
            user.profile = UserProfile(
                user_id=user.id,
                bio=form.bio.data,
                phone_number=form.phone_number.data,
                gender=form.gender.data,
                age=form.age.data,
                industry=form.industry.data,
                interests=form.interests.data,
                location=form.location.data
            )
        db.session.commit()
        flash('个人信息已更新！', 'success')
        return redirect(url_for('home'))

    return render_template('update_profile.html', form=form, user=user, name=name, email=email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        email_code_input = request.form.get('email_code', None)

        # 检查邮箱是否已存在
        # existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        existing_user_email = User.query.filter_by(email=email).first()
        if existing_user_email:
            flash('该邮箱已存在，请使用其他邮箱注册。')
            return render_template('register.bat.html')
        existing_user_name = User.query.filter_by(username=username).first()
        if existing_user_name:
            flash('该用户名已存在，请使用其他用户名注册。')
            return render_template('register.bat.html')

        if email_code_input == session.get('email_code') and 'email_sent_time' in session:
            email_sent_time = datetime.fromisoformat(session['email_sent_time'])
            if datetime.utcnow() - email_sent_time > timedelta(minutes=5):
                flash('验证码已过期，请重新发送!')
                # 清除过期的验证码和发送时间
                session.pop('email_code', None)
                session.pop('email_sent_time', None)
                return render_template('register.bat.html')  # 重新显示注册表单
            # 检查是否超过了发送限制
            if is_email_code_send_limit_exceeded(email):
                flash('您已达到发送验证码的限制，请稍后再试。')
                return render_template('register.bat.html')
            new_user = User(username=username, password_hash=generate_password_hash(password), email=email)
            # argon2牺牲安全性，但是速度快
            # new_user = User(username=username, password_hash=ph.hash(password), email=email)
            db.session.add(new_user)
            db.session.commit()
            new_user_roles = Role(user_id=new_user.id, name='user', description='normal')
            # new_user = User(username=username, password_hash=bcrypt.generate_password_hash(password).decode('utf-8'), email=email)
            db.session.add(new_user_roles)
            db.session.commit()
            flash('注册成功，请登录!')
            return redirect(url_for('login'))
        else:
            flash('邮箱验证码错误!')
            # 保存输入信息到 session
            # session['username'] = username
            # session['email'] = email
    # 从 session 中获取之前输入的信息（如果有的话）
    # username = session.get('username', '')
    # email = session.get('email', '')

    # return render_template('register.bat.html', username=username, email=email)
    # return render_template('register.bat.html')
        return redirect(url_for("register"))
    else:
        return render_template('register.bat.html')



# 检测到页面刷新则执行
@app.route('/page-refreshed', methods=['POST'])
def handle_page_refresh():
    if request.method == 'POST':
        if 'email_sent_time' in session:
            data = request.get_json()
            if data and data.get('refreshed'):
                # 清空会话
                del session['email_sent_time']
                # flash("注册失败，验证码无效")
                return jsonify({'cleared': True, 'message': "注册失败，验证码无效"})
    return jsonify({'cleared': False})


@app.route('/generate_captcha')
def generate_captcha_route():
    captcha_text = generate_captcha()
    return jsonify({'captcha_text': captcha_text})

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        email_code_input = request.form['email_code']
        username = session.get('temp_username')

        if email_code_input == session.get('email_code'):
            new_user = User(username=username, password_hash=generate_password_hash(request.form['password']))
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功，请登录!')
            return redirect(url_for('login'))
        else:
            flash('验证码错误!')

    return render_template('verify_email.html')

# 只实现了永久性且一次性的注册验证码
@app.route('/send_email', methods=['POST'])
def send_email():
    email = request.form['email']

    # 检查发送限制
    if is_email_code_send_limit_exceeded(email):
        return jsonify({'message': '您已达到发送验证码的限制，请稍后再试。'}), 429  # 429 Too Many Requests

    email_code = ''.join(random.choices(string.digits, k=6))
    try:
        send_email_verification(email, email_code)
        session['email_code'] = email_code
        session['email_sent_time'] = datetime.utcnow().isoformat()  # 存储为 ISO 格式字符串
        return jsonify({'message': '验证码已发送!'})
    except Exception as e:
        # 记录错误日志
        app.logger.error(f'Failed to send email verification: {e}')
        return jsonify({'message': '发送验证码时出错，请稍后再试。'}), 500  # 500 Internal Server Error


@app.route('/logout')
@login_required     # 新
def logout():
    session.pop('username', None)
    logout_user()       # 登出用户
    flash('您已成功登出!')
    # return redirect(url_for('index'))

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('jwt', '', expires=0, httponly=False, secure=True)  # 删除cookie
    return resp

# 日志审查
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())


# 多层级评论
@app.route('/comment', methods=['GET', 'POST'])
@login_required
def comment():
    if request.method == 'POST':
        comment_content = request.form['comment']
        parent_id = request.form.get('parent_id', None)
        reply_to_username = request.form.get('reply_to_username', None)

        # 确保parent_id是一个整数或者None
        parent_id = int(parent_id) if parent_id else None

        if parent_id and reply_to_username:
            # 如果是回复，添加前缀
            comment_content = f"回复 {reply_to_username}：{comment_content}"

        new_comment = Comment(content=comment_content, user_id=current_user.id, parent_id=parent_id)
        db.session.add(new_comment)
        db.session.commit()

    # 使用 joinedload 预加载子评论
    comments = Comment.query.options(db.joinedload(Comment.replies)).filter_by(parent_id=None).all()
    return render_template('comments.bat.html', comments=comments)


# 单层级(父子层，单层)
# 这个用法目前回复乱七八糟
# def get_all_replies(comment):
#     all_replies = []
#     for reply in comment.replies:
#         all_replies.append(reply)
#         all_replies.extend(get_all_replies(reply))
#     return all_replies
#
# @app.route('/comment', methods=['GET', 'POST'])
# @login_required
# def comment():
#     if request.method == 'POST':
#         comment_content = request.form['comment']
#         parent_id = request.form.get('parent_id', None)
#         reply_to_username = request.form.get('reply_to_username', None)
#
#         # 确保parent_id是一个整数或者None
#         parent_id = int(parent_id) if parent_id else None
#
#         if parent_id and reply_to_username:
#             # 如果是回复，添加前缀
#             comment_content = f"{comment_content}"
#
#         new_comment = Comment(content=comment_content, user_id=current_user.id, parent_id=parent_id)
#         db.session.add(new_comment)
#         db.session.commit()
#
#     # 获取所有评论
#     all_comments = Comment.query.all()
#
#     return render_template('comments.html', comments=all_comments)


# 重置密码
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        email_code_input = request.form['email_code']
        new_password = request.form['new_password']

        if email_code_input == session.get('email_code'):
            user = User.query.filter_by(email=email).first()
            if user:
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('密码重置成功，请登录!')

                if not user.activities:
                    # 如果不存在则创建一个新的UserActivity实例
                    user_activity = UserActivity(user_id=user.id)
                    db.session.add(user_activity)
                else:
                    # 如果存在，则获取第一个UserActivity实例
                    user_activity = user.activities[0]
                last_password_change_utc = datetime.utcnow()
                # 定义本地时区
                local_tz = pytz.timezone('Asia/Shanghai')  # 对于中国标准时间
                # 将 UTC 时间转换为本地时间
                last_password_change_local = last_password_change_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
                user_activity.last_password_change = last_password_change_local
                db.session.commit()

                # 登出及加密
                session.pop('username', None)
                logout_user()  # 登出用户
                resp = make_response(redirect(url_for('login')))
                resp.set_cookie('jwt', '', expires=0, httponly=False, secure=True)  # 删除cookie
                return resp

            else:
                flash('用户不存在!')

    # return render_template('reset_password.html')
    return render_template('reset_passw.html')

# 重置密码模板
# @app.route('/verify_reset_email', methods=['GET', 'POST'])
# def verify_reset_email():
#     if request.method == 'POST':
#         email_code_input = request.form['email_code']
#         username = session.get('reset_username')
#
#         if email_code_input == session.get('email_code'):
#             # 重置密码逻辑
#             new_password = request.form['new_password']
#             user = User.query.filter_by(username=username).first()
#             if user:
#                 user.password_hash = hash_password(new_password)
#                 db.session.commit()
#                 flash('密码重置成功，请登录!')
#                 return redirect(url_for('login'))
#             else:
#                 flash('用户不存在!')
#         else:
#             flash('验证码错误!')
#
#     return render_template('verify_email.html')  # 创建重置邮箱验证的HTML模板


@app.route('/user/list')
@role_required('admin')
def user_list():
    users = User.query.all()
    user_data = []

    for user in users:
        roles = [f"{role.name}: {role.description}" for role in user.roles]
        activities = user.activities[0] if user.activities else None
        user_data.append({
            'username': user.username,
            'email': user.email,
            'create_time': user.create_time,
            'roles': ', '.join(roles),
            'last_login': activities.last_login if activities else None,
            'last_info_change': activities.last_info_change if activities else None,
            'last_password_change': activities.last_password_change if activities else None
        })

    return render_template('user_list.html', user_data=user_data)


@app.route('/captcha/<filename>')
def captcha(filename):
    return send_file(os.path.join('captcha', filename))

@app.route('/send_reset_email', methods=['POST'])
def send_reset_email():
    email = request.form['email']
    email_code = ''.join(random.choices(string.digits, k=6))
    send_email_verification(email, email_code)
    session['email_code'] = email_code
    return jsonify({'message': '验证码已发送!'})


# 个人信息
# @app.route('/api/profile', methods=['GET'])
# def get_profile():
#     user_id = session.get('user_id')
#     profile = UserProfile.query.filter_by(user_id=user_id).first()
#     if profile:
#         return jsonify({
#             'phone_number': profile.phone_number,
#             'gender': profile.gender,
#             'age': profile.age,
#             'industry': profile.industry,
#             'bio': profile.bio,
#             'interests': profile.interests,
#             'location': profile.location
#         })
#     else:
#         return jsonify({})
#
# @app.route('/api/profile', methods=['PUT'])
# def update_profile():
#     data = request.json
#     user_id = session.get('user_id')
#     profile = UserProfile.query.filter_by(user_id=user_id).first()
#     if profile:
#         profile.phone_number = data.get('phone_number')
#         profile.gender = data.get('gender')
#         profile.age = data.get('age')
#         profile.industry = data.get('industry')
#         profile.bio = data.get('bio')
#         profile.interests = data.get('interests')
#         profile.location = data.get('location')
#         db.session.commit()
#         return jsonify({'message': 'Profile updated successfully'})
#     else:
#         return jsonify({'message': 'Profile not found'}), 404

@app.route('/position')
@login_required
def position():
    return render_template('position.html')

@app.route('/3D_map')
@login_required
def three_d_map():
    # print(session['lng'], session['lat'])
    # lng, lat = session.get('lng', None), session.get('lat', None)
    # print(lng, lat)

    token = request.cookies.get('position')
    print("1111", token)
    if token:
        try:
            position_data = serializer.loads(token, salt='cookie-session', max_age=3600)
            print(position_data)
        except:
            position_data = None
    else:
        token = None

    if token and position_data:
        lng, lat = position_data['lng'], position_data['lat']
        return render_template('3D_map.html', lng=lng, lat=lat)
    return redirect(url_for('position'))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', error_message=str(e)), 404


@app.errorhandler(500)
def internal_error(e):
    # 传递错误信息到模板中
    return render_template('500.html', error_message=str(e)), 500


def ReverseGeocode(location):
    print(location)
    url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {'output': 'json',
              'location': location,
              'key': "c617d9f467708db4f7fd97f31a37adbd",
              'extensions': 'base',
              'roadlevel': '1',
              'poitype': '',}

    res = requests.get(url, params=params)
    print(res.json())
    try:
        data = res.json()['regeocode']
    except Exception:
        data = None
    return data

@app.route('/api/submit_location', methods=['POST'])
@cross_origin(supports_credentials=True)
def submit_location():
    print("current_user: ", vars(current_user))
    data = request.get_json()
    position = data.get('position')
    # print(position)
    user_id = current_user.id
    session['position'] = position
    # 因为添加了target="_blank"切换了标签页，新标签页不继承原标签页的session，无法实现跨标签互联
    lng = position['lng']
    lat = position['lat']

    Local_Data = ReverseGeocode(f"{lng},{lat}")
    print("Local_Data: ", Local_Data)
    # 详细地址
    local_area = Local_Data['formatted_address']
    country = Local_Data['addressComponent']['country']         # 国家
    province = Local_Data['addressComponent']['province']       # 省份
    city = Local_Data['addressComponent']['city']               # 城市
    district = Local_Data['addressComponent']['district']       # 区域
    township = Local_Data['addressComponent']['township']       # 街道/村落
    # 街道
    street = Local_Data['addressComponent']['streetNumber']['street'] + Local_Data['addressComponent']['streetNumber']['number']
    # print(street)

    # 详细地址
    description = f"{country}/{province}/{city}/{district}/{township}/{street}"
    # print(description)

    # 获取当前登录用户的UserActivity记录，或者创建一个新的
    user_activity = UserActivity.query.filter_by(user_id=user_id).first()
    if not user_activity:
        user_activity = UserActivity(user_id=user_id)
        db.session.add(user_activity)
    # 更新UserActivity记录
    user_activity.last_login_latitude = float(lat)
    user_activity.last_login_longitude = float(lng)
    user_activity.last_login_location = local_area
    user_activity.last_login_location_description = description
    # 提交数据库更改
    db.session.commit()


    # 序列化位置信息
    token = serializer.dumps(position, salt='cookie-session')
    # 创建响应对象并设置cookie
    response = make_response(jsonify({'status': 'success', 'message': 'Location received'}))
    response.set_cookie(
        'position',
        value=token,
        path='/',  # 确保cookie在所有路径下可用
        httponly=False,  # 提高安全性，防止JavaScript访问
        secure=True,  # 如果是HTTPS环境，请设置为True
        samesite='None',  # 本地环境运行通常使用Lax
        # domain='localhost'  # 仅在需要模拟跨子域共享时设置
        # samesite='None',  # 允许跨站请求携带cookie
        # domain='yourdomain.com'  # 如果需要跨子域共享，请设置domain属性
    )
    return response



@app.route('/api/Browser_Detection', methods=['POST'])
@cross_origin(supports_credentials=True)
def Browser_Detection():
    # data = request.get_json()
    data = request.json
    Browser = data.get('Browser_Detection')
    session['Browser_Detection'] = Browser
    print(session['Browser_Detection'])
    # 序列化JSON数据
    browser_json_str = json.dumps(Browser)
    # 创建响应
    resp = make_response(jsonify({'status': 'success', 'message': 'success'}), 200)
    # 设置cookie
    resp.set_cookie(
        'Browser_Detection',
        browser_json_str,
        samesite='None',  # 明确设置 SameSite 属性为 None
        secure=True,      # 确保 Secure 属性为 True（如果是 HTTPS 环境）
        path='/',
        httponly=False,
        domain='localhost',
    )
    return resp

@app.route('/login/api/private_text', methods=['GET', 'POST'])
def private_text():
    return render_template('private_text.html')

@app.route('/login/api/personal', methods=['GET', 'POST'])
def personal():
    return render_template('personal.html')

signal.signal(signal.SIGINT, save_data)  # 捕获 Ctrl+C
signal.signal(signal.SIGTERM, save_data)  # 捕获终止信号

if __name__ == '__main__':
    # db.create_all()
    # app.run(debug=True, ssl_context='adhoc')  # 使用自签名证书启动 HTTPS
    # *** https://www.ssleye.com/ssltool/self_sign.html ***
    # context = ('certificate.pem', 'private_key.pem')
    context = (r'C:\Users\yang\localhost.pem', r'C:\Users\yang\localhost-key.pem')
    # app.run(debug=True, ssl_context=context, port=443, host='0.0.0.0')
    app.run(debug=True, ssl_context=context, threaded=True, port=5036, host='0.0.0.0')

