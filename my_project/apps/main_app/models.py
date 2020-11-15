from exts import db
from datetime import datetime

# 父类，简化每个类都要加id步骤
class BaseModel(db.Model):
    '''父类模型'''
    __abstract__ = True  # 抽象模型，不会在数据库生成表
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


# 在这里创建模型
class ScenicSpots(BaseModel):
    '''景点模型'''
    __tablename__ = 'scenic_spots'

    # 景点名称，必填
    sname = db.Column(db.String(20), nullable=False)
    # 景点简介
    scontent = db.Column(db.Text, nullable=False)
    # 最近更新时间，strftime是str类型
    stime = db.Column(db.String(15), default=datetime.now().strftime('%Y/%m/%d'))
    # 封面图
    simage = db.Column(db.String(64))  # 存储的是图片路径

    # 跟景点图集表建立关系，删除景点时也删除对应的图片
    images = db.relationship('ScenicSpotsImages', backref='scenic_spots')


class ScenicSpotsImages(BaseModel):
    '''景点图集'''
    __tablename__ = 'scenic_spots_images'

    # 图片路径
    image = db.Column(db.String(64))
    # 上传时间
    upload_time = db.Column(db.String(15), default=datetime.now().strftime('%Y/%m/%d'))

    # 外键，景点id，图片属于哪个景点
    scenic_spots_id = db.Column(db.Integer, db.ForeignKey('scenic_spots.id'))
