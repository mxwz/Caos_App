import base64
import os

from flask import session, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField, FileField
# 路径问题
from Models import UserProfile, User
from . import page
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))       # get基于主键查询，利用索引快速定位

@page.route('/')
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

    return render_template('home/home.html',
                           email=email,
                           username=user_name,
                           phone_number=user_profile.phone_number,
                           gender=user_profile.gender,
                           age=user_profile.age,
                           industry=user_profile.industry,
                           bio=user_profile.bio,
                           interests=user_profile.interests,
                           location=user_profile.location,
                           photo=user_profile.photo
    )


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
    photo = FileField('头像')
    submit = SubmitField('提交')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@page.route('/input/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user_id = session.get('user_id')
    name = session.get('username')
    email = session.get('email')

    user = User.query.get_or_404(user_id)
    form = UserProfileForm(obj=user.profile)

    if form.validate_on_submit():
        photo = request.files.get('photo')
        if user.profile:
            user.profile.bio = form.bio.data or user.profile.bio
            user.profile.phone_number = form.phone_number.data or user.profile.phone_number
            user.profile.gender = form.gender.data or user.profile.gender
            user.profile.age = form.age.data or user.profile.age
            user.profile.industry = form.industry.data or user.profile.industry
            user.profile.interests = form.interests.data or user.profile.interests
            user.profile.location = form.location.data or user.profile.location

            # 处理头像上传
            if photo and photo.filename != '':
            # if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_extension = os.path.splitext(filename)[1]  # 获取文件后缀
                    file_to_name = f"{user_id}{file_extension}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_to_name)
                    file.save(file_path)
                    user.profile.photo = file_to_name
                else:
                    flash('无效的文件格式，请上传有效的图片文件。', 'danger')
                    return redirect(url_for('page.update_profile'))

        else:
            # 处理头像上传
            if photo and photo.filename != '':
            # if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_extension = os.path.splitext(filename)[1]  # 获取文件后缀
                    file_to_name = f"{user_id}{file_extension}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_to_name)
                    file.save(file_path)
                    photo = file_to_name
                else:
                    photo = None
                    flash('无效的文件格式，请上传有效的图片文件。', 'danger')
                    return redirect(url_for('page.update_profile'))
            else:
                photo = None

            user.profile = UserProfile(
                user_id=user.id,
                bio=form.bio.data or '',
                phone_number=form.phone_number.data or '',
                gender=form.gender.data or '',
                age=form.age.data or None,
                industry=form.industry.data or '',
                interests=form.interests.data or '',
                location=form.location.data or '',
                photo=photo
            )
        db.session.commit()
        flash('个人信息已更新！', 'success')
        return redirect(url_for('page.home'))

    return render_template('home/update_profile.html', form=form, user=user, name=name, email=email)