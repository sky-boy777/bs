from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_caching import Cache

mail = Mail()  # 邮件
db = SQLAlchemy()  # 数据库
cache = Cache()  # 缓存
