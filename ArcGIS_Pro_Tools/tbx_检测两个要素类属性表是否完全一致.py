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


src = arcpy.GetParameterAsText(0)
dst = arcpy.GetParameterAsText(1)
outLog = arcpy.GetParameterAsText(2)
try:
    res = FCFieldValueMatchCheck(src, dst)

    if outLog[-4:] != '.txt':
        outLog = outLog[:-4] + '.txt'

    with open(outLog, 'w', encoding='utf-8') as f:
        f.write(str(res))

except KeyError:
    arcpy.AddWarning('ERROR --- the number of rows between input data1 and data2 is not euqal, processing is closing')
    arcpy.AddWarning('ERROR --- please make sure that, the number of rows between two data is equal')


