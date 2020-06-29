import arcpy
'''This script used to check whether the two feature calss inputed totally same'''

arcpy.env.overwriteOutput = True

deleteSwitch = True
inmemorySwitch = True


def FCFieldMatchCheck(src, dst):
    srcFieldList = [each.name for each in arcpy.ListFields(src)]
    dstFieldList = [each.name for each in arcpy.ListFields(dst)]
    sameField = [each for each in srcFieldList if each in dstFieldList]
    diffField = [each for each in srcFieldList if each not in dstFieldList]
    try:
        sameField.remove('SHAPE')
    except:
        pass

    try:
        sameField.remove('shape')
    except:
        pass

    try:
        sameField.remove('Shape')
    except:
        pass

    return sameField, diffField


def getAllFieldsValues(src, dst):
    sameFieldList, difFieldList = FCFieldMatchCheck(src, dst)
    sameFieldLen = len(sameFieldList)
    resDic = {}
    # get all field value in {1(objectid): [other field values], next objectid: ..... }
    with arcpy.da.SearchCursor(src, sameFieldList) as cur:
        for row in cur:
            rowList = []
            for i in range(sameFieldLen):
                if i == 0:
                    continue
                # start from 1, without objectid
                rowList.append(row[i])
            resDic[row[0]] = rowList

    return resDic


def FCFieldValueMatchCheck(src, dst):
    resDic = getAllFieldsValues(src, dst)
    sameFieldList, difFieldList = FCFieldMatchCheck(src, dst)
    sameFieldLen = len(sameFieldList)
    with arcpy.da.SearchCursor(dst, sameFieldList) as cur:
        dstDict = {}
        for row in cur:
            wrongKey = False
            diffValue = []
            objId = row[0]
            values = resDic[objId]
            for i in range(sameFieldLen):
                if i == 0:
                    continue
                if row[i] == values[i-1]:
                    pass
                else:
                    fieldName = sameFieldList[i]
                    difTup = (fieldName, values[i-1], row[i])
                    diffValue.append(difTup)
                    wrongKey = True
            if wrongKey:
                dstDict[objId] = diffValue
    return dstDict


# src = r'E:\松江管廊\统一sde与原数据的objectid\污水三维管线.gdb\PS_84P_ALLv2'
# dst = r'E:\松江管廊\统一sde与原数据的objectid\污水三维管线.gdb\PS_84P'
src = r'E:\温州污水\污水二三维数据更新_20200628\result\result_0629.gdb\PS_84P'
dst = r'E:\温州污水\污水二三维数据更新_20200628\result\result_0629.gdb\PS_84P_3Dv2'
res = FCFieldValueMatchCheck(src, dst)
with open(r'E:\温州污水\污水二三维数据更新_20200628\属性表对比\PS_84P.txt', 'w', encoding='utf-8') as f:
    f.write(str(res))