import arcpy
import os
import pandas as pd
import functools
import datetime

"""
Author: ALun
Create: 2020-11-30
Usage: Generate points in line, include polyline and arc
Porject: SH.ShenTong Metro
"""

arcpy.env.overwriteOutput = True


class NoSplitPntError(Exception):
    pass


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


def _addField(infc, fieldName, fieldType):
    try:
        arcpy.AddField_management(infc, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(infc, fieldName)
        arcpy.AddField_management(infc, fieldName, fieldType)


def _copyFeature(inFC: str, outputPath: str, outputName: str, addExtName: str = "") -> str:
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


@getRunTime
def readMileFromExcel_Pandas(inExcelFile, headerRow, dirHeaderName, selectHeaderList, sheetName):
    """

    :param inExcelFile: str, 输入xls或xlsx文件路径
    :param headerRow: int, excel数据中表头开始的行索引，第一行为0。 表头以上的行会被忽略
    :param selectHeaderList: list, 要提取的信息的列名（非索引）的列表
    :return:
    """
    # 确保输入表头索引非其他类型
    headerRow = int(headerRow)

    # 从excel中读取数据
    df = pd.read_excel(inExcelFile, header=headerRow, index=False, sheet_name=sheetName)
    print(df)

    rowDataDict = {}
    for row in df.iterrows():
        data = row[1]

        # 获取方向值
        dataDir = data[dirHeaderName]

        # 获取每行的
        rowDataList = []
        rowDataDict.setdefault(dataDir, [])
        for eachHeader in selectHeaderList:
            rowDataList.append(data[eachHeader])
        rowDataDict[dataDir].append(rowDataList)
    print(rowDataDict)
    return rowDataDict


def createFeatureClass(outputPath, outputName, createField, wkid=None, wkt=None):
    if wkid or wkt:
        if wkid:
            sr = arcpy.SpatialReference(wkid)
        else:
            sr = arcpy.SpatialReference()
            sr.loadFromString(wkt)

        data = arcpy.CreateFeatureclass_management(outputPath, outputName, "POINT", spatial_reference=sr)
    else:
        data = arcpy.CreateFeatureclass_management(outputPath, outputName, "POINT")

    # 添加所需字段
    for eachField in createField:
        _addField(data, eachField[0], eachField[1])

    return os.path.join(outputPath, outputName)


def generatePntFC(lineFC, lineFCDirFieldName, newPntFieldName, mileDataDict, outputPath, outputName, wkid=None,
                  wkt=None):
    global tempDataList, idIndex, startMileIndex, endMileIndex, midMileIndex, createFieldAttr, createFieldSplit, dirIndex
    # 生成切分点
    resSplitPnt = availableDataName(outputPath, outputName, "_split")
    outputPathSplitPnt = os.path.dirname(resSplitPnt)
    outputNameSplitPnt = os.path.basename(resSplitPnt)

    # 生成属性连接点
    resAttrPnt = availableDataName(outputPath, outputName, "_attr")
    outputPathAttrPnt = os.path.dirname(resAttrPnt)
    outputNameAttrPnt = os.path.basename(resAttrPnt)

    # 若输入 wkid 或 wkt 则根据其生成具有坐标系的数据，否则生成无坐标系要素类
    if wkid:
        newPntFC = createFeatureClass(outputPathSplitPnt, outputNameSplitPnt, createFieldSplit, wkid=wkid)
        newAttrFC = createFeatureClass(outputPathAttrPnt, outputNameAttrPnt, createFieldAttr, wkid=wkid)
    elif wkt:
        newPntFC = createFeatureClass(outputPathSplitPnt, outputNameSplitPnt, createFieldSplit, wkt=wkt)
        newAttrFC = createFeatureClass(outputPathAttrPnt, outputNameAttrPnt, createFieldAttr, wkt=wkt)
    else:
        newPntFC = createFeatureClass(outputPathSplitPnt, outputNameSplitPnt, createFieldSplit)
        newAttrFC = createFeatureClass(outputPathAttrPnt, outputNameAttrPnt, createFieldAttr)

    # 收集临时数据
    tempDataList += [newPntFC, newAttrFC]

    # 给分割点添加每个点自己的里程值
    _addField(newPntFC, "PMILE", "DOUBLE")
    _addField(newAttrFC, "PMILE", "DOUBLE")


    # 获取线要素的几何，以便生成分割点
    with arcpy.da.SearchCursor(lineFC, ["SHAPE@", lineFCDirFieldName]) as scur:
        with arcpy.da.InsertCursor(newPntFC, ["SHAPE@", *newPntFieldName, "PMILE"]) as icur:
            for srow in scur:
                # 获取线几何
                lineGeo = srow[0]
                # 获取线走向字段的值（上行/下行）
                lineDir = srow[1]
                print(lineDir)
                # 获取上行/下行的标牌点
                mileGenList = mileDataDict[lineDir]

                for eachMile in mileGenList:
                    # 插入起点里程值

                    # 按照里程值生成点几何
                    milePntGeo = lineGeo.positionAlongLine(eachMile[startMileIndex], False)

                    # 插入几何、序号、里程值
                    icur.insertRow([milePntGeo, eachMile[idIndex], eachMile[dirIndex], eachMile[startMileIndex], eachMile[endMileIndex],
                                    eachMile[midMileIndex], eachMile[startMileIndex]])

                    # 插入终点里程值
                    # 按照里程值生成点几何
                    milePntGeo = lineGeo.positionAlongLine(eachMile[endMileIndex], False)

                    # 插入几何、序号、里程值
                    icur.insertRow([milePntGeo, eachMile[idIndex], eachMile[dirIndex], eachMile[startMileIndex],
                                    eachMile[endMileIndex], eachMile[midMileIndex], eachMile[endMileIndex]])

            del srow

    # 按中间点里程值生成点，以便挂接属性
    with arcpy.da.SearchCursor(lineFC, ["SHAPE@", lineFCDirFieldName]) as scur:
        with arcpy.da.InsertCursor(newAttrFC, ["SHAPE@", *newPntFieldName, "PMILE"]) as icur:
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
                    milePntGeo = lineGeo.positionAlongLine(eachMile[midMileIndex], False)

                    # 插入几何、序号、里程值
                    icur.insertRow([milePntGeo, eachMile[idIndex], eachMile[dirIndex], eachMile[startMileIndex],
                                    eachMile[endMileIndex], eachMile[midMileIndex], eachMile[midMileIndex]])

    # 删除重复点
    arcpy.DeleteIdentical_management(newPntFC, ["DIRECTORY", "PMILE"])
    arcpy.DeleteIdentical_management(newAttrFC, ["DIRECTORY", "PMILE"])


    # 返回两个数据路径，第一个切分点，第二个属性点
    return resSplitPnt, resAttrPnt


#
def attrJoin(inFC, inXlsx, sheetName, extName, idFiledName):
    global tempDataList, joinAttrToSingleLine

    lyr = arcpy.MakeFeatureLayer_management(inFC, os.path.basename(inFC) + "_tmpLyr")

    if joinAttrToSingleLine:
        print("连接")
        xlsxExt = os.path.splitext(inXlsx)[1]
        if xlsxExt == ".xls" or xlsxExt == ".xlsx":
            tView = arcpy.MakeTableView_management(inXlsx + "/" + sheetName + "$",
                                                   os.path.basename(inXlsx).strip(xlsxExt) + "_tmpTV")

        lyr = arcpy.AddJoin_management(lyr, sheetName, tView, idFiledName)
    else:
        print("不连接")
    # 复制连接属性表后的数据
    fcBaseName = os.path.basename(inFC)
    fcDir = os.path.dirname(inFC)
    newLyr = _copyFeature(lyr, fcDir, fcBaseName, extName)

    tempDataList.append(newLyr)

    return newLyr


def splitLine(inLineFC, inSplitPnt, inAttrPnt, outputPath, outputName, extName, tolerance):
    global tempDataList, joinAttrToSingleLine
    # 分割线
    splitLine = availableDataName(outputPath, outputName, "_split_tmp")
    splitLyr = arcpy.SplitLineAtPoint_management(inLineFC, inSplitPnt, splitLine, tolerance)

    tempDataList.append(splitLine)

    # 连接属性
    resLine = availableDataName(outputPath, outputName, extName)
    arcpy.SpatialJoin_analysis(splitLyr, inAttrPnt, resLine, search_radius=tolerance)

    # # 参数控制是否将每个excel的属性表传入到线要素类中
    # if joinAttrToSingleLine:
    #     # 分割线
    #     splitLine = availableDataName(outputPath, outputName, "_split_tmp")
    #     splitLyr = arcpy.SplitLineAtPoint_management(inLineFC, inSplitPnt, splitLine, tolerance)
    #
    #     tempDataList.append(splitLine)
    #
    #     # 连接属性
    #     resLine = availableDataName(outputPath, outputName, extName)
    #     arcpy.SpatialJoin_analysis(splitLyr, inAttrPnt, resLine, search_radius=tolerance)
    #
    # # 不传入excel的属性表，则仅切分线要素类
    # else:
    #     # 分割线
    #     splitLine = availableDataName(outputPath, outputName, extName)
    #     resLine = arcpy.SplitLineAtPoint_management(inLineFC, inSplitPnt, splitLine, tolerance)

    return resLine


def clearTempData():
    global tempDataList
    try:
        arcpy.Delete_management(tempDataList)
    except:
        for each in tempDataList:
            try:
                arcpy.Delete_management(each)
            except:
                pass
    finally:
        print("程序运行完成")


def splitTotalLine(inLineFC, splitPntList, singleLineList, outputPath, outputName):
    global tempDataList, lineFCDirFieldName

    # 合并传入的分割点
    if len(splitPntList) == 0:
        print("没有分割点被传入")
        raise NoSplitPntError
    elif len(splitPntList) == 1:
        splitPnt = splitPntList[0]
    else:
        splitPntData = availableDataName(outputPath, outputName, "_splitPnt")
        splitPnt = arcpy.Merge_management(splitPntList, splitPntData)

        tempDataList.append(splitPntData)

    # 分割线
    resSplitLine = availableDataName(outputPath, outputName, "_splited_noattr")
    arcpy.SplitLineAtPoint_management(inLineFC, splitPnt, resSplitLine, search_radius=tolerance)

    tempDataList.append(resSplitLine)

    # 迭代每根单层线以空间连接的方式连接属性
    for i, eachLine in enumerate(singleLineList):

        # # 线转点
        # line2pnt = availableDataName(outputPath, outputName, f"lint2pnt{i}")
        # eachLine = arcpy.FeatureToPoint_management(eachLine, line2pnt, "INSIDE")
        # tempDataList.append(line2pnt)

        # 创建字段映射，只保留标识性ID
        fms = arcpy.FieldMappings()

        idFieldsList = [eachField.name for eachField in arcpy.ListFields(eachLine)
                         if eachField.name in sheetList]
        for eachField in idFieldsList:
            fm = arcpy.FieldMap()
            fm.mergeRule = 'Sum'
            fm.addInputField(eachLine, eachField)
            fms.addFieldMap(fm)

        # 并非第一次做空间连接时，后一次用前一次的结果
        if i != 0:
            resSplitLine = joined

            idFieldsListPre = [eachField.name for eachField in arcpy.ListFields(resSplitLine)
                            if eachField.name in sheetList]
            for eachField in idFieldsListPre:
                fm = arcpy.FieldMap()
                fm.mergeRule = 'Sum'
                fm.addInputField(resSplitLine, eachField)
                fms.addFieldMap(fm)

        # 方向字段做字段映射
        dirFm = arcpy.FieldMap()
        dirFm.mergeRule = 'First'
        dirFm.addInputField(resSplitLine, lineFCDirFieldName)
        fms.addFieldMap(dirFm)

        joined = availableDataName(outputPath, outputName, f"_temp{i}")
        arcpy.SpatialJoin_analysis(resSplitLine, eachLine, joined, field_mapping=fms, match_option="WITHIN")

        tempDataList.append(joined)

    # 赋值完属性后的线，新建两个字段 起始里程和终止里程
    _addField(joined, "SMILE", "DOUBLE")
    _addField(joined, "EMILE", "DOUBLE")

    # 计算全部打断后线的实际 起始里程 和 终止里程
    with arcpy.da.SearchCursor(inLineFC, ["SHAPE@", lineFCDirFieldName]) as oCur:
        with arcpy.da.UpdateCursor(joined, ["SHAPE@", lineFCDirFieldName, "SMILE", "EMILE"]) as tCur:
            for oRow in oCur:
                # 线几何
                oLineGeo = oRow[0]
                # 线方向
                oLineDir = oRow[1]

                for tRow in tCur:
                    # 获取点方向
                    tDir = tRow[1]
                    # 点线同向则求距离
                    if tDir == oLineDir:
                        # 点几何
                        sPnt = tRow[0].firstPoint
                        ePnt = tRow[0].lastPoint

                        disSPnt = oLineGeo.measureOnLine(sPnt)
                        disEPnt = oLineGeo.measureOnLine(ePnt)

                        tRow[2] = disSPnt
                        tRow[3] = disEPnt

                        tCur.updateRow(tRow)
                tCur.reset()

    # 将全部打断线 连接所有单段线属性后，复制一份出来
    _copyFeature(joined, outputPath, outputName)



data = r"F:\工作项目\项目_上海申通\数据_excel打断线_20201201\输入数据\new\地铁正线分段表序号1202(2).xls"
sheetList = ["VERT_ID", "CUR_ID", "LOT_ID", "ACO_ID", "SLO_ID", "GUA_ID"]
# sheetList = ["VERT_ID"]

# excel中表头所在的行，表头之上的行会被全部忽略掉。 从 0 开始
headerRow = 0

# 方向字段的表头名
dirHeaderName = "行别"

# 需要提取的值的表头名， 如 ["序号", "修正后里程值"]
idFiledName = "序列"
# selectHeaderList = ["序列", "实际起点里程", "实际终点里程", "实际中间点里程"]
# newPntFieldName = ["ORI_OID", "SGEOMILE", "EGEOMILE", "MGEOMILE"]
# newPntFieldType = ["LONG", "DOUBLE", "DOUBLE", "DOUBLE"]

# 起始里程在 newPntFieldName 列表中所处的索引
idIndex = 0
dirIndex = 1
startMileIndex = 2
endMileIndex = 3
midMileIndex = 4

# 输入线要素类（可以有曲线）
lineFC = r"F:\工作项目\项目_上海申通\数据_加点新_20201130\处理_数据生成\数据_中间数据\检测数据\DATA.gdb\zhengxian_ori"

# 线要素类中的 上下行字段名
lineFCDirFieldName = "行别"

# 输出数据的位置及数据名
outputPath = r"F:\工作项目\项目_上海申通\数据_excel打断线_20201201\中间数据\修正后数据1202.gdb"
# outputPath = r"F:\工作项目\项目_上海申通\数据_excel打断线_20201201\中间数据\vertid.gdb"
# outputName = "打断线"
finalDataName = "全部打断测试"

# 坐标定义文本
wkt = 'PROJCS["shanghaicity",GEOGCS["GCS_Beijing_1954",DATUM["D_Beijing_1954",SPHEROID["Krasovsky_1940",6378245.0,298.3]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",-3457147.81],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",121.2751921],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

# 搜索容差
tolerance = 0.01

#
joinAttrToSingleLine = True

# 删除临时数据
tempDataList = []
splitPntList = []
singleLineList = []

for sheetName in sheetList:
    outputName = sheetName

    selectHeaderList = ["序列", "行别", "实际起点里程", "实际终点里程", "实际中间点里程"]
    newPntFieldName = [sheetName, "DIRECTORY", "SGEOMILE", "EGEOMILE", "MGEOMILE"]
    newPntFieldType = ["LONG", "TEXT", "DOUBLE", "DOUBLE", "DOUBLE"]

    extName = "_temp"
    extNameFinal = ""

    # 生成器
    createFieldSplit = zip(newPntFieldName, newPntFieldType)
    createFieldAttr = zip(newPntFieldName, newPntFieldType)

    # 从 excel 读取数据，并格式化为 json
    mileDataDict = readMileFromExcel_Pandas(data, headerRow, dirHeaderName, selectHeaderList, sheetName)

    # 沿线生成分割点和属性连接点
    splitPnt, attrPnt = generatePntFC(lineFC, lineFCDirFieldName, newPntFieldName, mileDataDict, outputPath, outputName,
                                      wkt=wkt)

    # 将excel属性挂接给属性连接点
    inAttrPnt = attrJoin(attrPnt, data, sheetName, extName, idFiledName)

    # 依照每个 sheet 拆分线，并连接属性
    singleLine = splitLine(lineFC, splitPnt, inAttrPnt, outputPath, outputName, extNameFinal, tolerance)

    # 保存每条线的切分点
    splitPntList.append(splitPnt)

    # 保存每条单段线做属性连接
    singleLineList.append(singleLine)

# 使用其他所有线的分割点，将线整体切碎
splitTotalLine(lineFC, splitPntList, singleLineList, outputPath, finalDataName)

clearTempData()


# # 增加全分割后的配色字段

# def fillSymbol(fieldDict):
#     sym = ""
#     for eachFieldName, eachFIeldValue in fieldDict.items():
#         if eachFIeldValue is not None:
#             sym = sym + eachFieldName[:3] + "_"
#     return sym[:-1]
#
# fillSymbol({"GUA_ID": !GUA_ID!, "SLO_ID": !SLO_ID!, "ACO_ID": !ACO_ID!, "LOT_ID": !LOT_ID!, "CUR_ID": !CUR_ID!, "VERT_ID": !VERT_ID!})
# {"GUA_ID": !GUA_ID!, "SLO_ID": !SLO_ID!, "ACO_ID": !ACO_ID!, "LOT_ID": !LOT_ID!, "CUR_ID": !CUR_ID!, "VERT_ID": !VERT_ID!}