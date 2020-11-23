from PIL import Image, ImageFont, ImageDraw
import random

def random_RGB():
    '''随机生成RGB'''
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def create_image_code():
    '''创建图片验证码'''
    s = 'qwertyuiop1234567890lkjhgfdsazxcvbnm'  # 26个单词跟0-9数字
    # 创建画布
    image_code = Image.new(mode='RGB', size=(100, 30), color=random_RGB())
    # 添加字体文件
    my_font = ImageFont.truetype('static/font/bahnschrift.ttf', size=25)
    # 创建画图对象
    draw = ImageDraw.Draw(im=image_code)

    code = ''  # 初始化验证码

    # 开始绘制
    for i in range(4):
        c = random.choice(s)  # 每次随机选一个字符
        # xy坐标设置字符间距
        draw.text(xy=(i*random.randint(20, 30), random.randint(0, 10)), text=c, font=my_font, fill=random_RGB())
        code += c

    # 画干扰线
    for j in range(2):
        draw.line(xy=((0, random.randint(0, 30)), (90, random.randint(0, 30))), fill=random_RGB())

    # image_code.show()
    # print(code)

    return code, image_code


if __name__ == '__main__':
    create_image_code()