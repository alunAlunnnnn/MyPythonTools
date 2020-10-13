import arcpy
import os

arcpy.env.overwriteOutput = True


# 获取bim数据的结构名称
def getAllDataSets(gdb, name):
    resSet = set()
    arcpy.env.workspace = gdb
    dsats = arcpy.ListDatasets("*" + name + "*")
    for eachDataSets in dsats:
        datas = arcpy.ListFeatureClasses("", "", eachDataSets)
        for each in datas:
            print(each)
            if "Floorplan_Polyline" not in each and "Floorplan_Polygon" not in each:
                name = each.split("_")[0]
            else:
                name = each.split("_")[0] + "_" + each.split("_")[1]

            if name != "Floorplan_Polyline" and name != "Floorplan_Polygon":
                resSet.add(name)
            elif name == "Floorplan_Polyline":
                resSet.add("Floorplan_Polyline")
            elif name == "Floorplan_Polygon":
                resSet.add("Floorplan_Polygon")
    return resSet


def createDataSet(gdb, outputName):
    res = arcpy.CreateFeatureDataset_management(gdb, outputName)
    return res


def mergeBIMData(gdb, name, dSets, outputName):
    # 创建要素数据集
    createDataSet(gdb, outputName)
    dataSet = os.path.join(gdb, outputName)

    arcpy.env.workspace = gdb
    dsats = arcpy.ListDatasets("*" + name + "*")
    # 每个BIM数据结构名
    for eachName in dSets:
        print(eachName)
        print(f"{list(dSets).index(eachName)}/{len(dSets)}")
        mergeDataList = []
        # gdb中的每个数据集
        for eachSet in dsats:
            # 拆分后的数据集
            datas = arcpy.ListFeatureClasses("", "", eachSet)
            # 找到符合结构的数据
            for eachFC in datas:
                if eachName in eachFC:
                    mergeDataList.append(eachFC)

        # 合并数据
        arcpy.Merge_management(mergeDataList, os.path.join(dataSet, eachName + f"_{outputName}"))



def appendBIMData(gdb, name, dSets):
    # 创建要素数据集
    # createDataSet(gdb, outputName)
    # dataSet = os.path.join(gdb, outputName)

    arcpy.env.workspace = gdb
    dsats = arcpy.ListDatasets("*" + name + "*")
    dsats.remove("玉阳大道_part2")
    # 每个BIM数据结构名
    for eachName in dSets:
        print(eachName)
        print(f"{list(dSets).index(eachName)}/{len(dSets)}")
        mergeDataList = []
        # gdb中的每个数据集
        for eachSet in dsats:
            # 拆分后的数据集
            datas = arcpy.ListFeatureClasses("", "", eachSet)
            # 找到符合结构的数据
            for eachFC in datas:
                if eachName in eachFC:
                    mergeDataList.append(eachFC)

        # 合并数据
        try:
            arcpy.Append_management(mergeDataList, os.path.join(gdb, "玉阳大道_part2", eachName + "_玉阳大道_part2"), "NO_TEST")
        except:
            pass


def main(gdb, name, outputName):
    dSets = getAllDataSets(gdb, name)

    # 将拆分的BIM数据合并
    # mergeBIMData(gdb, name, dSets, outputName)

    # 将其他BIM部分追加到当前数据中
    appendBIMData(gdb, name, dSets)


gdb = r"E:\松江管廊\新数据0805\新BIM_1009\数据处理\BIM转GIS\BIM入GIS.gdb"
name = "玉阳大道"
outputName = "mmm"

main(gdb, name, outputName)
