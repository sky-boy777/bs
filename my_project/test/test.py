def a(n):
    if n==1:
        return n
    return n+a(n-1)
print(a(16))