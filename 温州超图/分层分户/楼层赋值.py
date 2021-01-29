a = 2
def f():
    global a
    a += 1
    return int(a / 3)


# 房间号
def f(floor, mid):
    mid += 3
    return floor *100 + mid % 3 if mid % 3 != 0 else floor * 100 + 3