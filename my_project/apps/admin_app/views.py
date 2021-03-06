from flask import Blueprint, render_template, request, redirect, url_for
from apps.admin_app.forms import *
from apps.main_app.models import *
from apps.user_app.models import *
from exts import db, cache
import os
import settings, uuid, datetime


# 后台管理蓝图，需要在create_app下注册
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/admin_index')
def admin_index():
    '''后台管理首页'''
    # 每一样查询最新的100条

    # 公告列表
    try:
        info_list = InfoModel.query.order_by(-InfoModel.id).limit(100).all()
    except:
        info_list = None
    # 景点列表
    try:
        scenic_spot_list = ScenicSpotsModel.query.order_by(-ScenicSpotsModel.id).limit(100).all()
    except:
        scenic_spot_list = None
    # 用户列表
    try:
        user_list = UserModel.query.order_by(-UserModel.id).limit(100).all()
    except:
        user_list = None
    # 动态列表
    try:
        dynamic_list = UserDynamicModel.query.order_by(-UserDynamicModel.id).limit(100).all()
    except:
        dynamic_list = None
    # 留言板列表
    try:
        message_board_list = MessageBoardModel.query.order_by(-MessageBoardModel.id).limit(100).all()
    except:
        message_board_list = None
    return render_template('admin/admin_index.html',
                           info_list=info_list,
                           scenic_spot_list=scenic_spot_list,
                           user_list=user_list,
                           dynamic_list=dynamic_list,
                           message_board_list=message_board_list
                           )


@admin_bp.route('/change_index_introduction', methods=['GET', 'POST'])
def change_index_introduction():
    '''修改首页简介'''
    cache.delete('index_brief_introduction')  # 删除缓存
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
        opening_hours = form.opening_hours.data
        rates = form.rates.data
        # 有则更新，无则添加
        if item:
            item.title = title
            item.content = content
            item.create_time = datetime.datetime.now().strftime('%Y-%m-%d')  # 更新时间
            item.opening_hours = opening_hours if opening_hours else '24小时开放'
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
            item.opening_hours = opening_hours if opening_hours else '24小时开放'
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


@admin_bp.route('/bottom_info', methods=['GET', 'POST'])
def bottom_info():
    '''修改网站底部信息'''
    cache.delete('bottom_info')  # 删除缓存
    form = BottomInfoForm()
    is_succeed = 0  # 标志:成功为1，否则为0
    try:
        # 查询看数据库是否有数据
        item = BottomInfoModel.query.filter().first()
    except:
        return render_template('admin/bottom_info.html',
                               is_succeed=is_succeed,
                               item=None, msg='查询数据失败', form=form)

    if request.method == 'POST' and form.validate_on_submit():
        phone = request.form.get('phone')
        email = request.form.get('email')
        phone2 = request.form.get('phone2')

        # 有数据则更新
        if item:
            item.phone = phone
            item.email = email
            item.phone2 = phone2
            try:
                db.session.commit()
            except:
                return render_template('admin/bottom_info.html',
                                       is_succeed=is_succeed,
                                       item=None, msg='失败', form=form)
        else:
            item = BottomInfoModel()
            item.phone = phone
            item.email = email
            item.phone2 = phone2
            try:
                db.session.add(item)
                db.session.commit()
            except:
                return render_template('admin/bottom_info.html',
                                       is_succeed=is_succeed,
                                       item=None, msg='失败', form=form)
        return render_template('admin/bottom_info.html', is_succeed=1, item=item, form=form)
    return render_template('admin/bottom_info.html', item=item, is_succeed=is_succeed, form=form)


