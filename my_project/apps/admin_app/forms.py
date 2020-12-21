from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField  # 字段
from wtforms.validators import DataRequired, Length, ValidationError  # 验证器
from flask import session
import re
from flask_wtf.file import FileField, FileAllowed  # 文件上传字段，验证


class ChangeIndexIntroductionForm(FlaskForm):
    '''修改首页简介表单验证'''
    # 标题
    title = StringField('title', validators=[DataRequired(message='请输入标题'),
                                             Length(max=30, message='最多只能输入三十个字符')])
    # 正文
    content = StringField('content', validators=[DataRequired(message='请输入正文')])
    # 门票费用说明
    rates = StringField('content', validators=[Length(max=20, message='最多只能输入二十个字符')])
    # 开放时间
    opening_hours = StringField('opening_hours', validators=[Length(max=50, message='最多只能输入五十个字符')])


class AddScenicSpotForm(FlaskForm):
    '''添加景点表单验证'''
    # 景点名称
    name = StringField('name', validators=[DataRequired(message='请输入景点名称'),
                                             Length(max=20, message='最多只能输入二十个字符')])
    # 景点简介
    content = StringField('content', validators=[DataRequired(message='请输入景点简介')])
    # 门票费用说明
    rates = StringField('content', validators=[Length(max=20, message='最多只能输入二十个字符')])
    # 开放时间
    opening_hours = StringField('opening_hours', validators=[Length(max=50, message='最多只能输入五十个字符')])
    # 景点封面图
    image = FileField('image', validators=[DataRequired(message='请添加封面图'),
        FileAllowed(['png', 'jpg', 'gif', 'jpeg'], message='只支持png,jpg,gif,jpeg格式的图片')
    ])


class AddInfoForm(FlaskForm):
    '''添加公告表单验证'''
    # 公告名称
    title = StringField('title', validators=[DataRequired(message='请输入标题'),
                                             Length(max=40, message='最多只能输入四十个字符')])
    # 内容
    content = StringField('content', validators=[DataRequired(message='请输入内容')])
