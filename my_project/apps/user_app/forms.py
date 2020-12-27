from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField  # 字段
from wtforms.validators import DataRequired, Length, ValidationError  # 验证器
from flask import session
import re
from flask_wtf.file import FileField, FileAllowed  # 文件上传字段，验证
from flask_wtf.file import FileStorage


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
        '''图片验证码匹配'''
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


class UserChangePasswordForm(FlaskForm):
    '''用户修改密码表单验证'''
    # 旧密码
    old_password = PasswordField('old_password', validators=[DataRequired(message='请输入密码'),
                                                            Length(min=6, message='密码格式不对')])
    # 新密码
    new_password = PasswordField('new_password', validators=[DataRequired(message='请输入密码'),
                                                            Length(min=6, message='密码长度至少六位')])


class SendEmailCodeForm(FlaskForm):
    '''发送动态验证码表单验证'''
    # 邮箱
    email = StringField('email', validators=[DataRequired(message='请输入邮箱')])
    # 图片验证码
    code = StringField('code', validators=[DataRequired('请输入验证码')])

    def validate_code(self, data):
        '''图片验证码匹配'''
        # 从session里取出验证码与前端传来的验证码对比
        code = session.get('code')
        if code != data.data:
            raise ValidationError(message='验证码错误')

    def validate_email(self, data):
        '''邮箱验证'''
        email = data.data
        if not re.search(r'^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$', email):
            raise ValidationError('邮箱错误')


class ResetPasswordForm(FlaskForm):
    '''重置密码表单验证'''
    # 密码
    password = PasswordField('password', validators=[DataRequired(message='请输入密码'),
                                                     Length(min=6, message='密码长度至少六位')])
    # 动态验证码
    email_code = StringField('email_code', validators=[DataRequired('请输入验证码')])
    # 图片验证码
    code = StringField('code', validators=[DataRequired('请输入验证码')])

    # 单字段验证，validate_字段名
    def validate_code(self, data):
        '''图片验证码匹配'''
        # 从session里取出验证码与前端传来的验证码对比
        code = session.get('code')
        if code != data.data:
            raise ValidationError(message='验证码错误')

    def validate_email_code(self, data):
        '''动态验证码匹配'''
        # 从session里取出动态验证码与前端传来的对比
        email_code = session.get('email_code')
        if email_code != data.data:
            raise ValidationError(message='动态验证码错误')


class UserCenterForm(FlaskForm):
    '''用户中心修改个人信息表单验证'''
    # 用户名
    username = StringField('username', validators=[Length(max=30, message='用户名太长了')])
    # 头像
    icon = FileField('icon', validators=[FileAllowed(['png', 'jpg', 'gif', 'jpeg'], message='只支持png,jpg,gif,jpeg格式的图片')])


class UserAddDynamicForm(FlaskForm):
    '''用户发表动态表单验证'''
    content = StringField('content', validators=[DataRequired(message='请输入内容'),
                                                 Length(max=500, message='最多只能输入500个字符')])
    images = FileField('images', validators=[FileAllowed(['png', 'jpg', 'gif', 'jpeg'], message='只支持png,jpg,gif,jpeg格式的图片')])
