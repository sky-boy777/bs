from flask import Blueprint
from flask import render_template

# 用户模块蓝图
user_bp = Blueprint(name='user', import_name=__name__, url_prefix='/user')


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    '''用户注册'''

    return render_template('user/register.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''用户登录'''

    return render_template('user/login.html')



