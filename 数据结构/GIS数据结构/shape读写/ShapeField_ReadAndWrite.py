import struct


shp = r'D:\c\a.shp'

with open(shp, 'rb') as f:
    # 二进制数据直接读取
    f.seek(36)
    data1 = f.read(8)
    data2 = f.read(8)
    data3 = f.read(8)
    data4 = f.read(8)
    print('data1 is %s' % data1)
    print('data2 is %s' % data2)
    print('data3 is %s' % data3)
    print('data4 is %s' % data4)

    s1 = struct.unpack('<d', data1)
    s2 = struct.unpack('<d', data2)
    s3 = struct.unpack('<d', data3)
    s4 = struct.unpack('<d', data4)
    print('s1 is %s' % s1)
    print('s2 is %s' % s2)
    print('s3 is %s' % s3)
    print('s4 is %s' % s4)



