import inspect
import os
import secrets
from datetime import timedelta
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_manager, login_required, current_user, login_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, make_response, \
    abort

# from ..app import create_app
# from ..app import main

basedir = os.path.abspath(os.path.dirname(__file__))
# basedir = os.path.abspath(__file__)
# BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(basedir, '.env'), override=True)


def print_calling_script():
    # 获取当前调用栈
    stack = inspect.stack()
    # 获取调用该函数的上一级调用栈信息
    caller_frame = stack[1]
    # 获取调用该函数的脚本文件名
    calling_script = caller_frame.filename
    # 打印调用该函数的脚本文件名
    print(f"Calling script: {calling_script}")


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(192)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.urandom(24).hex()
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_TYPE = os.environ.get("SESSION_TYPE")

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # 限制每个邮箱地址在一定时间内发送验证码的次数
    EMAIL_CODE_LIMIT = 5  # 每个邮箱5分钟内最多发送的验证码次数
    EMAIL_CODE_INTERVAL = timedelta(minutes=5)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    # ALLOWED_ORIGINS = ['http://127.0.0.1:5000', 'http://localhost:5000', 'https://127.0.0.1:5000',
    #                    'https://localhost:5000', ]
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    CAPTCHA_PATH = os.environ.get("CAPTCHA_PATH") or os.path.join(os.getcwd(), 'app', 'captcha')
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'head')
    DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY")


    @staticmethod
    def init_app(app):
        print("Initializing app for development environment")
        print_calling_script()



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
