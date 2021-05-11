import os

# DEBUG = True
# ENV = 'development'  # 开发环境

ENV = 'production'  # 生产环境：production
DEBUG = False

# 数据库
#                          数据库+驱动       用户  密码  主机      端口号 数据库名
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@127.0.0.1:3306/my_project'

# 主机地址（发邮件需要用到），部署时改成服务器的地址
LOCALHOST = '127.0.0.1:8000'

# 缓存配置
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://@localhost:6379/1'


SECRET_KEY = 'kdfuiefjk434348952fdhfueybdfhue-s&fkjksjfkdsf'

# 上传文件大小限制200M，全局，因为一次会上传多个文件
MAX_CONTENT_LENGTH = 200 * 1024 * 1024

SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不追踪对象，减少内存开销，默认为True
SQLALCHEMY_ECHO = True  # 记录所有 发到标准输出(stderr)的语句，这对调试很有帮助。


# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')  # 将window系统生成的路径\替换为/
# 静态文件路径
STATIC_DIR = os.path.join(BASE_DIR, 'static').replace('\\', '/')
# 模板路径
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
# 景点封面路径
SCENIC_SPOT_DIR = os.path.join(BASE_DIR, 'static/images/scenic_spot').replace('\\', '/')
# 景点图集路径
SCENIC_SPOT_IMAGES_DIR = os.path.join(BASE_DIR, 'static/images/scenic_spot_images').replace('\\', '/')
# 头像图片文件路径
UPLOAD_ICON_DIR = os.path.join(BASE_DIR, 'static/images/icon').replace('\\', '/')
# 轮播图路径
UPLOAD_BANNER_DIR = os.path.join(BASE_DIR, 'static/images/banner').replace('\\', '/')
# 用户发布动态图片上传路径
UPLOAD_USER_DYNAMIC_IMAGE = os.path.join(BASE_DIR, 'static/images/upload_user_dynamic_image/').replace('\\', '/')

# 发送邮件配置
MAIL_DEFAULT_SENDER = '旅游景点自助系统<bycwql@163.com>'  # 显示发件人
MAIL_SERVER = 'smtp.163.com'  # smtp服务的邮箱服务器， 如果是 qq 改成 smtp.qq.com
MAIL_USERNAME = 'bycwql@163.com'  # 发送邮件的邮箱
MAIL_PASSWORD = 'JBRHBAFRQNGZTPHP'  # 开启SMTP后的客户端授权码
MAIL_USE_SSL = True
MAIL_PORT = 465  # SMTP端口需要SSL