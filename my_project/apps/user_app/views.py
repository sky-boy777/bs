from flask import Blueprint, g, render_template, request, make_response, session, redirect, url_for
from utils.create_image_code import create_image_code  # 生成图片验证码
import io, os
import settings
from .forms import *  # 表单验证类
from .models import UserModel, MessageBoardModel, UserDynamicModel, UserDynamicImageModel
from apps.main_app.models import BottomInfoModel
from werkzeug.security import generate_password_hash, check_password_hash  # 密码加密，验证
from exts import db, cache
from utils.send_email import send_mail, send_mail_code  # 发送邮件
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature  # token
import random


# 用户模块蓝图
user_bp = Blueprint(name='user', import_name=__name__, url_prefix='/user')

# 生成序列化器(token)，24小时后过期，secret_key加密
serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY,
                                             expires_in=120)

# 需要登录的路径
required_login_path = ['/user/user_center', '/user/change_password',
                       '/user//delete_message', '/user/delete_dynamic',
                       ]
# 登录后不能访问的路径
login_not_path = ['/user/login', '/user/register']

# 钩子函数，每次请求前执行，只用于蓝图，用户权限验证
@user_bp.before_app_request
def my_before_request():
    '''用户权限验证'''
    # 查询网站底部信息
    try:
        g.bottom_info = BottomInfoModel.query.filter().first()
    except:
        g.bottom_info = None
    # 尝试获取用户id
    uid = session.get('uid')
    try:
        user = UserModel.query.get(uid)
        g.user = user  # 使用g对象存储用户，这样哪个页面都能用了
    except:
        # 查询数据库出错
        g.user = None
    # 未登录，不能访问
    if request.path in required_login_path and not user:
        return redirect(url_for('user.login'))
    # 已登录，不能访问
    if request.path in login_not_path and user:
        return redirect(url_for('main.index'))
    # 不是管理员不能访问
    if re.search(r'^/admin.*', request.path):
        if user and user.is_admin != 1:  # 已登录且是普通用户
            return redirect(url_for('main.index'))


@user_bp.route('/get_image_code')
def get_image_code():
    '''获取图片验证码'''
    # 生成图片验证码
    code, image_code = create_image_code()
    # 验证码存入session
    session['code'] = code
    # 创建缓冲区
    buffer = io.BytesIO()
    # 验证码图片存入缓冲区
    image_code.save(buffer, 'jpeg')
    # 获取缓冲区里二进制验证码图片
    b_img = buffer.getvalue()
    # 创建响应对象，响应头改为图片类型
    res = make_response(b_img)
    res.headers['Content-Type'] = 'image/jpg'
    return res


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    '''用户注册'''
    # 实例化一个表单验证对象
    form = UserRegisterForm()

    # 1表示已发送邮件，注册成功后才返回给前端
    is_send_register_mail = 1

    if request.method == 'POST':
        # 表单验证
        if form.validate_on_submit():
            # 验证通过，接收数据，可使用以下两种方式
            email = request.form.get('email')  # POST:form，GET:args
            password = form.password.data
            code = form.code.data
            # 判断是否重复提交表单
            if cache.get(email) == 1:
                return render_template('user/register.html', form=form, flag=is_send_register_mail)

            # 如果用户已注册，且已激活，first()得到一个对象，不加得到查询集
            # 方法一，取下标
            # user = UserModel.query.filter(UserModel.email == email)
            # user = user[0]
            # 方法二，first()
            user = UserModel.query.filter(UserModel.email == email).first()

            # 如果用户存在
            if user:
                # 用户存在且已激活
                if user.is_activate == 1:
                    return render_template('user/register.html', form=form, msg='邮箱已被注册')
                elif user.is_delete == 1:
                    # 恶意账户被管理员逻辑删除
                    return render_template('user/register.html', form=form, msg='该用户不能注册')
                elif user.is_delete == 0:
                    # 用户存在但未激活，未销号，只更新用户密码，然后重新发送激活邮件
                    user.password = generate_password_hash(password, salt_length=9)  # 密码加密
                    try:
                        db.session.commit()
                    except:
                        # 提交数据库出错
                        return render_template('user/register.html', form=form, msg='注册失败')

                    # 发邮件（异步）
                    send_mail(email)
                    # 防止重复提交，设置一唯一个标志，放入缓存
                    cache.set(email, 1, timeout=10)
                    return render_template('user/register.html', form=form, flag=is_send_register_mail)

            # 用户不存在，注册新用户
            user = UserModel()
            user.email = email
            user.password = generate_password_hash(password, salt_length=9)  # 密码加密
            try:
                db.session.add(user)
                db.session.commit()
            except:
                return render_template('user/register.html', form=form, msg='注册失败')

            # 发邮件（异步）
            send_mail(email)
            # 防止重复提交，设置一个唯一标志，放入缓存
            cache.set(email, 1, timeout=10)
            return render_template('user/register.html', form=form, flag=is_send_register_mail)

        # 表单验证未通过
        return render_template('user/register.html', form=form)
    # get请求
    return render_template('user/register.html', form=form)


