from flask import redirect, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, EmailField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_admin.contrib.sqla import ModelView


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
    column_list = ('id', 'username', 'email', 'create_time')
    column_searchable_list = ('username', 'email')
    column_filters = ('username', 'email', 'create_time')
    form_excluded_columns = ('password_hash', 'create_time')

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
        'id', 'user_id', 'last_login', 'last_info_change', 'last_password_change',
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
