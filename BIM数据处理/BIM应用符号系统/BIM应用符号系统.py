# 应用图层文件，应用到现在的数据

import arcpy
import os

outLyrDir = r"F:\工作项目\项目_松江管廊\代码_保存BIM图层样式\lyr文件 - 副本"

aprx = arcpy.mp.ArcGISProject("CURRENT")
scene = aprx.listMaps("Scene5")[0]
lyrs = scene.listLayers()

for eachLyr in lyrs:
    lyrName = eachLyr.name
    if eachLyr.isFeatureLayer:
        try:
            arcpy.ApplySymbologyFromLayer_management(eachLyr, os.path.join(outLyrDir, lyrName + ".lyrx"))
        except:
            print(f"Apply symbol erro in {lyrName}")
        # arcpy.SaveToLayerFile_management(eachLyr, os.path.join(outLyrDir, lyrName))





# 保存至图层文件，从管廊DEMO的数据里保存

import arcpy
import os

outLyrDir = r"F:\工作项目\项目_松江管廊\代码_保存BIM图层样式\lyr文件 - 副本"

aprx = arcpy.mp.ArcGISProject("CURRENT")
scene = aprx.listMaps("Scene2")[0]
lyrs = scene.listLayers()

for eachLyr in lyrs:
    lyrName = eachLyr.name
    if eachLyr.isFeatureLayer:
        arcpy.SaveToLayerFile_management(eachLyr, os.path.join(outLyrDir, lyrName))