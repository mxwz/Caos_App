import json
import logging
import os
import random
import string
import time
from datetime import datetime, timedelta
from pathlib import Path

# import bcrypt
# from flask_bcrypt import Bcrypt

from flask_sse import sse
from openai import OpenAI
import jwt
import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from captcha.image import ImageCaptcha
from flask_cors import cross_origin
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, make_response, \
    abort, current_app, Response, render_template_string, g
from flask_mail import Message
from flask_wtf import FlaskForm
from itsdangerous import URLSafeTimedSerializer
from openai.types.chat import ChatCompletionChunk
from sqlalchemy import or_
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from app import db, login_manager, role_required
# 路径问题
from Models import UserActivity, UserProfile, Role, Comment, User, Session as SessionModel, GPTConversation
from . import main
from app import mail

# 第一种加盐简单，第二种复杂
# from app import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.DEBUG)

# # 配置 APScheduler
# scheduler = BackgroundScheduler()
# def cleanup_expired_sessions():
#     with current_app.app_context():
#         expired_sessions = SessionModel.query.filter(SessionModel.expiry < datetime.utcnow()).all()
#         for session in expired_sessions:
#             db.session.delete(session)
#         db.session.commit()
#         print(f"Cleaned up {len(expired_sessions)} expired sessions.")
# # 添加定时任务，每小时执行一次
# scheduler.add_job(cleanup_expired_sessions, 'interval', day=1)
# scheduler.start()



# 哈希密码函数(如果用了werkzeug.security，则不需要使用以下两种)
# def hash_password(password):
#     # password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
#     # return password
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#
#
# # 验证密码
# def check_password(stored_password, provided_password):
#     # return bcrypt.check_password_hash(provided_password, stored_password)
#     return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


# 生成验证码图像
def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = ImageCaptcha()
    # 获取当前文件的绝对路径
    current_file_path = Path(__file__).resolve()
    # 获取当前文件的上一级目录
    parent_directory = current_file_path.parent.parent
    image_folder = parent_directory / 'captcha'
    image_file = os.path.join(str(image_folder), f"{captcha_text}.png")
    image.write(captcha_text, image_file)
    return captcha_text

