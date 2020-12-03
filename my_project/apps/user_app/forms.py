from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField  # 字段
from wtforms.validators import DataRequired, Length, ValidationError  # 验证器
from flask import session
import re


# 在下面定义表单验证类
class UserRegisterForm(FlaskForm):
    '''用户注册表单验证'''
    # 邮箱
    email = StringField('email', validators=[DataRequired(message='请输入邮箱')])
    # 密码
    password = PasswordField('password', validators=[DataRequired(message='请输入密码'),
                                                     Length(min=6, message='密码长度至少六位')])
    # 图片验证码
    code = StringField('code', validators=[DataRequired('请输入验证码')])

    # 单字段验证，validate_字段名
    def validate_code(self, data):
        '''验证码匹配'''
        # 从session里取出验证码与前端传来的验证码对比
        code = session.get('code')
        if code != data.data:
            raise ValidationError(message='验证码错误')

    def validate_email(self, data):
        '''邮箱验证'''
        email = data.data
        if not re.search(r'^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$', email):
            raise ValidationError('邮箱错误')


class UserLoginForm(UserRegisterForm):
    '''用户登录表单验证'''
    # 密码
    password = PasswordField('password', validators=[DataRequired(message='请输入密码')])

