from flask import Blueprint, render_template, request, redirect, g
from apps.main_app.models import *
import os
import uuid
import settings
from apps.user_app.forms import UserAddDynamicForm
from apps.user_app.models import *
from exts import cache

# 前台展示蓝图
main_bp = Blueprint('main', __name__)  # 前台展示蓝图，需要在create_app下注册

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


@main_bp.route('/user_dynamic', methods=['GET', 'POST'])
def user_dynamic():
    '''用户动态'''
    form = UserAddDynamicForm()

    # 是否登录
    if request.method == 'POST' and not g.user:
        return render_template('main/user_dynamic.html', form=form, msg='请先登录')

    # 表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        content = request.form.get('content')
        images = request.files.getlist('images')

        # 查看缓存是否有重复提交标志
        if cache.get(content) == 1:
            return render_template('main/user_dynamic.html', form=form)

        # 文本内容保存到数据库
        dynamic_item = UserDynamicModel()
        dynamic_item.content = content
        dynamic_item.user_id = g.user.id
        try:
            db.session.add(dynamic_item)
            db.session.commit()
        except:
            return render_template('main/user_dynamic.html', form=form, msg='发布失败')

        # 图片数量限制五张
        if len(images) > 5:
            return render_template('main/user_dynamic.html', form=form, image_too_many_error='最多只能上传五张图片')

        # 图片处理
        for image in images:
            # 图片后缀名验证
            if '.' not in image.filename or image.filename != '' and image.filename.rsplit('.')[1] not in ('png', 'jpg', 'gif', 'jpeg'):
                return render_template('main/user_dynamic.html', form=form, image_error='只支持png,jpg,gif,jpeg格式的图片')

            # 图片限制大小：10M
            size = image.read()
            if len(size) > 10*1024*1024:
                return render_template('main/user_dynamic.html', form=form, msg='大小不能超过10M')

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
                return render_template('main/user_dynamic.html', form=form, msg='发布失败')
        # 缓存添加标志，防止重复提交，20秒后过期
        cache.set(content, 1, timeout=20)

    # get请求
    # 查询所有用户动态+动态的图片
    try:
        item = UserDynamicModel.query.filter().all()
    except:
        return render_template('main/user_dynamic.html', form=form, item=None)

    return render_template('main/user_dynamic.html', form=form, item=item)