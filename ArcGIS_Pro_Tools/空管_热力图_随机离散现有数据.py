import random


data = r'D:/a/FlightRadar2.txt'

with open(data,'r') as f:
    res = f.readlines()
    print(res)

with open(r'D:/a/restxt.txt', 'w') as f:
    for i, each in enumerate(res):
        if i == 0:
            f.write(each)
            continue

        a = each.split('\t')
        print(a)
        a[2] = str(float(a[2]) + random.uniform(-1, 1))
        a[3] = str(float(a[3]) + random.uniform(-1, 1))
        print(a)
        eachStr = '\t'.join(a)
        f.write(eachStr)

