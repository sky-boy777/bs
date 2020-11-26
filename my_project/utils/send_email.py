from flask_mail import Message, Mail
from apps import mail


def send_mail():
    '''发送邮件'''
    msg = Message()
    msg.subject = '旅游景点自助系统'  # 主题
    msg.sender = '账户激活<bycwql@163.com>'  # 发件人
    msg.recipients = ['1251779123@qq.com']  # 收件人
    msg.html = '<a href="#">垃圾</a>'  # 内容

    # 发送
    try:
        mail.send(msg)
        return True
    except:
        return False


if __name__ == '__main__':
    pass
