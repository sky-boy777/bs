s = 'qwerkfjdgkajfkdsjflsd'
for i in range(len(s)):
    print(s[i], end='')
    if i>0 and i % 4 == 0:
        print()