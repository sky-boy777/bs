from flask import Blueprint, render_template, request, redirect, url_for
from apps.admin_app.forms import ChangeIndexIntroductionForm, AddScenicSpotForm
from apps.main_app.models import IndexBriefIntroductionModel, ScenicSpotsModel
from exts import db, cache
import os, settings, uuid


# 后台管理蓝图，需要在create_app下注册
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/admin_index')
def admin_index():
    '''后台管理首页'''


    return render_template('admin/admin_index.html')


@admin_bp.route('/change_index_introduction', methods=['GET', 'POST'])
def change_index_introduction():
    '''修改首页简介'''
    form = ChangeIndexIntroductionForm()
    is_succeed = 0  # 标志:成功为1，否则为0

    # get请求，首先查询数据库渲染表单
    try:
        # 查询看数据库是否有数据
        item = IndexBriefIntroductionModel.query.filter().first()
    except:
        return render_template('admin/change_index_introduction.html',
                               is_succeed=is_succeed,
                               item=None, form=form, msg='查询数据失败')
    # 表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        title = form.title.data
        content = form.content.data
        rates = form.rates.data
        # 有则更新，无则添加
        if item:
            item.title = title
            item.content = content
            item.rates = rates if rates else '免费'  # 三元表达式
            try:
                db.session.commit()
            except:
                return render_template('admin/change_index_introduction.html',
                                       is_succeed=is_succeed,
                                       item=item, form=form, msg='修改失败！')
        else:
            # 实例化一个新对象
            item = IndexBriefIntroductionModel()
            item.title = title
            item.content = content
            item.rates = rates if rates else '免费'  # 三元表达式
            try:
                db.session.add(item)
                db.session.commit()
            except:
                return render_template('admin/change_index_introduction.html',
                                       form=form, item=item,
                                       msg='添加失败!', is_succeed=is_succeed)
        is_succeed = 1  # 操作成功标志
        return render_template('admin/change_index_introduction.html',
                               item=item, form=form, is_succeed=is_succeed)
    return render_template('admin/change_index_introduction.html',
                           form=form, item=item, is_succeed=is_succeed)


@admin_bp.route('/add_scenic_spot', methods=['GET', 'POST'])
def add_scenic_spot():
    '''添加景点'''
    form = AddScenicSpotForm()
    is_succeed = 0  # 标志:添加成功为1，否则为0
    # post请求+表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        name = form.name.data
        content = form.content.data
        rates = form.rates.data
        image = form.image.data

        # 判断是否重复提交
        if cache.get(name) == 1:
            return redirect(url_for('admin.admin_index'))

        # 判断上传图片大小，限制大小：5M
        size = image.read()  # 读出二进制流
        if len(size) > 5 * 1024 * 1024:
            return render_template('admin/add_scenic_spot.html', form=form, msg='大小不能超过5M', is_succeed=is_succeed)

        # 将二进制图片保存到本地
        image_filename = str(uuid.uuid4()) + '.jpg'  # 文件名
        image_path = os.path.join(settings.SCENIC_SPOT_DIR, image_filename)
        with open(image_path, 'wb') as f:
            f.write(size)

        # 查询数据库是否有相同的景点名称，有则更新
        try:
            item = ScenicSpotsModel.query.filter(ScenicSpotsModel.name == name).first()
            if item:
                item.name = name
                item.content = content
                item.rates = rates if rates else '免费'  # 三元表达式
                item.image = '/images/scenic_spot/' + image_filename
                db.session.commit()
                # 防止重复提交，设置唯一标识，放入缓存
                cache.set(name, 1, timeout=10)
                return render_template('admin/add_scenic_spot.html', form=form, is_succeed=1)
        except:
            return render_template('admin/add_scenic_spot.html', form=form, is_succeed=is_succeed, msg='添加失败！')

        # 保存到数据库
        item = ScenicSpotsModel()
        item.name = name
        item.content = content
        item.rates = rates if rates else '免费'  # 三元表达式
        item.image = '/images/scenic_spot/' + image_filename
        try:
            db.session.add(item)
            db.session.commit()
            # 防止重复提交，设置唯一标识，放入缓存
            cache.set(name, 1, timeout=10)
            return render_template('admin/add_scenic_spot.html', form=form, is_succeed=1)
        except:
            return render_template('admin/add_scenic_spot.html', form=form, is_succeed=is_succeed, msg='添加失败！')
    # get请求
    return render_template('admin/add_scenic_spot.html', form=form)


@admin_bp.route('/add_info', methods=['GET', 'POST'])
def admin_add_info():
    '''发布公告'''
    pass
