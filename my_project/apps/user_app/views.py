from flask import Blueprint, g
from flask import render_template, request, make_response, session, redirect, url_for
from utils.create_image_code import create_image_code  # 生成图片验证码
import io
import settings
from .forms import UserRegisterForm, UserLoginForm  # 表单验证类
from .models import UserModel
from werkzeug.security import generate_password_hash, check_password_hash  # 密码加密，验证
from exts import db
from utils.send_email import send_mail  # 发送邮件
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature  # token


# 用户模块蓝图
user_bp = Blueprint(name='user', import_name=__name__, url_prefix='/user')

# 生成序列化器(token)，24小时后过期，secret_key加密
serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=120)

# 登录才能访问的路径
required_login_path = ['/user/user_center']
# 登录后不能访问的路径
login_not_path = ['/user/login', '/user/register']

# 钩子函数，每次请求前执行，只用于蓝图，用户权限验证
@user_bp.before_app_request
def my_before_request():
    '''用户权限验证'''
    # 获取已登录的用户id
    uid = session.get('uid')
    # 如果请求的路径需要登录才能访问
    if request.path in required_login_path:
        if uid:
            user = UserModel.query.get(uid)
            g.user = user  # 使用g对象存储用户，这样哪个页面都能用了
        else:
            return redirect(url_for('user.login'))
    elif request.path in login_not_path and uid:
        # 已登录，不能访问登录跟注册页面
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
    if request.method == 'POST':
        # 表单验证
        if form.validate_on_submit():
            # 验证通过，接收数据，可使用以下两种方式
            email = request.form.get('email')  # POST:form，GET:args
            password = form.password.data

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
                    return redirect(url_for(endpoint='user.login'))

            # 用户不存在，注册新用户
            user = UserModel()
            user.email = email
            user.password = generate_password_hash(password, salt_length=9)  # 密码加密
            try:
                db.session.add(user)
                db.session.commit()
            except:
                return render_template('user/register.html', form=form, msg='注册失败')
            # 发送邮件，并重定向到登录页面
            send_mail(email)
            return redirect(url_for(endpoint='user.login'))

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
            return '激活链接过期，请重新注册'
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
    if request.method == 'POST':
        # 登录表单验证
        if form.validate_on_submit():
            # 获取邮箱，密码
            email = form.email.data
            password = form.password.data
            # 验证邮箱，密码
            try:
                user = UserModel.query.filter(UserModel.email == email).first()
                if user and check_password_hash(user.password, password):
                    # 验证通过，登录，保持登录状态，重定向到主页
                    session['uid'] = user.id
                    return redirect(url_for('main.index'))
            except:
                return render_template('user/register.html', form=form, msg='登录失败')
        # 表单验证未通过
        return render_template('user/login.html', form=form)
    # get请求
    return render_template('user/login.html', form=form)


@user_bp.route('/user_logout')
def user_logout():
    '''退出登录'''
    # 删除session的内存空间和cookie
    session.clear()
    return redirect(url_for('main.index'))


@user_bp.route('/user_center', methods=['GET', 'POST'])
def user_center():
    '''用户中心'''
    user = g.user
    return render_template('user/user_center.html', user=user)




