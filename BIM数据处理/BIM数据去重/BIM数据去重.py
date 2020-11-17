import arcpy
import sqlite3
import os
import sys
import datetime

arcpy.env.overwriteOutput = True


def getRunTime(func):
    def _getRunTime(*args, **kwargs):
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        end = datetime.datetime.now()
        return res
    return _getRunTime


# 连接sqlite3
def _connectDB(dbfile):
    conn = sqlite3.connect(dbfile)
    return conn


# 解析创建字段的字典
def _parseFieldDict(fieldDict):
    exp = ""
    for key, value in fieldDict.items():
        field = key + " " + value + ", "
        exp += field

    # 删除最后的空格及逗号
    exp = exp[:-2]
    return exp


# 创建表
def createTable(dbfile, tableName, fieldDict):
    conn = _connectDB(dbfile)
    cur = conn.cursor()
    cur.execute(f"drop table if exists {tableName};")
    fieldExp = _parseFieldDict(fieldDict)
    cur.execute(f"create table if not exists {tableName}({fieldExp});")

    del cur
    del conn

    # 返回 dbName.tableName
    res = os.path.splitext(os.path.basename(dbfile))[0] + "." + tableName
    return res


# 读取
def readFromDB(dbfile, tableName, readField, dupDetFields):
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    fieldExp = "select "
    # 拼接查询语句
    for eachField in readField:
        field = f"{eachField}, "
        fieldExp += field
    fieldExp = fieldExp[:-2] + f" from {tableName}"
    fieldExp_bak = fieldExp
    fieldExp_bak_ = fieldExp

    for n, eachField in enumerate(dupDetFields):
        if n == 0:
            fieldExp += f" where {eachField} >= 2"
        else:
            fieldExp += f" and {eachField} >= 2"

    fieldExp += ";"
    # 查询重复字段值大于2的数据
    res = cur.execute(fieldExp).fetchall()

    # 获取重复的数据
    oidIndex = readField.index("OBJECTID")
    resList = []
    for eachData in res:
        oid = eachData[oidIndex]
        fieldExp_bak += f" where OBJECTID = {oid};"
        # print(fieldExp_bak)
        data = cur.execute(fieldExp_bak).fetchall()
        resList.append(data)
        fieldExp_bak = fieldExp_bak_

    print(res)
    print(resList)
    conn.close()
    del cur
    del conn

    return resList


# 删除重复数据
def getDupData(gdb, dupDataList, bimStructure):
    arcpy.env.workspace = gdb

    # 创建数据重复字典
    keySet = set()
    resDict = {}
    # 每组重复的数据
    for eachDupList in dupDataList:
        # 获取bim结构分类
        nameList = []
        for eachRow in eachDupList:
            fcName = eachRow[1].split("_")[0]
            index = bimStructure.index(fcName)
            nameList.append(index)

        # 数据里留bim结构里最靠前的，index最小的。 此处则是将最小的移除出去，留下剩余的重复的删除掉
        indexMin = nameList.index(min(nameList))
        eachDupListPro = eachDupList
        eachDupListPro.pop(indexMin)

        # 获取重复数据的key，以要素类为key
        for eachData in eachDupListPro:
            dataset = eachData[0]
            fcName = eachData[1]
            oid = eachData[2]
            oid_1 = eachData[3]
            featureClass = os.path.join(gdb, dataset, fcName)
            # 将数据路径设置为字典路径
            resDict.setdefault(featureClass, [])
            # 将数据的 oid 和 oid_1
            resDict[featureClass].append((oid, oid_1))

    print(resDict)
    return resDict


def delDupData(dupDictData):
    for fc, data in dupDictData.items():
        selExp = ""
        for eachValue in data:
            oid = eachValue[0]
            oid_1 = eachValue[1]
            selExp += f"(OBJECTID_1 = {oid} and ObjectId = '{oid_1}') or "
        selExp = selExp[:-4]
        print(selExp)

        print("or is ", selExp.count("or"))
        lyr = arcpy.MakeFeatureLayer_management(fc, "tempLyr")
        arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", selExp)

        print(arcpy.GetCount_management(lyr)[0])
        # arcpy.Delete_management(lyr)


# 检测多面体要素集内各要素类是否存在重复要素
def detDupMul(dbfile, tableName, readField, dupDetFields, bimStructure):
    # 筛选出所有重复的数据
    dupDataList = readFromDB(dbfile, tableName, readField, dupDetFields)

    # 按权重值筛选出重复数据
    resDict = getDupData(gdb, dupDataList, bimStructure)

    # 删除重复数据
    delDupData(resDict)


    # todo 删除后要把数据复制一份，以免出现主键不连续的情况