@admin_bp.route('/add_scenic_spot', methods=['GET', 'POST'])
def add_scenic_spot():
    '''添加景点'''
    cache.delete('scenic_spots_list')  # 删除缓存
    form = AddScenicSpotForm()
    is_succeed = 0  # 标志:添加成功为1，否则为0

    # 有sid则为编辑景点
    sid = request.args.get('sid')
    if sid:
        # 编辑景点表单验证
        form = EditScenicSpotForm()
        # 查询id对应景点
        item = ScenicSpotsModel.query.get(sid)

        if item and request.method == 'POST' and form.validate_on_submit():
            # 接收数据
            name = form.name.data
            content = form.content.data
            opening_hours = form.opening_hours.data
            rates = form.rates.data
            image = form.image.data
            images = request.files.getlist('images')  # 图集

            # 判断是否重复提交
            if cache.get(name) == 1:
                return redirect(url_for('admin.admin_index'))

            # 判断是否上传有封面图
            if image:
                # 判断上传封面图片大小，限制大小：5M
                size = image.read(5*1024*1024+1)  # 限制最大读取字节大小，防止读取全部
                if len(size) > 5 * 1024 * 1024:
                    return render_template('admin/add_scenic_spot.html', form=form, image_msg='大小不能超过5M',
                                           is_succeed=is_succeed, item=item)
                # 将二进制图片保存到本地
                image_filename = str(uuid.uuid4()) + '.jpg'  # 文件名
                image_path = os.path.join(settings.SCENIC_SPOT_DIR, image_filename)
                with open(image_path, 'wb') as f:
                    f.write(size)

                item.image = '/images/scenic_spot/' + image_filename

            # 更新数据库
            item.name = name
            item.content = content
            item.opening_hours = opening_hours if opening_hours else '24小时开放'
            item.rates = rates if rates else '免费'  # 三元表达式
            item.create_time = datetime.datetime.now().strftime('%Y-%m-%d')  # 更新时间
            db.session.commit()

            # 判断是否上传有图集
            if images[0].filename != '':
                # 图集处理
                for img in images:
                    # 图片后缀名验证
                    if '.' not in img.filename or img.filename != '' and img.filename.rsplit('.')[1] not in (
                    'png', 'jpg', 'gif', 'jpeg'):
                        return render_template('admin/add_scenic_spot.html', form=form,
                                               images_msg='只支持png,jpg,gif,jpeg格式的图片',
                                               is_succeed=is_succeed, item=item)
                    # 图片限制大小：15M
                    size = img.read(15 * 1024 * 1024+10)  # 读取15M加10字节
                    if len(size) > 15 * 1024 * 1024:
                        return render_template('admin/add_scenic_spot.html', form=form,
                                               images_too_big='最大只支持15M的图片',
                                               is_succeed=is_succeed,
                                               item=item)
                    # 创建文件名，景点id_uuid.jpg
                    img_filename = str(item.id) + '_' + str(uuid.uuid4()) + '.jpg'
                    # 创建文件路径
                    img_path = os.path.join(settings.SCENIC_SPOT_IMAGES_DIR, img_filename)
                    # 图片保存到本地，二进制写入
                    with open(img_path, 'wb') as f:
                        f.write(size)

                    # 保存图片到数据库
                    try:
                        img_item = ScenicSpotsImagesModel()
                        img_item.image = '/images/scenic_spot_images/' + img_filename
                        img_item.scenic_spots_id = item.id
                        db.session.add(img_item)
                        db.session.commit()
                    except:
                        return render_template('admin/add_scenic_spot.html', form=form,
                                               is_succeed=is_succeed,
                                               msg='添加失败！',
                                               item=item)
            # 防止重复提交，设置唯一标识，放入缓存
            cache.set(name, 1, timeout=10)
            return render_template('admin/add_scenic_spot.html', form=form, item=item, is_succeed=1)

        # get请求(编辑)
        return render_template('admin/add_scenic_spot.html', form=form, item=item)

    # post请求+表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        name = form.name.data
        content = form.content.data
        opening_hours = form.opening_hours.data
        rates = form.rates.data
        image = form.image.data
        images = request.files.getlist('images')  # 图集

        # 判断是否重复提交
        if cache.get(name) == 1:
            return redirect(url_for('admin.admin_index'))

        # 判断上传封面图片大小，限制大小：5M
        size = image.read(5*1024*1024+1)  # 限制最大读取字节大小，防止读取全部
        if len(size) > 5 * 1024 * 1024:
            return render_template('admin/add_scenic_spot.html', form=form, image_msg='大小不能超过5M', is_succeed=is_succeed)

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
                item.opening_hours = opening_hours if opening_hours else '24小时开放'
                item.rates = rates if rates else '免费'  # 三元表达式
                item.image = '/images/scenic_spot/' + image_filename
                item.create_time = datetime.datetime.now().strftime('%Y-%m-%d')  # 更新时间
                db.session.commit()

                # 判断是否上传有图集
                if images[0].filename != '':
                    # 图集处理
                    for img in images:
                        # 图片后缀名验证
                        if '.' not in img.filename or img.filename != '' and img.filename.rsplit('.')[1] not in ('png', 'jpg', 'gif', 'jpeg'):
                            return render_template('admin/add_scenic_spot.html', form=form,
                                                   images_msg='只支持png,jpg,gif,jpeg格式的图片',
                                                   is_succeed=is_succeed
                                                   )
                        # 图片限制大小：15M
                        size = img.read(15 * 1024 * 1024 + 1)
                        if len(size) > 15 * 1024 * 1024:
                            return render_template('admin/add_scenic_spot.html', form=form,
                                                   images_too_big='最大只支持15M的图片',
                                                   is_succeed=is_succeed
                                                   )
                        # 创建文件名，景点id_uuid.jpg
                        img_filename = str(item.id) + '_' + str(uuid.uuid4()) + '.jpg'
                        # 创建文件路径
                        img_path = os.path.join(settings.SCENIC_SPOT_IMAGES_DIR, img_filename)
                        # 图片保存到本地，二进制写入
                        with open(img_path, 'wb') as f:
                            f.write(size)

                        # 保存图片到数据库
                        try:
                            img_item = ScenicSpotsImagesModel()
                            img_item.image = '/images/scenic_spot_images/' + img_filename
                            img_item.scenic_spots_id = item.id
                            db.session.add(img_item)
                            db.session.commit()
                        except:
                            return render_template('admin/add_scenic_spot.html', form=form,
                                                   is_succeed=is_succeed,
                                                   msg='添加失败！'
                                                   )
                # 防止重复提交，设置唯一标识，放入缓存
                cache.set(name, 1, timeout=10)
                return render_template('admin/add_scenic_spot.html', form=form, is_succeed=1)
        except:
            return render_template('admin/add_scenic_spot.html', form=form, is_succeed=is_succeed, msg='添加失败！')

        # 保存到数据库
        item = ScenicSpotsModel()
        item.name = name
        item.content = content
        item.opening_hours = opening_hours if opening_hours else '24小时开放'
        item.rates = rates if rates else '免费'  # 三元表达式
        item.image = '/images/scenic_spot/' + image_filename
        try:
            db.session.add(item)
            db.session.commit()

            # 判断是否上传有图集
            if images[0].filename != '':
                # 图集处理
                for img in images:
                    # 图片后缀名验证
                    if '.' not in img.filename or img.filename != '' and img.filename.rsplit('.')[1] not in (
                    'png', 'jpg', 'gif', 'jpeg'):
                        return render_template('admin/add_scenic_spot.html', form=form,
                                               images_msg='只支持png,jpg,gif,jpeg格式的图片',
                                               is_succeed=is_succeed
                                               )
                    # 图片限制大小：15M
                    size = img.read(15 * 1024 * 1024 + 1)
                    if len(size) > 15 * 1024 * 1024:
                        return render_template('admin/add_scenic_spot.html', form=form,
                                               images_too_big='最大只支持15M的图片',
                                               is_succeed=is_succeed
                                               )
                    # 创建文件名，景点id_uuid.jpg
                    img_filename = str(item.id) + '_' + str(uuid.uuid4()) + '.jpg'
                    # 创建文件路径
                    img_path = os.path.join(settings.SCENIC_SPOT_IMAGES_DIR, img_filename)
                    # 图片保存到本地，二进制写入
                    with open(img_path, 'wb') as f:
                        f.write(size)

                    # 保存图片到数据库
                    try:
                        img_item = ScenicSpotsImagesModel()
                        img_item.image = '/images/scenic_spot_images/' + img_filename
                        img_item.scenic_spots_id = item.id
                        db.session.add(img_item)
                        db.session.commit()
                    except:
                        return render_template('admin/add_scenic_spot.html', form=form,
                                               is_succeed=is_succeed,
                                               msg='添加失败！'
                                               )
            # 防止重复提交，设置唯一标识，放入缓存
            cache.set(name, 1, timeout=10)
            return render_template('admin/add_scenic_spot.html', form=form, is_succeed=1)
        except:
            return render_template('admin/add_scenic_spot.html', form=form, is_succeed=is_succeed, msg='添加失败！')
    # get请求
    return render_template('admin/add_scenic_spot.html', form=form)


