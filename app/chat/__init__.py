from flask import Blueprint

# 创建主蓝本
# main = Blueprint('main', __name__, static_folder='static', template_folder='templates')
chat = Blueprint('chat', __name__)

from . import views, errors
