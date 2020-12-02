from flask import Blueprint
from flask import render_template, request, make_response, session, redirect, url_for
from utils.create_image_code import create_image_code  # 生成图片验证码
import io
import settings
from .forms import UserRegisterForm  # 表单验证类
from .models import UserModel
from werkzeug.security import generate_password_hash  # 密码加密
from exts import db
from utils.send_email import send_mail  # 发送邮件
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired  # token


# 用户模块蓝图
user_bp = Blueprint(name='user', import_name=__name__, url_prefix='/user')


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

            # 查询用户是否已存在数据库
            if user:
                # 用户存在且已激活
                if user.is_activate == 1:
                    return render_template('user/register.html', form=form, msg='邮箱已被注册')
                elif user.is_delete == 0:
                    # 用户存在但未激活，未销号（恶意账户被管理员逻辑删除），只更新用户密码，然后重新发送激活邮件
                    user.password = generate_password_hash(password, salt_length=9)  # 密码加密
                    try:
                        db.session.commit()
                    except:
                        # 提交数据库出错
                        return render_template('user/register.html', form=form, msg='注册失败')
                    # 发邮件
                    send_mail(email)
                    return redirect(url_for(endpoint='user.login'))

            # 新用户注册
            user = UserModel()
            user.email = email
            user.password = generate_password_hash(password, salt_length=9)  # 密码加密
            try:
                db.session.add(user)
                db.session.commit()
            except:
                return render_template('user/register.html', form=form, msg='注册失败')
            # 调用异步发送邮件函数，并重定向到登录页面
            send_mail(email)
            return redirect(url_for(endpoint='user.login'))

        # 表单验证未通过
        return render_template('user/register.html', form=form)
    # get请求
    return render_template('user/register.html', form=form)


@user_bp.route('/activate', methods=['GET'])
def activate():
    '''账户激活'''
    print('**************************************开始')
    # try:
    try:
        token = request.args.get('token')
        serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY)
        info = serializer.loads(token)
        email = info.get('email')
        print(token,'*******', email, '********************')
    except SignatureExpired as e:
        print('-------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>链接过期')
        return '激活链接过期，请重新注册'
    try:
        # 查找用户
        user = UserModel.query.filter(UserModel.email == email).first()
    except:
        return '用户不存在'
    if user:
        user.is_activate = 1
        db.session.commit()
        return '激活成功，可以登录了'
    else:
        return '用户不存在'
    # except:
    #     # 未知错误重定向到主页
    #     return redirect(url_for(endpoint='main.index'))


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''

    return render_template('user/login.html')






