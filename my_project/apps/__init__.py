from flask import Flask
import settings  # 配置文件
from exts import db
from apps.main_app.views import main_bp  # 前台展示蓝图
from apps.user_app.views import user_bp  # 用户模块蓝图
from flask_wtf.csrf import CsrfProtect  # 全局csrf
from exts import mail  # 邮件

csrf = CsrfProtect()


def create_app():
    # 创建app，并且指定templates、static文件夹位置
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(settings)  # 加载配置文件

    db.init_app(app)  # 初始化数据库
    csrf.init_app(app)  # 初始化全局csrf
    mail.init_app(app)  # 初始化发送邮件类

    # 注册蓝图
    app.register_blueprint(main_bp)  # 前台展示蓝图
    app.register_blueprint(user_bp)  # 用户模块蓝图

    return app