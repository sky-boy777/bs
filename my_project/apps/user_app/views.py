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
from itsdangerous import TimedJSONWebSignatureSerializer  # token


# 用户模块蓝图
user_bp = Blueprint(name='user', import_name=__name__, url_prefix='/user')


@user_bp.route('/get_image_code')
def get_image_code():
    '''图片验证码链接'''
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
    form = UserRegisterForm()
    if request.method == 'POST':
        # 表单验证
        if form.validate_on_submit():
            # 验证通过，接收数据，可使用以下两种方式
            email = request.form.get('email')  # POST:form，GET:args
            password = form.password.data

            # 查询邮箱是否被注册，布尔值
            is_register = UserModel.query.filter(UserModel.email == email).first()
            if is_register:
                return render_template('user/register.html', form=form, msg='邮箱已被注册')

            # 注册
            user = UserModel()
            user.email = email
            user.password = generate_password_hash(password, salt_length=9)  # 密码加密
            try:
                pass
                # db.session.add(user)
                # db.session.commit()
            except:
                return render_template('user/register.html', form=form, msg='未知错误')

            # 如果用户添加成功，则发送激活邮件
            if user:
                # 生成token，24小时后过期，secret_key加密
                serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=86400)
                token = serializer.dumps({email: email}).decode('utf-8')

                # 发送激活邮件
                result = send_mail(email, token)
                # 发送成功
                if result:
                    return redirect(url_for(endpoint='user.login'))
                # 发送失败
                else:
                    return render_template('user/register.html', form=form, msg='邮件发送失败')
        # 表单验证未通过
        return render_template('user/register.html', form=form)
    # get请求
    return render_template('user/register.html', form=form)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''

    return render_template('user/login.html')



