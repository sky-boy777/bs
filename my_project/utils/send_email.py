from flask_mail import Message
from exts import mail
import settings
import threading


def async_send_mail(msg):
    '''异步发送邮件'''
    # 在使用到的时候再导入app，在头部导入会出错
    from app import app
    # 创建应用上下文
    with app.app_context():
        mail.send(message=msg)


def send_mail(email=None):
    '''发送邮件'''
    from apps.user_app.views import serializer  # 序列化器
    token = serializer.dumps({'email': email}).decode('utf-8')

    # 创建邮件对象
    html = '''<h1>欢迎注册</h1>点击下面链接激活账号(24小时后过期)<br>
                    <a href="http://%s/user/activate?token=%s">%s/user/active/?token=%s</a>
                    ''' % (settings.LOCALHOST, token, settings.LOCALHOST, token)
    msg = Message(subject='旅游景点自助系统账户激活', recipients=[email], html=html)

    # 创建一个线程，并启动
    t = threading.Thread(target=async_send_mail, args=(msg,))
    t.start()

def async_send_mail_code(msg):
    '''异步发送动态验证码'''
    # 在使用到的时候再导入app，在头部导入会出错
    from app import app
    # 创建应用上下文
    with app.app_context():
        mail.send(message=msg)


def send_mail_code(email=None, email_code=None):
    '''发送动态验证码'''
    # 创建邮件对象
    msg = Message(subject='旅游景点自助系统验证码', recipients=[email], body='您的验证码为：' + email_code)
    # 创建一个线程，并启动
    t = threading.Thread(target=async_send_mail_code, args=(msg,))
    t.start()


if __name__ == '__main__':
    print('pass')