@admin_bp.route('/add_info', methods=['GET', 'POST'])
def add_info():
    '''发布公告'''
    form = AddInfoForm()
    is_succeed = 0  # 标志:添加成功为1，否则为0
    # get请求如果带有info_id，则为编辑公告

    # 编辑公告
    info_id = request.args.get('info_id')
    if info_id:
        # 查询id对应公告
        try:
            item = InfoModel.query.get(info_id)
            if request.method == 'POST' and form.validate_on_submit() and item:
                title = form.title.data
                # 判断是否重复提交
                if cache.get(title) == 1:
                    return redirect(url_for('admin.admin_index'))

                item.title = title
                item.content = form.content.data
                item.create_time = datetime.datetime.now().strftime('%Y-%m-%d')  # 更新时间
                db.session.commit()
                # 防止重复提交，设置唯一标识，放入缓存
                cache.set(title, 1, timeout=10)
                return render_template('admin/add_info.html', form=form, is_succeed=1)
            return render_template('admin/add_info.html', form=form, is_succeed=is_succeed, item=item)
        except:
            # 查询出错则转为添加公告
            return render_template('admin/add_info.html', form=form, is_succeed=is_succeed)

    # 发布或更新公告
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        title = form.title.data
        content = form.content.data
        # 判断是否重复提交
        if cache.get(title) == 1:
            return redirect(url_for('admin.admin_index'))

        # 查询数据库是否有相同的公告名称，有则更新公告
        try:
            item = InfoModel.query.filter(InfoModel.title == title).first()
            if item:
                item.title = title
                item.content = content
                item.create_time = datetime.datetime.now().strftime('%Y-%m-%d')  # 更新时间
                db.session.commit()
                # 防止重复提交，设置唯一标识，放入缓存
                cache.set(title, 1, timeout=10)
                return render_template('admin/add_info.html', form=form, is_succeed=1)
        except:
            return render_template('admin/add_info.html', form=form, is_succeed=is_succeed, msg='发布失败！')

        # 发布公告
        item = InfoModel()
        item.title = title
        item.content = content
        try:
            db.session.add(item)
            db.session.commit()
            # 防止重复提交，设置唯一标识，放入缓存
            cache.set(title, 1, timeout=10)
            return render_template('admin/add_info.html', form=form, is_succeed=1)
        except:
            return render_template('admin/add_info', form=form, is_succeed=is_succeed, msg='发布失败！')

    # 普通get请求(添加公告)
    return render_template('admin/add_info.html', form=form, is_succeed=is_succeed)


