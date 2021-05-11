# arr1 = input().split(',')
# arr2 = input().split(',')
# arr1 = '3,2,1'.split(',')
# arr2 = '4,5,6'.split(',')
# l = arr1+arr2
# l.sort(reverse=True)
# l = ','.join(l)
# print(type(l))

# s = 'abcaABC'
# d = dict()
#
# for i in s:
#     if d.get(i):
#         d[i] += 1
#     else:
#         d[i] = 1
# max_d = dict()
# max_d['d'] = 1
# for j in d:
#     if d[j] > max_d['d']:
#         max_d['d'] = d[j]
#
# print(max_d['d'])

# input = '"[()]{}"'
# s = '[({'
# l = list()
# flag = True
# for i in input:
#     if i in s:
#         l.append(i)
#     elif len(l) <= 0:
#         flag = False
#         break
#     elif i == l.pop():
#         flag = True
#         continue
#     else:
#         flag = False
#         break

# n = 2
# l = []
# i = 0
# while i < n:
#     s = input().split()
#     l.append(s)
#     i += 1
#
# max_l = []
# for j in l:
#     j.sort(reverse=True)
#     max_l.append(j[0])
# print(max_l)

import hashlib
a = hashlib.sha256('123'.encode()).hexdigest()
b = hashlib.sha256('123'.encode()).hexdigest()
print(a==b)
