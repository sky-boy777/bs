from exts import db
from apps.main_app.models import BaseModel  # 父模型
import random


def generate_random_str():
    '''生成随机用户名'''
    s = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOLKJHGFDSAZXCVBNM'
    random_str = ''
    for i in range(10):
        random_str += random.choice(s)
    return random_str


# 创建模型
class UserModel(BaseModel):
    '''用户模型'''
    __tablename__ = 'user'

    # 用户名
    username = db.Column(db.String(30), default='新用户' + generate_random_str(), nullable=False)
    # 邮箱，唯一，用来登录，找回密码等
    email = db.Column(db.String(255), nullable=False, unique=True)
    # 加密后的密码
    password = db.Column(db.String(128), nullable=False)
    # 用户头像，存图片路径
    icon = db.Column(db.String(255), default='/images/icon/icon.jpg')
    # 是否激活，默认未激活，需要邮箱激活
    is_activate = db.Column(db.Boolean, default=0, nullable=False)  # 0:False，1:True
    # 用户是否已销号，默认未销号，逻辑删除
    is_delete = db.Column(db.Boolean, default=0, nullable=False)
    # 是否超级用户（管理员）
    is_admin = db.Column(db.Boolean, default=0, nullable=False)

    def __str__(self):
        '''魔法方法：打印输出用户名'''
        return self.username
