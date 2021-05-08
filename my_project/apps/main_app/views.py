from flask import Blueprint, render_template, request, redirect, g, url_for, session
from apps.main_app.models import *
import os
import uuid
import settings
from apps.user_app.forms import UserAddDynamicForm, MessageBoradForm
from apps.user_app.models import *
from exts import cache
from math import ceil
from sqlalchemy import func

# 前台展示蓝图
main_bp = Blueprint('main', __name__)  # 前台展示蓝图，需要在create_app下注册

@main_bp.route('/', endpoint='index')
def index():
    '''首页'''
    # 先从缓存中获取数据，没有则到数据库查找，并更新缓存
    index_brief_introduction = cache.get('index_brief_introduction')
    scenic_spots_list = cache.get('scenic_spots_list')
    image_list = cache.get('image_list')

    # 查询首页简介数据
    if not index_brief_introduction:
        try:
            index_brief_introduction = IndexBriefIntroductionModel.query.filter().first()
            cache.set('index_brief_introduction', index_brief_introduction, timeout=60*60)  # 1小时
        except:
            index_brief_introduction = None

    # 查询景点数据
    if not scenic_spots_list:
        try:
            scenic_spots_list = ScenicSpotsModel.query.filter().all()
            cache.set('scenic_spots_list', scenic_spots_list, timeout=1800)  # 30分钟
        except:
            scenic_spots_list = None

    # 轮播图
    if not image_list:
        try:
            image_list = BannerModel.query.filter().all()
            cache.set('image_list', image_list, timeout=60*60*24*7)  # 7天
        except:
            image_list = None
    return render_template('main/index.html',
                           index_brief_introduction=index_brief_introduction,
                           scenic_spots_list=scenic_spots_list,
                           image_list=image_list
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


@main_bp.route('/scenic_spots')
def scenic_spots():
    '''景点列表页'''
    # 页码
    try:
        p = int(request.args.get('page', 1))  # 页码要为整形
    except:
        p = 1

    # 每页条数
    per_page = 15

    # count = ScenicSpotsModel.query.count()  # 会生成子查询
    # SELECT count(scenic_spots.id) AS count_1 FROM scenic_spots
    count = db.session.query(func.count(ScenicSpotsModel.id)).scalar()

    # 总页数，上一页，下一页，还有景点列表
    pages = ceil(count/per_page)
    if not 0 < p <= pages:
        p = 1
    prev_num = p-1
    next_num = p+1
    try:
        scenic_spots_list = ScenicSpotsModel.query.order_by(-ScenicSpotsModel.id).offset((p-1)*per_page).limit(per_page)
    except:
        return render_template('main/scenic_spots.html')
    return render_template('main/scenic_spots.html',
                           scenic_spots_list=scenic_spots_list,
                           pages=pages,
                           prev_num=prev_num,
                           next_num=next_num,
                           page=p
                           )


@main_bp.route('/info', endpoint='info')
def info():
    '''公告信息列表页'''
    # 页码
    try:
        p = int(request.args.get('page', 1))  # 页码要为整形
    except:
        p = 1
    # 查询数据库展示数据，分页
    try:
        info_list = InfoModel.query.order_by(-InfoModel.id).paginate(page=p, per_page=15)
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
            # 查询是否有session缓存
            if session.get('info_id'+str(info_id)) == info_id:
                return render_template('main/info_detail.html', item=item)
            # 设置session记录浏览标记
            session['info_id'+str(info_id)] = info_id
            item.num += 1  # 浏览量加1
            try:
                db.session.commit()
            except:
                return render_template('main/info_detail.html', item=item)
            return render_template('main/info_detail.html', item=item)
    return redirect(url_for('main.info'))


@main_bp.route('/attractions_map')
def attractions_map():
    '''景点地图'''
    return render_template('main/attractions_map.html')


@main_bp.route('/user_dynamic', methods=['GET', 'POST'])
def user_dynamic():
    '''用户动态'''
    form = UserAddDynamicForm()
    # 页码
    try:
        p = int(request.args.get('page', 1))  # 页码要为整形
    except:
        p = 1
    # 查询数据，分页，按id降序
    try:
        item = UserDynamicModel.query.order_by(-UserDynamicModel.id).paginate(page=p, per_page=15)
    except:
        return render_template('main/user_dynamic.html', form=form)

    # 是否登录
    if request.method == 'POST' and not g.user:
        return render_template('main/user_dynamic.html', form=form, item=item, msg='请先登录')

    # 表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        content = request.form.get('content')
        images = request.files.getlist('images')

        # 查看缓存，判断是否重复提交
        if cache.get(str(g.user.id)+content+request.path) == 1:
            return redirect(url_for('main.user_dynamic'))

        # 文本内容保存到数据库
        dynamic_item = UserDynamicModel()
        dynamic_item.content = content
        dynamic_item.user_id = g.user.id
        try:
            db.session.add(dynamic_item)
            db.session.commit()
            # 缓存，10秒内不能重复提交，唯一标识key：用户id+内容+请求路径
            cache.set(str(g.user.id)+content+request.path, 1, timeout=10)
        except:
            return render_template('main/user_dynamic.html', form=form, item=item, msg='发布失败')

        # 没有上传图片直接重定向
        if images[0].filename == '':
            return redirect(url_for('main.user_dynamic'))

        # 图片数量限制五张
        if len(images) > 5:
            return render_template('main/user_dynamic.html', form=form, item=item, image_too_many_error='最多只能上传五张图片')

        # 图片处理
        for image in images:
            # 图片后缀名验证
            if '.' not in image.filename or (image.filename != '' and image.filename.rsplit('.')[1] not in ('png', 'jpg', 'gif', 'jpeg')):
                return render_template('main/user_dynamic.html', form=form, item=item, image_error='只支持png,jpg,gif,jpeg格式的图片')

            # 图片限制大小：10M
            size = image.read(10*1024*1024+1)  # 最大读取10M+1字节，防止读取全部
            if len(size) > 10*1024*1024:
                return render_template('main/user_dynamic.html', form=form, item=item, msg='大小不能超过10M')

            # 创建文件名，用户id_uuid.jpg
            image_filename = str(g.user.id) + '_' + str(uuid.uuid4()) + '.jpg'
            # 创建文件路径
            image_path = os.path.join(settings.UPLOAD_USER_DYNAMIC_IMAGE, image_filename)
            # 图片保存到本地，二进制写入
            with open(image_path, 'wb') as f:
                f.write(size)

            # 保存图片到数据库
            try:
                image_item = UserDynamicImageModel()
                image_item.image = '/images/upload_user_dynamic_image/' + image_filename
                image_item.dynamic_id = dynamic_item.id
                db.session.add(image_item)
                db.session.commit()
            except:
                return render_template('main/user_dynamic.html', form=form, item=item, msg='发布失败')
        return redirect(url_for('main.user_dynamic'))
    # get请求
    return render_template('main/user_dynamic.html', form=form, item=item)


@main_bp.route('/message_board', methods=['GET', 'POST'])
def message_board():
    '''留言板'''
    form = MessageBoradForm()

    # get请求
    try:
        p = int(request.args.get('page', 1))  # 页码要为整形
    except:
        p = 1
    # 查询数据，分页，按id降序
    try:
        message_list = MessageBoardModel.query.order_by(-MessageBoardModel.id).paginate(page=p, per_page=20)
    except:
        return render_template('main/message_board.html', form=form)

    # post请求
    # 是否登录
    if request.method == 'POST' and not g.user:
        return render_template('main/message_board.html', form=form, message_list=message_list, msg='请先登录')

    # 表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        content = form.content.data
        # 查看缓存判断是否重复提交
        if cache.get(str(g.user.id) + content + request.path) == 1:
            return redirect(url_for('main.message_board'))

        # 创建对象
        item = MessageBoardModel()
        item.content = content
        item.user_id = g.user.id
        # 提交数据库
        try:
            db.session.add(item)
            db.session.commit()
            # 缓存，10秒内不能重复提交，唯一标识key：用户id+内容+请求路径
            cache.set(str(g.user.id) + content + request.path, 1, timeout=10)
            return redirect(url_for('main.message_board'))
        except:
            return render_template('main/message_board.html', form=form, message_list=message_list, msg='提交失败')
    # get请求
    return render_template('main/message_board.html', form=form, message_list=message_list)


# 自定义404错误页面
@main_bp.app_errorhandler(404)
def page_404(e):
    '''页面未找到错误'''
    return render_template('404.html'), 404

