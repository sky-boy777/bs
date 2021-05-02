# num = 9966
# d = {
#             0: 'ling',
#             1: 'yi',
#             2: 'er',
#             3: 'san',
#             4: 'si',
#             5: 'wu',
#             6: 'liu',
#             7: 'qi',
#             8: 'ba',
#             9: 'jiu'
#         }
# str_num = str(num)
# if len(str_num) > 1:
#     l = []
#     for i in str_num:
#         l.append(d[int(i)])
#     l.insert(1, 'shi')
#     print(''.join(l))
# else:
#     print(d[num])

numstr = "213334152226"
s = set(numstr)
d = {}
for i in s:
    d[i] = 0

for j in numstr:
    d[j] += 1

m = max(d.values())
for n in numstr:
    if d[n] == m:
        ll = [n, m]
        print(ll)
        break







