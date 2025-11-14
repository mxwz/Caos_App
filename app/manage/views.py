from flask import session, render_template, flash, redirect, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField, FileField
# 路径问题
from Models import User
from . import manage
from app import db, login_manager, role_required, admin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # get基于主键查询，利用索引快速定位


# 管理界面(界面文件(夹)不能以admin或者Admin等起名，会替换flask-admin的页面)
@manage.route('/')
@role_required('admin')
def management():
    user_count = User.query.count()
    role = f"{session['role_description']} {session['role']}"
    return render_template('Manager/index.html', username=session['username'], usercount=user_count, userrole=role)


# 数据可视化界面（数据大屏）
@manage.route('/DataV')
def datav():
    return render_template('DataV/index.html')


# 重定向flask-admin管理界面(需要放在管理界面)
@manage.route('/admin')
@role_required('admin')
def go_admin():
    return redirect(url_for('admin.index'))
