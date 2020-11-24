from exts import db
from datetime import datetime

# 父类，简化每个类都要加id步骤
class BaseModel(db.Model):
    '''父类模型'''
    __abstract__ = True  # 抽象模型，不会在数据库生成表
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 创建时间，strftime是str类型
    create_time = db.Column(db.String(15), default=datetime.now().strftime('%Y-%m-%d'))


class ScenicSpotsModel(BaseModel):
    '''景点模型'''
    __tablename__ = 'scenic_spots'

    # 景点名称，必填
    name = db.Column(db.String(20), nullable=False)
    # 景点简介内容（富文本编辑器，图文），图片以<img src='...'>形式存放数据库
    content = db.Column(db.Text, nullable=False)
    # 封面图
    image = db.Column(db.String(64))  # 存储的是图片路径

    # 跟景点图集表建立关系，删除景点时也删除对应的图片
    images = db.relationship('ScenicSpotsImagesModel', backref='scenic_spots')


class ScenicSpotsImagesModel(BaseModel):
    '''景点图集模型'''
    __tablename__ = 'scenic_spots_images'

    # 图片路径
    image = db.Column(db.String(64))

    # 外键，景点id，图片属于哪个景点
    scenic_spots_id = db.Column(db.Integer, db.ForeignKey('scenic_spots.id'))


class InfoModel(BaseModel):
    '''公告信息模型'''
    __tablename__ = 'info'

    # 标题
    title = db.Column(db.String(64), nullable=False)
    # 内容（富文本编辑器，图文）
    content = db.Column(db.Text, nullable=False)