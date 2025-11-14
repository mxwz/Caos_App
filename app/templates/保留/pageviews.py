import base64

from flask import session, render_template, flash, redirect, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField, FileField

from Models import UserProfile, User
from . import page
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))       # get基于主键查询，利用索引快速定位

@page.route('/home')
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
                           photo=base64.b64encode(user_profile.photo).decode('utf-8') if user_profile.photo else None,
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


@page.route('/input/update_profile', methods=['GET', 'POST'])
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
            if form.photo.data:
                user.profile.photo = form.photo.data.read()
        else:
            user.profile = UserProfile(
                user_id=user.id,
                bio=form.bio.data,
                phone_number=form.phone_number.data,
                gender=form.gender.data,
                age=form.age.data,
                industry=form.industry.data,
                interests=form.interests.data,
                location=form.location.data,
                photo=form.photo.data.read() if form.photo.data else None
            )
        db.session.commit()
        flash('个人信息已更新！', 'success')
        return redirect(url_for('home'))

    return render_template('home/update_profile.html', form=form, user=user, name=name, email=email)