@user_bp.route('/activate')
def activate():
    '''新用户激活'''
    try:
        try:
            # 获取token值
            token = request.args.get('token', None)
            # 判断是否有token值
            if not token:
                return redirect(url_for(endpoint='main.index'))
            # 解密token
            info = serializer.loads(token)
            email = info.get('email')
        except SignatureExpired as e:
            return '激活链接过期'
        except BadSignature as e:
            return '无效的链接'
        # 查找用户
        try:
            user = UserModel.query.filter(UserModel.email == email).first()
        except:
            return '激活失败'
        # 用户存在且未激活，激活用户
        if user and user.is_activate == 0:
            user.is_activate = 1
            db.session.commit()
            return '激活成功，可以登录了'
        # 用户已激活
        elif user.is_activate == 1:
            return '激活成功'
        else:
            return '用户不存在'
    except:
        # 未知错误重定向到主页
        return redirect(url_for(endpoint='main.index'))


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''
    form = UserLoginForm()
    # 登录表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 获取邮箱，密码
        email = form.email.data
        password = form.password.data
        # 验证邮箱，密码
        try:
            user = UserModel.query.filter(UserModel.email == email).first()
            if user and check_password_hash(user.password, password):
                if user.is_activate != 1:
                    return render_template('user/login.html', form=form, msg='该邮箱尚未激活，请先重新注册')
                if user.is_delete == 1:
                    return render_template('user/login.html', form=form, msg='该邮箱已被管理员加入黑名单')
                # 验证通过，登录并保持登录状态，重定向到主页
                session['uid'] = user.id
                return redirect(url_for('main.index'))
            return render_template('user/login.html', form=form, msg='邮箱未注册或密码错误')
        except:
            return render_template('user/login.html', form=form, msg='未知错误，登录失败')
    # 表单验证未通过或get请求
    return render_template('user/login.html', form=form)


# 忘记密码逻辑处理开始
@user_bp.route('/send_email_code', methods=['GET', 'POST'])
def send_email_code():
    '''发送动态验证码'''
    form = SendEmailCodeForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 接收邮箱号
        email = form.email.data
        # 判断缓存是否有值，有：表单重复提交
        if cache.get(email) == 1:
            # 重复提交表单处理
            return render_template('user/send_email_code.html', form=form, is_send_mail=1)

        # 生成随机动态验证码，保存到session
        email_code = str(random.randint(1000, 999999))  # 4~6位验证码，转为str发送邮件
        # 保存到session，邮箱也要保存到session
        session['email_code'] = email_code
        session['email'] = email

        # 发送动态验证码
        send_mail_code(email=email, email_code=email_code)
        is_send_mail = 1  # 标记动态验证码发送成功，用来返回给前端
        # 防止重复提交：设置一唯一个标志，放入缓存
        cache.set(email, 1, timeout=10)
        return render_template('user/send_email_code.html', form=form, is_send_mail=is_send_mail)
    return render_template('user/send_email_code.html', form=form)


