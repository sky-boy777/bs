from flask import Blueprint, render_template, request, redirect
from apps.main_app.models import *


# 前台展示蓝图
main_bp = Blueprint('main', __name__)  # 前台展示蓝图，需要在create_app下注册

# 在这里定义视图
@main_bp.route('/', endpoint='index')
def index():
    '''首页'''
    # 查询首页简介数据
    try:
        index_brief_introduction = IndexBriefIntroductionModel.query.filter().first()
    except:
        return render_template('main/index.html')
    # 查询景点数据
    try:
        scenic_spots_list = ScenicSpotsModel.query.filter().all()
    except:
        return render_template('main/index.html')
    return render_template('main/index.html',
                           index_brief_introduction=index_brief_introduction,
                           scenic_spots_list=scenic_spots_list,
                           )


@main_bp.route('/scenic_spots_detail')
def scenic_spots_detail():
    '''景点详情页'''
    # 获取景点id
    sid = request.args.get('sid')
    if sid:
        try:
            item = ScenicSpotsModel.query.get(sid)
        except:
            return '数据加载失败'
        if item:
            return render_template('main/scenic_spots_detail.html', item=item)
    return redirect('/')


@main_bp.route('/info', endpoint='info')
def info():
    '''公告信息列表页'''
    # 页码
    p = int(request.args.get('page', 1))  # 页码要为整形
    # 查询数据库展示数据，分页
    try:
        info_list = InfoModel.query.filter().paginate(page=p, per_page=20, max_per_page=20)
        return render_template('main/info.html', info_list=info_list)
    except:
        return render_template('main/info.html')


@main_bp.route('/info_detail', endpoint='info_detail')
def info_detail():
    '''公告信息详情页'''
    # 获取id
    info_id = request.args.get('info_id')
    if info_id:
        try:
            item = InfoModel.query.get(info_id)
        except:
            return '数据加载失败'
        if item:
            return render_template('main/info_detail.html', item=item)
    return redirect('/')