"!警告：会出现错误的地方：MAIL_USE_SSL=False不能出现在.env里，无论设置什么都会被视为True，应该保持None"
"原文；https://cloud.tencent.com/developer/ask/sof/107832577"
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
    msg = Message('[混沌新城]邮箱验证码', sender=current_app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.html = html_body
    mail.send(msg)


def is_email_code_send_limit_exceeded(email):
    if 'email_send_counts' not in session:
        session['email_send_counts'] = {}

    send_counts = session['email_send_counts'].get(email, 0)
    last_send_time = session.get(f'{email}_last_send_time', None)

    if last_send_time and datetime.utcnow() - datetime.fromisoformat(last_send_time) < current_app.config[
        'EMAIL_CODE_INTERVAL']:
        send_counts += 1
    else:
        send_counts = 1
        session[f'{email}_last_send_time'] = datetime.utcnow().isoformat()

    session['email_send_counts'][email] = send_counts

    return send_counts > current_app.config['EMAIL_CODE_LIMIT']


def cleanup_folder(folder_path="captcha"):
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


@main.route('/')
def index():
    if 'username' in session:
        return render_template('main/index.html', username=session['username'], userid=session['user_id'], role=session['role'])
    return render_template('main/index.html')


@main.route('/update_session_id')
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


@main.route('/1234')
@login_required
def admin2():
    if not current_user.is_admin():
        abort(403)
    return 'Admin page'


@main.route('/rotate_session')
def rotate_session():
    # 删除旧的会话
    session.clear()
    # 创建一个新的会话ID
    session['session_id'] = os.urandom(24)
    return redirect(url_for('main.index'))


@main.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('main.login'))

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
            last_login_utc = datetime.utcnow()
            # 定义本地时区
            local_tz = pytz.timezone('Asia/Shanghai')  # 对于中国标准时间
            # 将 UTC 时间转换为本地时间
            last_login_local = last_login_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
            try:
                client_ip = request.remote_addr
                if not client_ip:
                    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            except Exception:
                client_ip = None
            if client_ip:
                user_activity.last_login_ip = client_ip
            user_activity.last_login = last_login_local
            db.session.commit()
            logging.debug("提交完毕！")

            # 删除当前会话的所有内容，防止会话劫持，但是会把之前的session全部删除
            # session.clear()

            role = Role.query.filter_by(user_id=user.id).first()

            session.permanent = True  # 设置会话为持久性
            session['username'] = user.username
            session['email'] = user.email
            session['user_id'] = user.id
            session['role'] = role.name
            session['role_description'] = role.description
            # remember参数用于保持登录状态
            # login_user(user)  # 登录用户
            login_user(user, remember=True)  # 登录用户
            flash('登录成功!')

            # if 'remember_me' in request.form:
            if 'automatic_login' in request.form:
                token = jwt.encode({
                    'user_id': user.id,
                    'exp': last_login_utc + timedelta(days=7)
                }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

                # 将令牌存储在cookie中
                # resp = make_response(redirect(url_for('main.index')))
                if session['role'] == 'user':
                    resp = make_response(redirect(url_for('main.index')))
                elif session['role'] == 'admin':
                    resp = make_response(redirect(url_for('manage.management')))
                # httponly和secure是https加密参数
                # secure = True确保cookie只能通过HTTPS传输，而httponly = True确保cookie不能通过客户端脚本访问
                resp.set_cookie('jwt', token, httponly=False, secure=False)
                resp.set_cookie('user_id', str(user.id), httponly=False, secure=False)  # 将 user.id 转换为字符串
                resp.set_cookie('username', user.username, httponly=False, secure=False)
                resp.set_cookie('email', user.email, httponly=False, secure=False)
                logging.debug("登陆成功")
                return resp
            # return redirect(url_for('main.index'))
            if session['role'] == 'user':
                return redirect(url_for('main.index'))
            elif session['role'] == 'admin':
                return redirect(url_for('manage.management'))
        # 用户不存在/密码错误
        else:
            flash('用户名或密码错误!')  # 为防止sql注入风险，不提示密码错误和账户不存在
        session['captcha_text'] = generate_captcha()
        # request.args.get('login_name', '')中从http://xxx/login.bat.html?login_name=获取数据，如果填写了则有，未填写则为''
        return redirect(url_for('main.login', username=request.args.get('login_name', '')))

    else:
        session['captcha_text'] = generate_captcha()
        if session.get('login_name'):
            username = session.get('login_name')
        else:
            username = ""
        return render_template('main/login.html', username=username)


@main.route('/register', methods=['GET', 'POST'])
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
            return render_template('main/register.html')
        existing_user_name = User.query.filter_by(username=username).first()
        if existing_user_name:
            flash('该用户名已存在，请使用其他用户名注册。')
            return render_template('main/register.html')

        if email_code_input == session.get('email_code') and 'email_sent_time' in session:
            email_sent_time = datetime.fromisoformat(session['email_sent_time'])
            if datetime.utcnow() - email_sent_time > timedelta(minutes=5):
                flash('验证码已过期，请重新发送!')
                # 清除过期的验证码和发送时间
                session.pop('email_code', None)
                session.pop('email_sent_time', None)
                return render_template('main/register.html')  # 重新显示注册表单
            # 检查是否超过了发送限制
            if is_email_code_send_limit_exceeded(email):
                flash('您已达到发送验证码的限制，请稍后再试。')
                return render_template('main/register.html')
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
            return redirect(url_for('main.login'))
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
        return redirect(url_for("main.register"))
    else:
        return render_template('main/register.html')


# 检测到页面刷新则执行
@main.route('/page-refreshed', methods=['POST'])
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


@main.route('/generate_captcha')
def generate_captcha_route():
    captcha_text = generate_captcha()
    return jsonify({'captcha_text': captcha_text})


# @main.route('/verify_email', methods=['GET', 'POST'])
# def verify_email():
#     if request.method == 'POST':
#         email_code_input = request.form['email_code']
#         username = session.get('temp_username')
#
#         if email_code_input == session.get('email_code'):
#             new_user = User(username=username, password_hash=generate_password_hash(request.form['password']))
#             db.session.add(new_user)
#             db.session.commit()
#             flash('注册成功，请登录!')
#             return redirect(url_for('main.login'))
#         else:
#             flash('验证码错误!')
#
#     return render_template('main/verify_email.html')


# 只实现了永久性且一次性的注册验证码
@main.route('/send_email', methods=['POST'])
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
        main.logger.error(f'Failed to send email verification: {e}')
        return jsonify({'message': '发送验证码时出错，请稍后再试。'}), 500  # 500 Internal Server Error


@main.route('/logout')
@login_required  # 新
def logout():
    session.pop('username', None)
    logout_user()  # 登出用户
    flash('您已成功登出!')
    # return redirect(url_for('index'))

    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('jwt', '', expires=0, httponly=False, secure=False)  # 删除cookie
    return resp


@main.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    """
    添加评论的路由处理函数。

    1. 从请求表单中获取评论内容。
    2. 创建一个新的 Comment 对象，并设置其内容和用户ID。
    3. 将新的评论对象添加到数据库会话中。
    4. 提交数据库会话以保存更改。
    5. 使用 flash 函数显示一条成功消息。
    6. 重定向到评论页面。

    :return: 重定向到评论页面
    """
    content = request.form.get('content')
    comment = Comment(content=content, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    flash('评论已发表！', 'success')
    return redirect(url_for('main.comment'))

@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    删除评论的路由处理函数。

    1. 从数据库中查询指定ID的评论对象。
    2. 检查评论是否属于当前用户，如果不是则显示未经授权的消息并重定向。
    3. 从数据库会话中删除评论对象。
    4. 提交数据库会话以保存更改。
    5. 使用 flash 函数显示一条成功消息。
    6. 重定向到评论页面。

    :param comment_id: 要删除的评论ID
    :return: 重定向到评论页面
    """
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash('未经授权的操作！', 'danger')
        return redirect(url_for('main.comment'))
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除！', 'success')
    return redirect(url_for('main.comment'))


@main.route('/add_reply/<int:comment_id>', methods=['POST'])
@login_required
def add_reply(comment_id):
    """
    添加回复的路由处理函数。

    1. 从请求表单中获取回复内容。
    2. 创建一个新的 Comment 对象，并设置其内容、用户ID和父评论ID。
    3. 将新的回复对象添加到数据库会话中。
    4. 提交数据库会话以保存更改。
    5. 使用 flash 函数显示一条成功消息。
    6. 重定向到评论页面。

    :param comment_id: 父评论的ID
    :return: 重定向到评论页面
    """
    content = request.form.get('reply_content')
    reply = Comment(content=content, user_id=current_user.id, parent_id=comment_id)
    db.session.add(reply)
    db.session.commit()
    flash('回复已发表！', 'success')
    return redirect(url_for('main.comment'))

@main.route('/delete_reply/<int:reply_id>', methods=['POST'])
@login_required
def delete_reply(reply_id):
    """
    删除回复的路由处理函数。

    1. 从数据库中查询指定ID的回复对象。
    2. 检查回复是否属于当前用户，如果不是则显示未经授权的消息并重定向。
    3. 从数据库会话中删除回复对象。
    4. 提交数据库会话以保存更改。
    5. 使用 flash 函数显示一条成功消息。
    6. 重定向到评论页面。

    :param reply_id: 要删除的回复ID
    :return: 重定向到评论页面
    """
    reply = Comment.query.get_or_404(reply_id)
    if reply.user_id != current_user.id:
        flash('未经授权的操作！', 'danger')
        return redirect(url_for('main.comment'))
    db.session.delete(reply)
    db.session.commit()
    flash('回复已删除！', 'success')
    return redirect(url_for('main.comment'))


@main.route('/comment')
@login_required
def comment():
    """
    显示评论的路由处理函数。

    1. 从数据库中查询所有顶级评论（即没有父评论的评论）。
    2. 渲染评论模板，并传递评论列表给模板。

    :return: 渲染后的评论页面
    """
    comments = Comment.query.filter_by(parent_id=None).all()
    return render_template('comment/comments.html', comments=comments)

@main.route('/reset_password', methods=['GET', 'POST'])
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
                resp = make_response(redirect(url_for('main.login')))
                resp.set_cookie('jwt', '', expires=0, httponly=False, secure=False)  # 删除cookie
                return resp

            else:
                flash('用户不存在!')

    # return render_template('reset_password.html')
    return render_template('main/reset_passw.html')

# def reorder_messages(messages):
#     system_message = None
#     user_message = None
#     assistant_messages = []
#
#     for message in messages:
#         if message['role'] == 'system':
#             system_message = message
#         elif message['role'] == 'user':
#             user_message = message
#         elif message['role'] == 'assistant':
#             assistant_messages.append(message)
#
#     # 构建新的消息列表
#     reordered_messages = []
#     if system_message:
#         reordered_messages.append(system_message)
#     if user_message:
#         reordered_messages.append(user_message)
#     reordered_messages.extend(assistant_messages)
#
#     return reordered_messages


@main.route('/user/list')
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

    return render_template('else/user_list.html', user_data=user_data)


# 定义ask_gpt函数，输入问题，返回GPT的回答
def ask_gpt_v3(question, user_id, api_key, questions, role="helpful assistant"):
    print(f"user_{user_id}正在与GPT对话...")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    if questions:
        messages = [
            {
                "role": "assistant",
                "content": conv.question
            }
            for conv in questions
        ]
    else:
        messages = []

    if any("system" in message["role"] for message in messages):
        pass
    else:
        messages.append({"role": "system", "content": f"You are a {role}"})

    messages.append({"role": "user", "content": f"{question}"})
    print(messages)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=1024,                        # 最大输出长度和token消耗量
        temperature=0.7,                        # 随机性(采样温度，高随机低准确)
        stream=True,                            # 流式输出
    )
    # 非流式输出
    # result = response.choices[0].message.content
    # 流式
    for chunk in response:
        if isinstance(chunk, ChatCompletionChunk):
            # print("chunk是", chunk)
            for choice in chunk.choices:
                delta = choice.delta
                if delta and delta.content:
                    content = delta.content
                    # print("content是", content)
                    yield f"data: {content}\n\n"  # SSE 格式
        elif chunk.strip() == "data: [DONE]":
            break  # 结束标志，停止处理




# 定义ask_gpt函数，输入问题，返回GPT的回答
def ask_gpt_r1(question, user_id, api_key, questions, role="helpful assistant"):
    print(f"user_{user_id}正在与GPT对话...")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    messages = [{"role": "user", "content": f"{question}"}]
    # messages.append({"role": "user", "content": f"{question}"})

    if questions:
        messages.append([
            {
                "role": "assistant",
                "content": conv.question
            }
            for conv in questions
        ])

    # else:
    #     messages = []

    # if any("system" in message["role"] for message in messages):
    #     pass
    # else:
    #     messages.append({"role": "system", "content": f"You are a {role}"})

    # messages.append({"role": "user", "content": f"{question}"})
    reordered_messages = reorder_messages(messages)
    print(reordered_messages)
    response = client.chat.completions.create(
        model="deepseek-reasoner",                  # deepseek-chat为V3，deepseek-reasoner为R1
        messages=reordered_messages,
        max_tokens=1024,                        # 最大输出长度和token消耗量
        temperature=0.7,                        # 随机性(采样温度，高随机低准确)
        stream=True,                            # 流式输出
    )
    # 非流式输出
    # result = response.choices[0].message.content
    # 流式
    for chunk in response:
        if isinstance(chunk, ChatCompletionChunk):
            # print("chunk是", chunk)
            for choice in chunk.choices:
                delta = choice.delta
                if delta and delta.content:
                    content = delta.content
                    # print("content是", content)
                    yield f"data: {content}\n\n"  # SSE 格式
        elif chunk.strip() == "data: [DONE]":
            break  # 结束标志，停止处理



def ask_BDgpt_r1(question, user_id, api_key, questions, role="helpful assistant", gptsql=None):
    print(f"user_{user_id}正在与GPT对话...")
    client = OpenAI(
        base_url='https://qianfan.baidubce.com/v2',
        api_key='bce-v3/ALTAK-Q4DPopGoxOy7CJlZjHVzI/e98b5f7b8a59b33f49c9ad30412184f4606fd84c'
    )
    messages = []
    if (bool(questions) and bool(questions[0].answer)):
        messages.append([
            {
                "role": "user",
                "content": conv.question
            }
            for conv in questions
        ])
        messages.append([
            {
                "role": "assistant",
                "content": conv.answer_reasoning
            }
            for conv in questions
        ])
        messages.append([
            {
                "role": "assistant",
                "content": conv.answer
            }
            for conv in questions
        ])
    # print(messages)
    messages.append({"role": "user", "content": f"{question}"})

    # print(messages)
    chat_completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=messages,
        stream=True,
        stream_options={
            "include_usage": True,
        },
        max_tokens=8192,
        temperature=0.7,
        top_p=0.9,
    )

    global response, reresponse_reasoning
    response = ""
    response_reasoning = ""
    reasoning_button = False
    usage_info = None
    start_time_reasoning = None
    end_time_reasoning = None
    start_time_content = None
    end_time_content = None

    for chunk in chat_completion:
        for choice in chunk.choices:
            if choice.delta.reasoning_content:
                if not reasoning_button:
                    # 添加深度思考提示语
                    yield f"data: {json.dumps({'reasoning_content': '深度思考：'})}\n\n"
                    reasoning_button = True
                if start_time_reasoning is None:
                    start_time_reasoning = chunk.created  # 记录第一条reasoning_content的创建时间
                    print(start_time_reasoning)

                response_reasoning += choice.delta.reasoning_content
                # yield f"data: {choice.delta.reasoning_content}\n\n"  # SSE 格式
                yield f"data: {json.dumps({'reasoning_content': choice.delta.reasoning_content})}\n\n"
            if choice.delta.content:
                if start_time_content is None:
                    end_time_reasoning = time.time()
                    print(end_time_reasoning)
                    start_time_content = chunk.created  # 记录第一条content的创建时间
                    print(start_time_content)

                response += choice.delta.content
                # yield f"data: {choice.delta.content}\n\n"  # SSE 格式
                yield f"data: {json.dumps({'content': choice.delta.content})}\n\n"
        if chunk.usage:
            usage_info = chunk.usage

        # yield "data: [DONE]\n\n"
        # yield "data: {\"data\": \"[DONE]\"}\n\n"

    # # 检查是否存在相应的GPT对话记录
    # conversation = GPTConversation.query.filter_by(user_id=user_id, question=question).first()
    # if conversation:
    #     # 如果记录存在，更新记录
    #     conversation.answer_reasoning = response_reasoning  # 假设 content 是最终的回答
    #     conversation.answer = response  # 假设 content 是最终的回答
    #     db.session.add(conversation)
    #     db.session.commit()
    end_time_content = time.time()
    print(end_time_content)

    duration_reasoning = end_time_reasoning - start_time_reasoning
    duration_content = end_time_content - start_time_content

    if usage_info:
        # 返回token消耗信息
        usage_str = (
            f"回答消耗token:     {usage_info.completion_tokens}\n"
            f"回答消耗时间:       {duration_content:.2f} 秒\n"
            f"提示词消耗token:    {usage_info.prompt_tokens}\n"
            f"总计消耗token:     {usage_info.total_tokens}\n"
            f"思考消耗token:     {usage_info.completion_tokens_details.reasoning_tokens}\n"
            f"思考消耗时间:       {duration_reasoning:.2f} 秒\n"
        )
        yield f"data: {json.dumps({'usage': usage_str})}\n\n"

    yield "data: {\"data\": \"[DONE]\"}\n\n"


@main.route('/gpt', methods=['GET', 'POST'])
@login_required
def gpt():
    if request.method == 'POST':
        user_id = session['user_id']
        question = request.json['question']  # 获取POST请求中的question字段

        # 检查是否存在相应的GPT对话记录
        conversation = GPTConversation.query.filter_by(user_id=user_id, question=question).first()
        if conversation:
            # 如果记录存在，更新记录
            # conversation.answer = question  # 假设 content 是最终的回答
            conversation.question = question
        else:
            # 如果记录不存在，创建新的记录
            conversation = GPTConversation(user_id=user_id, question=question)
        db.session.add(conversation)
        db.session.commit()

        questions = GPTConversation.query.filter_by(user_id=user_id).all()
        return Response(ask_BDgpt_r1(question, user_id, current_app.config['DEEPSEEK_KEY'], questions, role="helpful assistant", gptsql=conversation), mimetype='text/event-stream')
    else:
        return render_template('main/gpt.html')  # 返回模板页

@main.route('/gpt/stream', methods=['GET'])
def gpt_stream():
    user_id = session['user_id']
    question = request.args.get('question')

    questions = GPTConversation.query.filter_by(user_id=user_id).all()
    return Response(ask_BDgpt_r1(question, user_id, current_app.config['DEEPSEEK_KEY'], questions), mimetype='text/event-stream')



@main.route('/captcha/<filename>')
def captcha(filename):
    return send_file(os.path.join('captcha', filename))


@main.route('/send_reset_email', methods=['POST'])
def send_reset_email():
    email = request.form['email']
    email_code = ''.join(random.choices(string.digits, k=6))
    send_email_verification(email, email_code)
    session['email_code'] = email_code
    return jsonify({'message': '验证码已发送!'})


@main.route('/position')
@login_required
def position():
    userid = current_user.id
    return render_template('map/position.html', userid=userid)





@main.route('/3D_map')
@login_required
def three_d_map():
    # 查询用户最后的登录活动记录
    activity = UserActivity.query.filter_by(user_id=current_user.id).order_by(UserActivity.last_login.desc()).first()
    latitude = activity.last_login_latitude,
    longitude = activity.last_login_longitude,
    lng, lat = longitude, latitude
    return render_template('map/3D_map.html', lng=lng, lat=lat)

# 通过经纬度获取位置
def ReverseGeocode(location):
    # print(location)
    url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {'output': 'json',
              'location': location,
              'key': "c617d9f467708db4f7fd97f31a37adbd",
              'extensions': 'base',
              'roadlevel': '1',
              'poitype': '', }

    res = requests.get(url, params=params)
    # print(res.json())
    try:
        data = res.json()['regeocode']
    except Exception:
        data = None
    return data


@main.route('/api/submit_location', methods=['POST'])
@cross_origin(supports_credentials=True)
def submit_location():
    data = request.get_json()
    position = data.get('position')
    # print(position)
    user_id = data.get('user_id')
    # print(user_id)
    session['position'] = position
    # 因为添加了target="_blank"切换了标签页，新标签页不继承原标签页的session，无法实现跨标签互联
    lng = position['lng']
    lat = position['lat']

    Local_Data = ReverseGeocode(f"{lng},{lat}")
    # print("Local_Data: ", Local_Data)
    # 详细地址
    local_area = Local_Data['formatted_address']
    country = Local_Data['addressComponent']['country']  # 国家
    province = Local_Data['addressComponent']['province']  # 省份
    city = Local_Data['addressComponent']['city']  # 城市
    district = Local_Data['addressComponent']['district']  # 区域
    township = Local_Data['addressComponent']['township']  # 街道/村落
    # 街道
    street = Local_Data['addressComponent']['streetNumber']['street'] + Local_Data['addressComponent']['streetNumber'][
        'number']
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

    return jsonify({'status': 'success', 'message': 'Location received'})


@main.route('/api/Browser_Detection', methods=['POST'])
@cross_origin(supports_credentials=True)
def Browser_Detection():
    data = request.get_json()
    Browser = data.get('Browser_Detection')
    User_id = data.get('user_id')
    # print(data)
    # session['Browser_Detection'] = Browser
    # print(session['Browser_Detection'])

    user_activity = UserActivity.query.filter_by(user_id=User_id).first()

    device = Browser['平台类型']  # 设备信息

    user_activity.last_login_device = device
    user_activity.last_device_info = Browser
    db.session.commit()
    # # 序列化JSON数据
    # browser_json_str = json.dumps(Browser)
    #
    # # 创建响应
    # resp = make_response(jsonify({'status': 'success', 'message': 'success'}), 200)
    #
    # # 设置cookie
    # resp.set_cookie(
    #     'Browser_Detection',
    #     browser_json_str,
    #     samesite='None',  # 明确设置 SameSite 属性为 None
    #     secure=True,  # 确保 Secure 属性为 True（如果是 HTTPS 环境）
    #     path='/',
    #     httponly=False,
    # )
    #
    # return resp
    return jsonify({'status': 'success', 'message': 'success'})


@main.route('/login/api/private_text', methods=['GET', 'POST'])
def private_text():
    return render_template('main/private_text.html')


@main.route('/login/api/personal', methods=['GET', 'POST'])
def personal():
    return render_template('main/personal.html')

@main.route('/EMOFALL')
def run_gradio_iface_all():
    """
    弃置

    :return:
    """
    from gradio_pro.car.lane_gradio import iface_all
    # iface_all.launch(share=False, show_error=True, show_api=False, server_port=5034,
    #                  quiet=True, inbrowser=False, prevent_thread_lock=True, inline=True)


@main.route('/LANE')
def run_gradio_iface():
    """
    弃置

    :return:
    """
    from gradio_pro.car.lane_gradio import iface
    # iface.launch(share=False, show_error=True, show_api=False, debug=True, server_port=5035,
    #              quiet=True, inbrowser=False, prevent_thread_lock=True, inline=True)



import requests
from bs4 import BeautifulSoup

def ai_news():
    """
    新闻资讯爬取

    :return:
    :return-type: json
    """
    headers = {
        "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    }

    head_url = "https://www.aitntnews.com"

    res = requests.get(
        "https://www.aitntnews.com/newList.html?typeId=1",
        headers=headers,
    )

    news_data = []

    soup = BeautifulSoup(res.text, "html.parser")
    # news_list = soup.select(".news-list > li")
    news_list = soup.find_all("article", class_="news-item")
    for news in news_list:
        header = news.find("div", class_="new-head")
        title = header.find("a").text
        url = head_url + header.find("a")["href"]
        p_text = news.find_all("p")
        keyword = ''.join(p_text[0].text.split('\n'))
        news_text = p_text[1].text

        news_data.append({
            "title": title,
            "url": url,
            "keyword": keyword,
            "news_text": news_text,
        })
    return news_data


@main.route('/newspaper')
def newspaper():
    time.sleep(1)
    news_data = ai_news()
    return render_template('main/news.html', news_data=news_data)



@main.route('/api/delete_gptepoch/<int:user_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@login_required
def delete_gptepoch(user_id):
    """
    删除GPT对话记录的API路由处理函数。

    1. 从数据库中查询所有指定用户的GPT对话记录对象。
    2. 检查这些对话记录是否属于当前用户，如果不是则返回未授权的响应。
    3. 从数据库会话中删除这些对话记录对象。
    4. 提交数据库会话以保存更改。
    5. 返回删除成功的响应。

    :param user_id: 要删除的GPT对话记录所属的用户ID
    :return: JSON响应
    """
    conversations = GPTConversation.query.filter_by(user_id=user_id).all()

    if not all(conversation.user_id == current_user.id for conversation in conversations):
        return jsonify({'message': '未经授权的操作！'}), 403  # 403 Forbidden

    for conversation in conversations:
        db.session.delete(conversation)

    db.session.commit()
    flash("对话已删除")
    return jsonify({'message': '所有对话记录已删除！'})