@admin_bp.route('/search_page', methods=['POST', 'GET'])
def search_page():
    '''搜索结果页面'''
    # 一个标志,返回给前端，表示对应返回的数据类型
    flag = 0

    # get请求:接收翻页的参数
    key = request.args.get('key', None)
    content = request.args.get('content', None)

    # 提取关键字跟搜索内容
    if request.method == 'POST':
        key = request.form.get('key', None)
        content = request.form.get('content', None)

    # 空值处理:关键字必须
    if not key:
        return redirect(url_for('admin.admin_index'))

    # 页码
    try:
        p = int(request.args.get('page', 1))  # 页码要为整形
    except:
        p = 1

    """
    1: 公告标题
    2: 景点名
    3: 用户名
    4: 邮箱
    5: 动态
    6: 留言
    """
    try:
        items_dict = {
            '1': InfoModel.query.filter(InfoModel.title.contains(content)),
            '2': ScenicSpotsModel.query.filter(ScenicSpotsModel.name.contains(content)),
            '3': UserModel.query.filter(UserModel.username.contains(content)),
            '4': UserModel.query.filter(UserModel.email.contains(content)),
            '5': UserDynamicModel.query.filter(UserDynamicModel.content.contains(content)),
            '6': MessageBoardModel.query.filter(MessageBoardModel.content.contains(content))
        }
    except:
        return redirect(url_for('admin.admin_index'))

    items = items_dict.get(key)
    if items:
        items = items.paginate(page=p, per_page=20)
        return render_template('admin/search_page.html', items=items, flag=int(key), key=key, content=content)

    return redirect(url_for('admin.admin_index'))


@admin_bp.route('/add_banner', methods=['GET', 'POST'])
def add_banner():
    '''首页轮播图管理'''
    cache.delete('image_list')  # 删除缓存
    form = BannerForm()
    # 查询所有图片，渲染到页面
    image_list = None
    try:
        image_list = BannerModel.query.order_by(-BannerModel.id).all()
    except:
        return render_template('admin/add_banner.html', form=form, error='数据加载失败')

    # 上传图片验证
    if request.method == 'POST' and form.validate_on_submit():
        image = form.image.data

        # 读取图片，限制大小：15M
        size = image.read(15 * 1024 * 1024 + 1)
        if len(size) > 15 * 1024 * 1024:
            return render_template('admin/add_banner.html', form=form, msg='图片大小限制15M',
                                   image_list=image_list)

        # 将二进制图片保存到本地
        image_filename = str(uuid.uuid4()) + '.jpg'  # 文件名
        image_path = os.path.join(settings.UPLOAD_BANNER_DIR, image_filename)
        with open(image_path, 'wb') as f:
            f.write(size)

        # 图片保存到数据库
        item = BannerModel()
        item.image = '/images/banner/' + image_filename
        try:
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('admin.add_banner'))
        except:
            return render_template('admin/add_banner.html', form=form, msg='上传失败',
                                   image_list=image_list)

    return render_template('admin/add_banner.html', form=form, image_list=image_list)


