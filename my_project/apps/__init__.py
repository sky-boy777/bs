from flask import Flask
import settings  # 配置文件
from apps.main_app.views import main_bp  # 前台展示蓝图
from apps.user_app.views import user_bp  # 用户模块蓝图
from apps.admin_app.views import admin_bp  # 后台管理蓝图
from flask_wtf.csrf import CsrfProtect  # 全局csrf
from exts import db, mail, cache  # 数据库，邮件，缓存

csrf = CsrfProtect()


def create_app():
    # 创建app，并且指定templates、static文件夹位置
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(settings)  # 加载配置文件

    db.init_app(app)  # 初始化数据库
    csrf.init_app(app)  # 初始化全局csrf
    mail.init_app(app)  # 初始化发送邮件类
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})  # 初始化缓存，简单缓存

    # 注册蓝图
    app.register_blueprint(main_bp)  # 前台展示蓝图
    app.register_blueprint(user_bp)  # 用户模块蓝图
    app.register_blueprint(admin_bp)  # 后台管理蓝图

    return app