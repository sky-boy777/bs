# # 接收初始坐标
# xy = list(input())
# try:
#     x = int(xy[0])
#     y = int(xy[-1])
# except:
#     pass
#
# # 接收指令
# s = input()
# if len(s) <= 10000:
#     # 执行指令
#     for i in s:
#         if i == 'U':
#             y += 1
#         if i == 'D':
#             y -= 1
#         if i == 'L':
#             x -= 1
#         if i == 'R':
#             x += 1
# print(x, end=' ')
# print(y)

#n = int(input())
n = 3
l = list()

for i in range(n):
    s = list(input())
    l.append(s)
print(l)
