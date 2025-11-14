from flask import Blueprint

# 创建主蓝本
manage = Blueprint('manage', __name__)


from . import views, errors
