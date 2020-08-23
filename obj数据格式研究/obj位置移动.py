import re, os, sys

objData = './data/大桥/qiao.obj'

i = 0
newf = open(r'E:\cesium\cesium数据导入测试\obj\长江镇大桥obj_原始\newobj\newobj.obj', 'w')
with open(objData) as f:
    for each in f.readlines():
        dataType = each.replace('  ', ' ').split(' ')[0]
        if dataType == 'v':
            data_x = str(float(each.replace('  ', ' ').split(' ')[1]) + 629452.8281)
            data_y = str(float(each.replace('  ', ' ').split(' ')[3]) + 3546467.041)
            data_z = each.replace('  ', ' ').split(' ')[2]
            newdata = dataType + '  ' + data_x + ' ' + data_z + ' ' + data_y + '\n'
            newf.write(newdata)
        else:
            newf.write(each)



newf.close()