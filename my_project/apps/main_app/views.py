from flask import Blueprint, render_template

main_bp = Blueprint('main_app', __name__)  # 前台展示蓝图，需要在create_app下注册


@main_bp.route('/', endpoint='index')
def index():
    # 查询数据库展示

    return render_template('main_app/index.html')