@user_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    '''发送验证码后重置密码处理'''
    form = ResetPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        password = form.password.data
        email = session.get('email')
        # 查询用户重置密码
        try:
            user = UserModel.query.filter(UserModel.email == email).first()
            if user:
                # 重置密码
                user.password = generate_password_hash(password=password, salt_length=9)
                db.session.commit()
                # 清除session重新登录
                session.clear()
                is_reset_password = 1  # 标记重置密码成功，返回给前端
                return render_template('user/reset_password.html', form=form, is_reset_password=is_reset_password)
            else:
                return render_template('user/reset_password.html', form=form, msg='用户不存在')
        except:
            return render_template('user/reset_password.html', form=form, msg='未知错误，重置密码失败')
    # get请求
    return render_template('user/reset_password.html', form=form)
# 忘记密码逻辑处理结束


@user_bp.route('/user_logout')
def user_logout():
    '''退出登录'''
    # 删除session的内存空间和cookie
    session.clear()
    return redirect(url_for('main.index'))


@user_bp.route('/user_center', methods=['GET', 'POST'])
def user_center():
    '''用户中心'''
    form = UserCenterForm()

    # post请求，修改个人信息
    if request.method == 'POST' and form.validate_on_submit():
        # 查询当前用户
        user = g.user
        # 判断用户名是否有值
        if request.form.get('username'):
            user.username = form.username.data  # 添加到待提交区
        # 判断是否上传有图片文件
        if form.icon.data:
            icon = form.icon.data
            # 创建文件名跟保存的路径
            icon_filename = str(user.id) + '.gif'  # 文件名为：用户id.gif，可以动图
            icon_path = os.path.join(settings.UPLOAD_ICON_DIR, icon_filename)

            # 判断文件大小，字节换算
            '''
            1Byte(字节) = 8bit(位)
            1KB = 1024Byte(字节)
            1MB = 1024KB
            1GB = 1024MB
            1TB = 1024GB
            '''
            size = icon.read(3*1024*1024+1)  # 最大读取3M+1字节，防止全部读取
            if len(size) > 3*1024*1024:  # 限制文件大小：3M
                return render_template('user/user_center.html', form=form, msg='大小不能超过3M')
            # 图片保存到本地，二进制写入
            with open(icon_path, 'wb') as f:
                f.write(size)

            # # 添加到待提交区
            user.icon = '/images/icon/' + icon_filename
        # 提交到数据库
        db.session.commit()

    return render_template('user/user_center.html', form=form)


@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    '''修改密码：已登录才能修改密码'''
    # 实例化表单验证对象
    form = UserChangePasswordForm()
    # post请求，表单验证
    if request.method == 'POST' and form.validate_on_submit():
        # 接收数据
        old_password = form.old_password.data
        new_password = form.new_password.data

        user = g.user
        # 匹配用户密码
        if check_password_hash(user.password, old_password):
            # 修改密码，提交
            user.password = generate_password_hash(password=new_password)
            db.session.commit()
            # 清除session，修改密码后需要重新登录
            session.clear()
            is_change = 1  # 表示修改成功，前端弹框告知用户
            return render_template('user/change_password.html', form=form, is_change=is_change)
        else:
            return render_template('user/change_password.html',
                                   form=form,
                                   old_password_error='严重怀疑你不是本人，自己的密码都记不住')
    # 表单验证未通过或get请求
    return render_template('user/change_password.html', form=form)


@user_bp.route('/delete_message', methods=['GET', 'POST'])
def delete_message():
    '''删除留言'''
    if request.method == 'POST':
        # 获取需要删除的公告id
        message_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = MessageBoardModel.query.get(message_id)
            #       判断当前留言是否属于当前用户
            if item and item.user_id == g.user.id:
                db.session.delete(item)
                db.session.commit()
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        return 'true'


@user_bp.route('/delete_dynamic', methods=['GET', 'POST'])
def delete_dynamic():
    '''删除动态'''
    if request.method == 'POST':
        # 获取需要删除的公告id
        dynamic_id = request.form.get('id')
        # 根据id查询，然后删除
        try:
            item = UserDynamicModel.query.get(dynamic_id)
            #       判断当前留言是否属于当前用户
            if item and item.user_id == g.user.id:
                # 查询此条动态的图片
                item_images = UserDynamicImageModel.query.filter(UserDynamicImageModel.dynamic_id == item.id).all()
                if item_images:
                    for i in item_images:
                        db.session.delete(i)
                db.session.delete(item)
                db.session.commit()
            else:
                return '失败，资源不存在'
        except:
            return '失败'
        return 'true'









