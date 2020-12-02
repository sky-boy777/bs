from flask_mail import Message
from exts import mail
import settings
import threading
from itsdangerous import TimedJSONWebSignatureSerializer  # token


def async_send_mail(msg):
    '''异步发送邮件'''
    # 在使用到的时候再导入app，在头部导入会出错
    from app import app
    # 创建应用上下文
    with app.app_context():
        mail.send(message=msg)


def send_mail(email=None):
    '''发送邮件'''
    # 生成token，24小时后过期，secret_key加密
    serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=120)
    token = serializer.dumps({'email': email}).decode('utf-8')

    # 创建邮件对象
    html = '''<h1>欢迎注册</h1>点击下面链接激活账号(24小时后过期)<br>
                    <a href="http://%s/user/activate?token=%s">%s/user/active/?token=%s</a>
                    ''' % (settings.LOCALHOST, token, settings.LOCALHOST, token)
    msg = Message(subject='旅游景点自助系统账户激活', recipients=[email], html=html)

    # 创建一个线程，并启动
    t = threading.Thread(target=async_send_mail, args=(msg,))
    t.start()


if __name__ == '__main__':
    print('pass')
