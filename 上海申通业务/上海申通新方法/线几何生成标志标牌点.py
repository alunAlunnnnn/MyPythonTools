import arcpy
import os
import pandas as pd
import functools

"""
Author: ALun
Create: 2020-11-30
Usage: Generate points in line, include polyline and arc
Porject: SH.ShenTong Metro
"""


arcpy.env.overwriteOutput = True


# 带参装饰器，用于将函数执行时的 arcgis 工作空间和函数外的工作空间隔离开来
# 将需要设置工作空间的函数上加上该装饰器，并将函数整体外再嵌套一层大函数，用于动态传递工作空间即可
def setTempWorkspace(workspace):
    def _inner(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # keep origin workspace
            oriWS = None
            if arcpy.env.workspace:
                oriWS = arcpy.env.workspace

            # set temp workspace
            arcpy.env.workspace = workspace
            res = func(*args, **kwargs)

            try:
                if oriWS:
                    arcpy.env.workspace = oriWS
                else:
                    arcpy.ClearEnvironment("workspace")
            except:
                pass
            return res

        return _wrapper

    return _inner


# auto create a available name for feature classes
def availableDataName(outputPath: str, outputName: str, addExtName: str = None) -> str:
    @setTempWorkspace(outputPath)
    def _wrapper(outputPath: str, outputName: str, addExtName: str = None) -> str:

        # 确定是否有传入 addExtName
        if addExtName is None or addExtName == "":
            addExtName = ""
        else:
            addExtName = "_" + addExtName

        folderType = arcpy.Describe(outputPath).dataType
        if folderType.lower() == "workspace":
            if outputName[-4:] == ".shp":
                outputName = outputName[:-4] + addExtName
            else:
                outputName = outputName + addExtName
        # .sde like directory
        elif folderType.lower() == "file":
            if outputName[-4:] == ".shp":
                outputName = outputName[:-4] + addExtName
            else:
                outputName = outputName + addExtName

        else:
            if not outputName[-4:] == ".shp":
                outputName = outputName + addExtName + ".shp"
            else:
                outputName = outputName[:-4] + addExtName + ".shp"

        return os.path.join(outputPath, outputName)

    res = _wrapper(outputPath, outputName, addExtName)
    return res


def _copyFeature(inFC: str, outputPath: str, outputName: str, addExtName: str="") -> str:
    oriEnvQFName = arcpy.env.qualifiedFieldNames
    arcpy.env.qualifiedFieldNames = False

    if addExtName is None or addExtName == "":
        addExtName = ""
    else:
        addExtName = "_" + addExtName

    # keep origin workspace
    oriWS = None
    if arcpy.env.workspace:
        oriWS = arcpy.env.workspace

    folderType = arcpy.Describe(outputPath).dataType
    if folderType.lower() == "workspace":
        if outputName[-4:] == ".shp":
            outputName = outputName[:-4] + addExtName
        else:
            outputName = outputName + addExtName
    # .sde like directory
    elif folderType.lower() == "file":
        if outputName[-4:] == ".shp":
            outputName = outputName[:-4] + addExtName
        else:
            outputName = outputName + addExtName

    else:
        if not outputName[-4:] == ".shp":
            outputName = outputName + addExtName + ".shp"
        else:
            outputName = outputName[:-4] + addExtName + ".shp"

    arcpy.CopyFeatures_management(inFC, os.path.join(outputPath, outputName))

    try:
        if oriWS:
            arcpy.env.workspace = oriWS
        else:
            arcpy.ClearEnvironment("workspace")
    except:
        pass

    arcpy.env.qualifiedFieldNames = oriEnvQFName
    return os.path.join(outputPath, outputName)


def readMileFromExcel_Pandas(inExcelFile, headerRow, dirHeaderName, selectHeaderList):
    """

    :param inExcelFile: str, 输入xls或xlsx文件路径
    :param headerRow: int, excel数据中表头开始的行索引，第一行为0。 表头以上的行会被忽略
    :param selectHeaderList: list, 要提取的信息的列名（非索引）的列表
    :return:
    """
    # 确保输入表头索引非其他类型
    headerRow = int(headerRow)

    # 从excel中读取数据
    df = pd.read_excel(inExcelFile, header=headerRow, index=False)
    print(df)
    # 迭代每一行，获取里程值和序号值
    rowDataDict = {}
    for row in df.iterrows():
        data = row[1]
        dataDir = data[dirHeaderName]

        rowDataList = []
        rowDataDict.setdefault(dataDir, [])
        for eachHeader in selectHeaderList:
            rowDataList.append(data[eachHeader])
        rowDataDict[dataDir].append(rowDataList)
    print(rowDataDict)
    return rowDataDict


def createFeatureClass(outputPath, outputName, wkid=None, wkt=None):
    if wkid:
        sr = arcpy.SpatialReference(wkid)
    elif wkt:
        sr = arcpy.SpatialReference()
        sr.loadFromString(wkt)
    else:
        sr = None

    data = arcpy.CreateFeatureclass_management(outputPath, outputName, "POINT", spatial_reference=sr)
    arcpy.AddField_management(data, "GEOMILE", "DOUBLE")
    arcpy.AddField_management(data, "ORI_OID", "LONG")

    return os.path.join(outputPath, outputName)


#
def generatePntFC(lineFC, lineFCDirFieldName, newPntFieldName, mileDataDict, outputPath, outputName, wkid=None, wkt=None):
    # 若输入 wkid 或 wkt 则根据其生成具有坐标系的数据，否则生成无坐标系要素类
    resDataName = availableDataName(outputPath, outputName, "_split")
    outputPathSplitPnt = os.path.dirname(resDataName)
    outputNameSplitPnt = os.path.basename(resDataName)

    if wkid:
        newPntFC = createFeatureClass(outputPathSplitPnt, outputNameSplitPnt, wkid=wkid)
    elif wkt:
        newPntFC = createFeatureClass(outputPathSplitPnt, outputNameSplitPnt, wkt=wkt)
    else:
        newPntFC = createFeatureClass(outputPathSplitPnt, outputNameSplitPnt)

    # 获取线要素的几何
    with arcpy.da.SearchCursor(lineFC, ["SHAPE@", lineFCDirFieldName]) as scur:
        with arcpy.da.InsertCursor(newPntFC, ["SHAPE@", *newPntFieldName]) as icur:
            for srow in scur:
                # 获取线几何
                lineGeo = srow[0]
                # 获取线走向字段的值（上行/下行）
                lineDir = srow[1]
                print(lineDir)
                # 获取上行/下行的标牌点
                mileGenList = mileDataDict[lineDir]

                for eachMile in mileGenList:
                    # 按照里程值生成点几何
                    milePntGeo = lineGeo.positionAlongLine(eachMile[1], False)

                    # 插入几何、序号、里程值
                    icur.insertRow([milePntGeo, eachMile[0], eachMile[1]])

    return resDataName


#
def attrJoin(inFC, inXlsx, sheetName):
    lyr = arcpy.MakeFeatureLayer_management(inFC, os.path.basename(inFC) + "_tmpLyr")

    xlsxExt = os.path.splitext(inXlsx)[1]
    if xlsxExt == ".xls" or xlsxExt == ".xlsx":
        tView = arcpy.MakeTableView_management(inXlsx + "/" + sheetName + "$", os.path.basename(inXlsx).strip(xlsxExt) + "_tmpTV")

    lyr = arcpy.AddJoin_management(lyr, "ORI_OID", tView, "序号")


    fcBaseName = os.path.basename(inFC)
    fcDir = os.path.dirname(inFC)
    newLyr = _copyFeature(lyr, fcDir, fcBaseName, "new")
    print(newLyr)
    return newLyr


data = r"F:\工作项目\项目_上海申通\数据_加点新_20201130\数据_excel\标志标牌修改_20201201.xlsx"
sheetName = "Sheet1"

# excel中表头所在的行，表头之上的行会被全部忽略掉。 从 0 开始
headerRow = 0

# 方向字段的表头名
dirHeaderName = "行别/股道"

# 需要提取的值的表头名， 如 ["序号", "修正后里程值"]
selectHeaderList = ["序号", "修正后里程值"]
newPntFieldName = ["ORI_OID", "GEOMILE"]

# 输入线要素类（可以有曲线）
lineFC = r"F:\工作项目\项目_上海申通\数据_加点新_20201130\处理_数据生成\数据_中间数据\检测数据\DATA.gdb\zhengxian_ori"

# 线要素类中的 上下行字段名
lineFCDirFieldName = "行别"

# 输出数据的位置及数据名
outputPath = r"F:\工作项目\项目_上海申通\数据_加点新_20201130\处理_数据生成\数据_中间数据\标识标牌_20201201"
outputName = "标志标牌点"

# 坐标定义文本
wkt = 'PROJCS["shanghaicity",GEOGCS["GCS_Beijing_1954",DATUM["D_Beijing_1954",SPHEROID["Krasovsky_1940",6378245.0,298.3]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",-3457147.81],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",121.2751921],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'


mileDataDict = readMileFromExcel_Pandas(data, headerRow, dirHeaderName, selectHeaderList)

pntFC = generatePntFC(lineFC, lineFCDirFieldName, newPntFieldName, mileDataDict, outputPath, outputName, wkt=wkt)

attrJoin(pntFC, data, sheetName)