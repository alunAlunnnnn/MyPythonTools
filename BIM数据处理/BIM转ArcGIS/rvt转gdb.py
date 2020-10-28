import arcpy
import os
fileDir = r"E:\松江管廊\新数据0805\新BIM_1009\数据筛选后\白粮路"
dataList = []
for eachRoot, eachDir, eachFile in os.walk(fileDir):
    # print(eachFile)
    for each in eachFile:
        if each[-4:] == ".rvt":
            dataList.append(os.path.join(eachRoot, each))
print(dataList)
print(len(dataList))
arcpy.conversion.BIMFileToGeodatabase(dataList, r"D:\Users\lyce\Documents\ArcGIS\Projects\管廊BIM\白粮路_BIM2GIS.gdb", "白粮路")