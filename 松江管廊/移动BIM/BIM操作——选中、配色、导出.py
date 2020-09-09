import arcpy
import os

aprx = arcpy.mp.ArcGISProject("CURRENT")
mapList = aprx.listMaps("Scene")
lyrList = mapList[0].listLayers()

outputPath = r"E:\松江管廊\新数据0805\管廊BIM数据位置移动\lyr"
for each in lyrList:
    desc = arcpy.Describe(each)
    eachName = each.name
    print(desc.dataType)
    if desc.dataType == "FeatureLayer":
        arcpy.SaveToLayerFile_management(each, os.path.join(outputPath, eachName))

arcpy.env.workspace = r"E:\松江管廊\新数据0805\管廊BIM数据位置移动\GL_BIM.gdb\bim2gis_1_1_Project"
dataList = arcpy.ListFeatureClasses()
for each in dataList:
    arcpy.RecalculateFeatureClassExtent_management(each)

# 保存为图层文件
aprx = arcpy.mp.ArcGISProject("CURRENT")
mapList = aprx.listMaps("Scene")
lyrList = mapList[0].listLayers()

outputPath = r"E:\松江管廊\新数据0805\管廊BIM数据位置移动\lyr"
for each in lyrList:
    desc = arcpy.Describe(each)
    eachName = each.name
    print(desc.dataType)
    if desc.dataType == "FeatureLayer":
        arcpy.SaveToLayerFile_management(each, os.path.join(outputPath, eachName))

import os

# 应用图层文件
aprx = arcpy.mp.ArcGISProject("CURRENT")
mapList = aprx.listMaps("Scene1")
lyrList = mapList[0].listLayers()

outputPath = r"E:\松江管廊\新数据0805\管廊BIM数据位置移动\lyr"
for each in lyrList:
    desc = arcpy.Describe(each)
    eachName = each.name
    print(desc.dataType)
    if desc.dataType == "FeatureLayer":
        arcpy.ApplySymbologyFromLayer_management(each, os.path.join(outputPath, "touming.lyrx"))
        # arcpy.SaveToLayerFile_management(each, os.path.join(outputPath, eachName))

# BIM配色
import os

aprx = arcpy.mp.ArcGISProject("CURRENT")
mapList = aprx.listMaps("Scene1")
lyrList = mapList[0].listLayers()

outputPath = r"E:\松江管廊\新数据0805\管廊BIM数据位置移动\lyr"
for each in lyrList:
    desc = arcpy.Describe(each)
    eachName = each.name
    print(desc.dataType)
    if desc.dataType == "FeatureLayer":
        arcpy.ApplySymbologyFromLayer_management(each, os.path.join(outputPath, eachName + ".lyrx"))

# 管廊监控点配色
mapping = {'超声波液位仪': 0, '防爆型含氧量检测': 1, '防爆型红外入侵': 2, '防爆型摄像机': 3,
           '防爆型声光报警': 4, '防爆型温湿度检测': 5, '含氧量检测': 6, '红外入侵': 7, '甲烷检测': 8,
           '硫化氢检测': 9, '摄像机': 10, '声光报警': 11, '温湿度检测': 12, '自动液压井盖': 13}
def f(a):
    return mapping[a]


# 删除损坏数据源
aprx = arcpy.mp.ArcGISProject("CURRENT")
mapList = aprx.listMaps()
map1 = mapList[0]
brklyrs = aprx.listBrokenDataSources()
for eachBrk in brklyrs:
    map1.removeLayer(eachBrk)
