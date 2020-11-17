from flask import Blueprint, render_template
from .models import ScenicSpotsImagesModel, ScenicSpotsModel

# 前台展示蓝图
main_bp = Blueprint('main', __name__)  # 前台展示蓝图，需要在create_app下注册

# 在这里定义视图
@main_bp.route('/', endpoint='index')
def index():
    '''首页'''
    # 查询数据库展示

    return render_template('main/index.html')


@main_bp.route('/scenic_spots_detail', endpoint='scenic_spots_detail')
def scenic_spots_detail():
    '''景点详情页'''
    # 获取景点id
    # 查询数据库展示数据
    return 'ok'


@main_bp.route('/info', endpoint='info')
def info():
    '''公告信息'''
    # 查询数据库展示数据
    pass


@main_bp.route('/info_detail', endpoint='indo_detail')
def info_detail():
    '''公告信息详情页'''
    # 获取id
    # 查询数据库
    pass