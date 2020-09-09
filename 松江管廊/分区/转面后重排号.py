import arcpy
import functools
import datetime
import os
import uuid


def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        print(f"Start at: {start}")
        res = func(*args, **kwargs)
        end = datetime.datetime.now()
        cost = end - start
        print(f"Start at: {start}")
        print(f"Finish at: {end}")
        print(f"Total cost at: {cost}")
        return res

    return _wrapper


def addFormatFields(inFC):
    fieldNameList = ["X", "Y", "PARTID"]
    fieldTypeList = ["DOUBLE", "DOUBLE", "TEXT"]
    for i, eachField in enumerate(fieldNameList):
        try:
            arcpy.AddField_management(inFC, eachField, fieldTypeList[i])
        except:
            arcpy.DeleteField_management(inFC, eachField)
            arcpy.AddField_management(inFC, eachField, fieldTypeList[i])


def calculateCoordField(inFC):
    arcpy.CalculateField_management(inFC, "X", "!shape.centroid.X!", "PYTHON3")
    arcpy.CalculateField_management(inFC, "Y", "!shape.centroid.Y!", "PYTHON3")


def sortDataByCoordField(inFC):
    if inFC == "最终_分区界限_分界面_S02_空间连接":
        arcpy.Sort_management(inFC, inFC + "_Sorted", [["Y", "ASCENDING"], ["X", "ASCENDING"]])
    else:
        arcpy.Sort_management(inFC, inFC + "_Sorted", [["X", "ASCENDING"], ["Y", "ASCENDING"]])
    return inFC + "_Sorted"


def calPartIDField(inFC):
    if inFC == "最终_分区界限_分界面_S01_空间连接_Sorted":
        codes = """a = "1"
b = 0
def f():
    global a, b
    b += 1
    if len(str(b)) < 2:
        return a + "0" + str(b)
    else:
        return a + str(b)"""
    elif inFC == "最终_分区界限_分界面_S02_空间连接_Sorted":
        codes = """a = "2"
b = 0
def f():
    global a, b
    b += 1
    if len(str(b)) < 2:
        return a + "0" + str(b)
    else:
        return a + str(b)"""
    elif inFC == "最终_分区界限_分界面_S03_空间连接_Sorted":
        codes = """a = "3"
b = 0
def f():
    global a, b
    b += 1
    if len(str(b)) < 2:
        return a + "0" + str(b)
    else:
        return a + str(b)"""
    elif inFC == "最终_分区界限_分界面_S04_空间连接_Sorted":
        codes = """a = "4"
b = 0
def f():
    global a, b
    b += 1
    if len(str(b)) < 2:
        return a + "0" + str(b)
    else:
        return a + str(b)"""
    arcpy.CalculateField_management(inFC, "PARTID", "f()", "PYTHON3", codes)


def clearField(inFC):
    arcpy.DeleteField_management(inFC,
                                 ['Join_Count', 'TARGET_FID', 'Entity', 'Layer', 'Color', 'Linetype', 'Elevation',
                                  'LineWt', 'RefName', 'ORIG_FID'])


def mergeData(inFCList, outputData):
    arcpy.Merge_management(inFCList, outputData)
    addMessageField_FenQu(outputData)


def dissolveData(inFCList):
    newFCList = []
    for each in inFCList:
        arcpy.Dissolve_management(each, each + "_dis", ["part"])
        newFCList.append(each + "_dis")
    outputData = "管廊分区_合并"
    mergeData(newFCList, outputData)
    addMessageField_FenQu(outputData)


# a = "4"
# b = 0
# def f():
#     global a, b
#     b += 1
#     if len(str(b)) < 2:
#         return a + "0" + str(b)
#     else:
#         return a + str(b)


def addMessageField_FenQu(inFC):
    fieldName = ["ZONE", "UUID1"]
    fieldType = ["TEXT", "TEXT"]
    for i, each in enumerate(fieldName):
        try:
            arcpy.AddField_management(inFC, each, fieldType[i])
        except:
            arcpy.DeleteField_management(inFC, each)
            arcpy.AddField_management(inFC, each, fieldType[i])

    arcpy.CalculateField_management(inFC, "ZONE", "!part!", "PYTHON3")
    codes = """import uuid
def f():
    return str(uuid.uuid1())"""
    arcpy.CalculateField_management(inFC, "UUID1", "f()", "PYTHON3", codes)
    # try:
    #     arcpy.DeleteField_management(inFC, "part")
    # except:
    #     pass


@getRunTime
def main(inFC):
    addFormatFields(inFC)
    calculateCoordField(inFC)
    sortedFC = sortDataByCoordField(inFC)
    calPartIDField(sortedFC)
    clearField(sortedFC)


data = ["最终_分区界限_分界面_S01_空间连接", "最终_分区界限_分界面_S02_空间连接",
        "最终_分区界限_分界面_S03_空间连接", "最终_分区界限_分界面_S04_空间连接"]

sortdata = ["最终_分区界限_分界面_S01_空间连接_Sorted", "最终_分区界限_分界面_S02_空间连接_Sorted",
            "最终_分区界限_分界面_S03_空间连接_Sorted", "最终_分区界限_分界面_S04_空间连接_Sorted"]

sourceGDB = r"E:\松江管廊\新数据0805\分区图层_0902\gis\cad转入数据投影至84.gdb"
targetGDB = r"E:\松江管廊\新数据0805\分区图层_0902\gis\cad转入数据投影至84.gdb"

arcpy.env.workspace = sourceGDB
arcpy.env.overwriteOutput = True
for each in data:
    main(each)

outputData = "分区界限_合并"
mergeData(sortdata, outputData)

dissolveData(sortdata)
