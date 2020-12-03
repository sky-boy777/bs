from flask import Blueprint, render_template, g, session
from .models import ScenicSpotsImagesModel, ScenicSpotsModel
from apps.user_app.models import UserModel


# 前台展示蓝图
main_bp = Blueprint('main', __name__)  # 前台展示蓝图，需要在create_app下注册

# 在这里定义视图
@main_bp.route('/', endpoint='index')
def index():
    '''首页'''
    # 如果用户已登录，查询用户
    uid = session.get('uid')
    user = UserModel.query.get(uid)

    # 查询数据

    return render_template('main/index.html', user=user)


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