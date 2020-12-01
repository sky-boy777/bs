from flask_mail import Message
from exts import mail
import settings


def send_mail(email=None, token=None):
    '''发送邮件'''
    msg = Message()
    msg.subject = '旅游景点自助系统账户激活'  # 主题
    msg.recipients = [email]  # 收件人
    msg.html = '''<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>账户激活</title>
                </head>
                <body>
                <h1>欢迎注册</h1>
                点击下面链接激活账号(24小时后过期)<br>
                <a href="%s/user/active/?token=%s">%s/user/active/?token=%s</a>
                </body>
                </html>''' % (settings.LOCALHOST, token, settings.LOCALHOST, token)
    # msg.html = '<h1>欢迎注册</h1> ' \
    #            '点击下面链接激活账号(24小时后过期)<br>' \
    #            '<a href="http://%s/user/active/?token=%s">%s/user/active/?token=%s</a>' \
    #            % (settings.LOCALHOST, token, settings.LOCALHOST, token)

    # 发送
    try:
        mail.send(msg)
        return True
    except:
        return False


if __name__ == '__main__':
    pass
