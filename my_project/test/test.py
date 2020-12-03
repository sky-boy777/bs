import random


def generate_random_str():
    '''生成随机用户名'''
    s = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOLKJHGFDSAZXCVBNM'
    random_str = ''
    for i in range(20):
        random_str += random.choice(s)
    return random_str

if __name__ == '__main__':
    print(generate_random_str())