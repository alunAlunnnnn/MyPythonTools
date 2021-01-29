import threading
import arcpy
import os

"""
结果：失败 貌似arcpy不支持多线程
"""

arcpy.env.overwriteOutput = True

# ********** 拆分polygon **********

def getFCOIDName(inFC):
    oIDField = [each.name for each in arcpy.ListFields(inFC) if each.type == "OID"][0]
    return oIDField


# get name and value list of input featureclass
def getFCOIDValue(inFC):
    oIDName = getFCOIDName(inFC)
    oIDValueList = []
    with arcpy.da.SearchCursor(inFC, [oIDName]) as cur:
        for row in cur:
            oIDValueList.append(row[0])
        del row

    return oIDName, oIDValueList


# split input featureclass to multi shape file
def splitData(inputData, splitNum, outputPath, outputName):
    # only accept int number
    if isinstance(splitNum, int):
        splitNum = int(splitNum)

    # get objectid name and all objectid values
    OIDName, OIDValueList = getFCOIDValue(inputData)

    # get min and max value
    minValue, maxValue = min(OIDValueList), max(OIDValueList)
    stepTotal, step = (maxValue - minValue), (maxValue - minValue) / splitNum

    # split data
    for i in range(1, splitNum + 1):
        if i == 1:
            selectSQL = f"{OIDName} < {minValue + step * i}"
        elif i == splitNum:
            selectSQL = f"{OIDName} >= {minValue + step * (i - 1)}"
        else:
            selectSQL = f"{OIDName} >= {minValue + step * (i - 1)} and {OIDName} < {minValue + step * i}"

        print(selectSQL)

        #
        arcpy.Select_analysis(inputData, os.path.join(outputPath, f"shpSplit_{i}"), selectSQL)

# ********** 拆分polygon **********

def convertPlgToRas(plg, outputPath):
    print(plg, outputPath)
    # 获取OID字段名和字段值
    OIDName, OIDValue = getFCOIDValue(plg)

    # 获取线程名，用以创建输出目录
    tName = threading.current_thread().name
    print(tName)
    if not os.path.exists(os.path.join(outputPath, tName)):
        os.makedirs(os.path.join(outputPath, tName))

    with arcpy.da.SearchCursor(plg, [OIDName]) as cur:
        lyr = arcpy.MakeFeatureLayer_management(plg, "lyr")
        # lyr = plg
        for row in cur:
            print(threading.current_thread())
            arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", f"{OIDName} = {row[0]}")
            arcpy.PolygonToRaster_conversion(plg, OIDName, os.path.join(outputPath, tName, f"ras_{row[0]}"))


def getResultData(inputPath):
    resList = [os.path.join(inputPath, each) for each in os.listdir(inputPath) if each[-4:] == ".shp"]
    print(resList)
    return resList



inputData = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\工程_DEM挖坑测试\温州_DEM挖坑\温州_DEM挖坑.gdb\RES_PY_MOUN_Buffer_Multipart2"
splitNum = 10
outputPath = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\测试_大数据量压平DEM\数据_拆分缓冲面"
outRasPath = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\测试_大数据量压平DEM\数据_拆分缓冲面_多线程测试"
outputName = "split"
threadList = [t1, t2, t3, t4, t5] = None, None, None, None, None
threadNameList = ["t1", "t2", "t3", "t4", "t5"]
threads = []

# 拆分数据
# splitData(inputData, splitNum, outputPath, outputName)

# 获取拆分后的数据
dataList = getResultData(outputPath)
print(dataList)
# 循环实例化线程并启动
# for i, eachThread in enumerate(threadList):
#     data = dataList[i]
#     eachThread = threading.Thread(target=convertPlgToRas, name=f"{threadNameList[i]}", args=(data, outRasPath))
#     threads.append(eachThread)
#     eachThread.start()

convertPlgToRas(dataList[1], outRasPath)