@getRunTime
def main(dbfile, tableName, fieldDict, gdb, dataset):
    # 创建表
    createTable(dbfile, tableName, fieldDict)

    # 获取数据集
    arcpy.env.workspace = gdb
    datas = arcpy.ListFeatureClasses("", "", dataset)
    print(datas)

    # 迭代读取要素类信息
    conn = sqlite3.connect(dbfile)
    cur_sql = conn.cursor()
    featureSet = dataset
    oidCountList = []
    shpCountList = []
    for eachFC in datas:
        featureClass = eachFC
        with arcpy.da.SearchCursor(eachFC, ["SHAPE@", "OBJECTID_1", "OBJECTID", "Family",
                                            "FamilyType", "Category"]) as cur:
            for row in cur:
                # 获取坐标信息
                shp = row[0]
                (xMin, yMin, zMin,
                 xCen, yCen, zCen,
                 xMax, yMax, zMax) = (round(shp.extent.XMin, 8), round(shp.extent.YMin, 8), round(shp.extent.ZMin, 8),
                                      round(shp.centroid.X, 8), round(shp.centroid.Y, 8), round(shp.centroid.Z, 8),
                                      round(shp.extent.XMax, 8), round(shp.extent.YMax, 8), round(shp.extent.ZMax, 8))

                # 获取其他信息
                oid_1, oid, fmy, fmyType, cat = row[1], row[2], row[3], row[4], row[5]

                if oid is None:
                    oid = "null"

                if fmy is None:
                    fmy = "null"

                if fmyType is None:
                    fmyType = "null"

                if cat is None:
                    cat = "null"

                oidCountList.append(oid)
                oidCount = oidCountList.count(oid)

                shpCoord = (xMin, yMin, zMin, xCen, yCen, zCen, xMax, yMax, zMax)
                shpCountList.append(shpCoord)
                shpCount = shpCountList.count(shpCoord)
                try:
                    cur_sql.execute(f"insert into {tableName} values(null,"
                                    f" '{featureSet}', '{featureClass}', {oid_1}, {oid}, '{fmy}',"
                                    f"'{fmyType}', '{cat}', {xMin}, {yMin}, {zMin}, {xCen}, {yCen},"
                                    f" {zCen}, {xMax}, {yMax}, {zMax}, {oidCount}, {shpCount});")
                except:
                    print(f"insert into {tableName} values(null,"
                          f" '{featureSet}', '{featureClass}', {oid_1}, {oid}, '{fmy}',"
                          f"'{fmyType}', '{cat}', {xMin}, {yMin}, {zMin}, {xCen}, {yCen},"
                          f" {zCen}, {xMax}, {yMax}, {zMax}, {oidCount}, {shpCount});")
                    sys.exit()
                conn.commit()
    del cur_sql
    del conn


if __name__ == "__main__":
    gdb = r"E:\松江管廊\新数据0805\新BIM_1009\处理结果\套合管廊及管线\松江管廊BIM结果数据.gdb"
    dbfile = "./data/mulDupDet.db"
    fieldDict = {
        "ID": "integer primary key autoincrement",
        "FEATURE_SET": "text not null",
        "FEATURE_CLASS": "text not null",
        "OBJECTID_1": "integer",
        "OBJECTID": "integer",
        "FAMILY": "text",
        "FAMILY_TYPE": "text",
        "CATEGORY": "text",
        "X_MIN": "real",
        "Y_MIN": "real",
        "Z_MIN": "real",
        "X_CEN": "real",
        "Y_CEN": "real",
        "Z_CEN": "real",
        "X_MAX": "real",
        "Y_MAX": "real",
        "Z_MAX": "real",
        "OID_COUNT": "integer",
        "SHAPE_DUP": "integer"
    }

    readField = ["FEATURE_SET", "FEATURE_CLASS", "OBJECTID_1", "OBJECTID", "OID_COUNT", "SHAPE_DUP"]
    dupDetFields = ["OID_COUNT", "SHAPE_DUP"]
    bimStructure = ["Pipes", "PipeFitting", "PipeAccessory", "StructuralColumns", "StructuralFraming",
                    "SpecialtyEquipment", "Walls", "Windows", "MechanicalEquipment", "LightingFixtures",
                    "LightingDevices", "Floors", "FireAlarmDevices", "DuctFitting", "ExteriorShape",
                    "ElectricalEquipment", "Ducts", "DuctAccessories", "Doors", "CableTrayFitting",
                    "CableTray", "ConduitFitting", "Conduit", "CurtainWallPanels", "ElectricalFixtures",
                    "SecurityDevices", "Stairs", "StructuralFoundation", "TelephoneDevices", "GenericModel",
                    "ExteriorShell"]
    dataSets = ["白粮路_1", "旗亭路_1_1", "玉阳大道_1"]
    tableNames = ["BLROAD", "QTROAD", "YYROAD"]
    for i, eachSet in enumerate(dataSets):
        # main(dbfile, tableNames[i], fieldDict, gdb, eachSet)
        detDupMul(dbfile, tableNames[i], readField, dupDetFields, bimStructure)
