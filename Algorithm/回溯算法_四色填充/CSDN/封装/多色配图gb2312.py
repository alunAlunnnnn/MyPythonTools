import arcpy
from numpy import *
import datetime


def addColorField(InputFeature, colorField):
    try:
        arcpy.AddField_management(InputFeature, colorField, "SHORT")
    except:
        arcpy.DeleteField_management(InputFeature, colorField)
        arcpy.AddField_management(InputFeature, colorField, "SHORT")

    if len(arcpy.ListFields(InputFeature, colorField)) > 0:
        arcpy.AddMessage(f"create color field '{colorField}' successful")

    return InputFeature


def generateColorValue(InputFeature, level, UniqueField, ConnectField, splitDim, maxColor, colorField):
    U = []
    C = []
    S = []
    N = 0
    rows = arcpy.UpdateCursor(InputFeature)
    if (level):
        for row in rows:
            N = N + 1
            U.append(str(row.getValue(UniqueField)))
            C.append(str(row.getValue(ConnectField)))
            S.append(row.getValue(level))
    else:
        for row in rows:
            N = N + 1
            U.append(str(row.getValue(UniqueField)))
            C.append(str(row.getValue(ConnectField)))
            S.append('total')

    sheng = list(set(S))
    for each_sheng in sheng:
        u = []
        c = []
        for i in range(0, N):
            if (S[i] == each_sheng):
                u.append(U[i])
                c.append(C[i])
        n = len(u)
        mat = zeros([n, n], int)
        for i in range(0, n):
            tem = c[i].split(splitDim)
            for j in tem:
                if (j in u):
                    ind = u.index(j)
                    if (ind != i):
                        mat[i][ind] = 1
        colorIndex = ones(n, int)
        I = 1
        colorI = 1
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
                I = I - 1
                colorI = colorIndex[I] + 1

        i = 0
        j = 0
        # rows = arcpy.UpdateCursor(InputFeature)
        # for row in rows:
        #     if (S[j] == each_sheng):
        #         row.color = int(colorIndex[i])
        #         rows.updateRow(row)
        #         i = i + 1
        #     j = j + 1
        # rows = arcpy.UpdateCursor(InputFeature)
        with arcpy.da.UpdateCursor(InputFeature, [colorField]) as cur:
            for row in cur:
                if (S[j] == each_sheng):
                    row[0] = int(colorIndex[i])
                    cur.updateRow(row)
                    i = i + 1
                j = j + 1


def main(InputFeature, colorField, level, UniqueField, ConnectField, splitDim, maxColor):
    # add a corlor filed
    addColorField(InputFeature, colorField)

    # calculate color value
    generateColorValue(InputFeature, level, UniqueField, ConnectField, splitDim, maxColor, colorField)


InputFeature = arcpy.GetParameterAsText(0)
colorField = arcpy.GetParameterAsText(1)
UniqueField = arcpy.GetParameterAsText(2)
ConnectField = arcpy.GetParameterAsText(3)
level = arcpy.GetParameterAsText(4)
splitDim = arcpy.GetParameterAsText(5)
maxColor = arcpy.GetParameterAsText(6)

maxColor = int(maxColor)

if __name__ == "__main__":
    runData = datetime.datetime.now()
    limit = datetime.datetime.strptime("2021-03-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    if limit > runData:
        main(InputFeature, colorField, level, UniqueField, ConnectField, splitDim, maxColor)
    else:
        arcpy.AddError("failed")