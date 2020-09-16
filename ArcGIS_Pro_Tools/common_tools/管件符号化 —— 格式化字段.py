import os
import functools
import arcpy
import datetime
import json

arcpy.env.overwriteOutput = True


def _addMessage(mes: str) -> None:
    print(mes)
    arcpy.AddMessage(mes)
    return None


def _addWarning(mes: str) -> None:
    print(mes)
    arcpy.AddWarning(mes)
    return None


def _addError(mes: str) -> None:
    print(mes)
    arcpy.AddError(mes)
    return None


# decorater --- used to get function run time
def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        print(f"Method {func.__name__} start running ! ")
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        stop = datetime.datetime.now()
        cost = stop - start
        print("*" * 30)
        print(f"Method {func.__name__} start at {start}")
        print(f"Method {func.__name__} finish at {stop}")
        print(f"Method {func.__name__} total cost {cost}")
        print("*" * 30)
        return res

    return _wrapper


def _addField(*args, **kwargs):
    try:
        arcpy.AddField_management(*args, **kwargs)
    except:
        arcpy.DeleteField_management(*(args[:2]))
        arcpy.AddField_management(*args, **kwargs)


def addFiled(inFC: str, fieldName: str, fieldType: str, fieldLength: int = None, fieldPrec: int = None) -> str:
    if fieldLength:
        if fieldPrec:
            _addField(inFC, fieldName, fieldType, field_length=fieldLength, field_precision=fieldPrec)
        else:
            _addField(inFC, fieldName, fieldType, field_length=fieldLength)
    else:
        _addField(inFC, fieldName, fieldType)
    return inFC


def _copyFeature(inFC: str, outputPath: str, outputName: str) -> str:
    # keep origin workspace
    oriWS = None
    if arcpy.env.workspace:
        oriWS = arcpy.env.workspace

    folderType = arcpy.Describe(outputPath).dataType
    if folderType == "Workspace":
        if outputName[-4:] == ".shp":
            outputName = outputName[:-4]
    # .sde like directory
    elif folderType == "File":
        if outputName[-4:] == ".shp":
            outputName = outputName[:-4]
    else:
        if not outputName[-4:] == ".shp":
            outputName = outputName + ".shp"

    arcpy.CopyFeatures_management(inFC, os.path.join(outputPath, outputName))

    try:
        if oriWS:
            arcpy.env.workspace = oriWS
        else:
            arcpy.ClearEnvironment("workspace")
    except:
        pass

    return os.path.join(outputPath, outputName)


def addFormatFields(inFC: str, formatJsonFile: str, outputPath: str, outputName: str) -> str:
    # copy a new data
    pFC = _copyFeature(inFC, outputPath, outputName)

    with open(formatJsonFile, "r", encoding="utf-8") as f:
        dataMapList = json.loads(f.read())["convert"]

    # add target fields
    for eachField in dataMapList:
        skipSW, fieldName, fieldType = eachField["skip"], eachField["tar_field"], eachField["tar_type"]
        if skipSW.lower() != "skip":
            addFiled(pFC, fieldName, fieldType)

    return pFC


def calMapValue(inFC: str, formatJsonFile: str) -> str:
    with open(formatJsonFile, "r", encoding="utf-8") as f:
        dataMapList = json.loads(f.read())["convert"]

    # add target fields
    for eachField in dataMapList:
        (skipSW, oriField, oriType,
         tarField, tarType, values) = (eachField["skip"], eachField["ori_field"], eachField["ori_type"],
                                       eachField["tar_field"], eachField["tar_type"], eachField["values"])

        if skipSW.upper() != "SKIP":
            codes = f"""valueDict = {values}
fieldAType = '{oriType}'
def f(fieldA):
    if fieldAType != "TEXT":
        fieldA = str(fieldA)
        if fieldA in valueDict:
            return int(valueDict[fieldA])
        else:
            try:
                return -999999
            except:
                pass
    else:
        if fieldA in valueDict:
            return valueDict[fieldA]
        else:
            try:
                return "-999999"
            except:
                pass"""
            arcpy.CalculateField_management(inFC, tarField, f"f(!{oriField}!)", "PYTHON3", codes)

    return inFC


@getRunTime
def main(inFC, formatJsonFile, outputPath, outputName):
    # add format field
    pFC = addFormatFields(inFC, formatJsonFile, outputPath, outputName)

    # convert origin field value to target field
    calMapValue(pFC, formatJsonFile)


demoData = r"E:\公司GIS共用\管件配色支持文件\demoData\demo.shp"
formatJsonFile = r"E:\公司GIS共用\管件配色支持文件\外来数据字段格式化映射文件.json"
outputPath = r"E:\公司GIS共用\管件配色支持文件\demoData\res"
outputName = "test"

if __name__ == "__main__":
    main(demoData, formatJsonFile, outputPath, outputName)


# import random
# list1 = ["分线箱a", "监控器a", "接线箱a", "人孔a", "手孔a"]
# list2 = ["出入地点a","非探测区a","分支a","拐点a","井边点a","入户a","上杆a","预留口a","直线点a"]
# list3 = ["01","1001","1021","1031","1041","1051","1061","2021"]
# list4 = ["塑料a","砼a","铸铁a"]
#
# def f():
#     return int(list3[random.randint(0, 2)])
