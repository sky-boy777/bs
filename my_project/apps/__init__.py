from flask import Flask
import settings
from exts import db
from apps.main_app.views import main_bp  # 前台展示蓝图
from apps.user_app.views import user_bp  # 用户模块蓝图


def create_app():
    # 创建app，并且指定templates、static文件夹位置
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(settings)  # 加载配置文件
    db.init_app(app)  # 初始化数据库

    # 注册蓝图
    app.register_blueprint(main_bp)  # 前台展示蓝图
    app.register_blueprint(user_bp)  # 用户模块蓝图

    return app