from flask import render_template
from . import main


@main.errorhandler(404)
def not_found(e):
    return render_template('error/404.html', error_message=str(e)), 404


@main.errorhandler(500)
def internal_error(e):
    # 传递错误信息到模板中
    return render_template('error/500.html', error_message=str(e)), 500