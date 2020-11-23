import os

DEBUG = True
ENV = 'development'  # 开发环境，上线部署使用生产环境：production

# 数据库
#                          数据库+驱动       用户  密码  主机      端口号 数据库名
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@127.0.0.1/my_project'

SECRET_KEY = 'kdfuiefjk4343424@&&$^@&$@&$&@^$&fkjksjfkdsf'

SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不追踪对象，减少内存开销，默认为True
SQLALCHEMY_ECHO = True  # 记录所有 发到标准输出(stderr)的语句，这对调试很有帮助。


# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')  # 将window系统生成的路径\替换为/
# 静态文件路径
STATIC_DIR = os.path.join(BASE_DIR, 'static').replace('\\', '/')
# 模板路径
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
# 上传文件路径
# UPLOAD_DIR = os.path.join(BASE_DIR, 'static/upload').replace('\\', '/')
# 头像图片文件路径
# UPLOAD_ICON_DIR = os.path.join(BASE_DIR, 'static/upload/icon').replace('\\', '/')