@admin_bp.route('/delete_info', methods=['GET', 'POST'])
def delete_info():
    '''删除公告信息'''
    if request.method == 'POST':
        # 获取需要删除的公告id
        info_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = InfoModel.query.get(info_id)
            if item:
                db.session.delete(item)
                db.session.commit()
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        return 'true'


@admin_bp.route('/delete_scenic_spots', methods=['GET', 'POST'])
def delete_scenic_spots():
    '''删除景点'''
    if request.method == 'POST':
        # 获取id
        sp_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = ScenicSpotsModel.query.get(sp_id)
            # 删除封面图
            if os.path.exists(settings.STATIC_DIR + item.image):
                os.remove(settings.STATIC_DIR + item.image)
            if item:
                # 删除对应的图集
                item_images = ScenicSpotsImagesModel.query.filter(ScenicSpotsImagesModel.scenic_spots_id == item.id).all()
                if item_images:
                    for i in item_images:
                        db.session.delete(i)
                db.session.delete(item)
                db.session.commit()
                # 删除完数据库里面的数据后，删除保存在本地的图片
                for j in item_images:
                    if os.path.exists(settings.STATIC_DIR + j.image):
                        os.remove(settings.STATIC_DIR + j.image)
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        cache.delete('scenic_spots_list')  # 删除缓存
        return 'true'


@admin_bp.route('/delete_scenic_spots_image', methods=['GET', 'POST'])
def delete_scenic_spots_image():
    '''单独删除景点图集对应图片'''
    if request.method == 'POST':
        # 获取id
        sp_image_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = ScenicSpotsImagesModel.query.get(sp_image_id)
            if item:
                db.session.delete(item)
                db.session.commit()
                # 删除完数据库里面的数据后，删除保存在本地的图片
                if os.path.exists(settings.STATIC_DIR + item.image):
                    os.remove(settings.STATIC_DIR + item.image)
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        cache.delete('scenic_spots_list')  # 删除缓存
        return 'true'


@admin_bp.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    '''添加管理员'''
    if request.method == 'POST':
        # 用户id
        user_id = request.form.get('id')
        # 根据id查询
        try:
            item = UserModel.query.get(user_id)
            if item:
                item.is_admin = 1
                db.session.commit()
            else:
                return '失败，用户不存在'
        except:
            return '添加失败'
        return 'true'


@admin_bp.route('/del_user', methods=['GET', 'POST'])
def del_user():
    '''删除未激活的用户'''
    if request.method == 'POST':
        # 用户id
        user_id = request.form.get('id')
        # 根据id查询
        try:
            item = UserModel.query.get(user_id)
            # 判断是否为未激活的用户
            if item and not item.is_activate:
                db.session.delete(item)
                db.session.commit()
            else:
                return '失败，用户不存在'
        except:
            return '失败'
        return 'true'


@admin_bp.route('/delete_dynamic', methods=['GET', 'POST'])
def delete_dynamic():
    '''删除动态'''
    if request.method == 'POST':
        # 获取id
        d_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = UserDynamicModel.query.get(d_id)
            if item:
                # 删除对应的图集
                item_images = UserDynamicImageModel.query.filter(UserDynamicImageModel.dynamic_id == item.id).all()
                if item_images:
                    for i in item_images:
                        db.session.delete(i)
                db.session.delete(item)
                db.session.commit()
                # 删除完数据库里面的数据后，删除保存在本地的图片
                for j in item_images:
                    if os.path.exists(settings.STATIC_DIR + j.image):
                        os.remove(settings.STATIC_DIR + j.image)
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        return 'true'


@admin_bp.route('/delete_message', methods=['GET', 'POST'])
def delete_message():
    '''删除留言'''
    if request.method == 'POST':
        # 获取id
        message_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = MessageBoardModel.query.get(message_id)
            if item:
                db.session.delete(item)
                db.session.commit()
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        return 'true'


@admin_bp.route('/delete_banner_img', methods=['GET', 'POST'])
def delete_banner_img():
    '''删除轮播图'''
    if request.method == 'POST':
        # 获取id
        img_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = BannerModel.query.get(img_id)
            if item:
                db.session.delete(item)
                db.session.commit()
                # 删除本地的图片
                if os.path.exists(settings.STATIC_DIR + item.image):
                    os.remove(settings.STATIC_DIR + item.image)
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        cache.delete('image_list')  # 删除缓存
        return 'true'

