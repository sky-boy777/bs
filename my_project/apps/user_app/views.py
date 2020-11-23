from flask import Blueprint
from flask import render_template, request, make_response, session
from utils.create_image_code import create_image_code  # 生成图片验证码
import io
from .forms import UserRegisterForm  # 表单验证类


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
            pass
        return render_template('user/register.html', form=form)


    return render_template('user/register.html', form=form)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''

    return render_template('user/login.html')



