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

    # 跟用户动态模型建立关系，不会在数据库生成字段
    dynamics = db.relationship('UserDynamicModel', backref='user')
    # 跟留言板模型建立关系
    messages = db.relationship('MessageBoardModel', backref='user')

    def __str__(self):
        '''魔法方法：打印输出用户名'''
        return self.username


class UserDynamicModel(BaseModel):
    '''用户动态模型'''
    __tablename__ = 'user_dynamic'
    # 内容
    content = db.Column(db.String(500))
    # 用户id，此条动态属于哪个用户
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 用法:user_dynamic.user.username

    # 跟用户动态图片集建立关系，不会在数据库生成字段
    images = db.relationship('UserDynamicImageModel', backref='user_dynamic')  # 用法：user_dynamic.images.image


class UserDynamicImageModel(BaseModel):
    '''用户动态图片集模型'''
    __tablename__ = 'user_dynamic_image'
    # 图片路径
    image = db.Column(db.String(255))

    # 外键，图片属于哪条动态
    dynamic_id = db.Column(db.Integer, db.ForeignKey('user_dynamic.id'), nullable=False)


class MessageBoardModel(BaseModel):
    '''留言板模型'''
    __tablename__ = 'message_board'
    content = db.Column(db.String(500), nullable=False)

    # 外键：用户id，此条留言属于哪个用户
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 用法:message_board.user.username