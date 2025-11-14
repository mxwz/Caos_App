from flask import Blueprint, Flask

# 创建主蓝本
page = Blueprint('page', __name__)

from . import views, errors