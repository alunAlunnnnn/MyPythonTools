import arcpy
from numpy import *

InputFeature = arcpy.GetParameterAsText(0)
UniqueField = arcpy.GetParameterAsText(1)
ConnectField = arcpy.GetParameterAsText(2)
# level = arcpy.GetParameterAsText(3)

# 先检查color字段是否存在，不存在则创建该字段
arcpy.AddField_management(InputFeature, "color", "SHORT")
U = []
C = []
S = []
N = 0
# 图层中多边形的个数
rows = arcpy.UpdateCursor(InputFeature)
# 读取数据
for row in rows:
    N = N + 1
    U.append(str(row.getValue(UniqueField)))
    C.append(str(row.getValue(ConnectField)))
    S.append(u'全国')
sheng = list(set(S))
for each_sheng in sheng:
    u = []
    c = []
    arcpy.AddMessage(u'正在计算：' + each_sheng)
    for i in range(0, N):
        if (S[i] == each_sheng):
            u.append(U[i])
            c.append(C[i])
    # 生成邻接矩阵
    n = len(u)
    mat = zeros([n, n], int)
    for i in range(0, n):
        # arcpy.AddMessage(c[i])
        tem = c[i].split(" ")
        for j in tem:
            if (j in u):
                ind = u.index(j)
                if (ind != i):
                    mat[i][ind] = 1
                    # arcpy.AddMessage("mat["+str(i)+"]["+str(ind)+"]")
    # 计算颜色
    maxColor = 4
    colorIndex = ones(n, int)
    I = 1
    colorI = 1
    # arcpy.AddMessage(maxColor)
    while (I < n and I >= 0):
        arcpy.AddMessage(str(I))
        while (colorI <= maxColor and I < n):
            for k in range(0, I):
                if (mat[k][I] and colorIndex[k] == colorI):
                    k = k - 1
                    break
            if ((k + 1) == I):
                colorIndex[I] = colorI
                colorI = 1
                I = I + 1
            else:
                colorI = colorI + 1
        if (colorI > maxColor):
            # arcpy.AddMessage(str(I))
            I = I - 1
            colorI = colorIndex[I] + 1
    i = 0
    j = 0
    rows = arcpy.UpdateCursor(InputFeature)
    for row in rows:
        if (S[j] == each_sheng):
            row.color = colorIndex[i]
            rows.updateRow(row)
            i = i + 1
        j = j + 1
