import arcpy
import os
fileDir = r"E:\松江管廊\新数据0805\新BIM_1009\松江管廊模型数据\unpack\001模型文件夹\模型文件夹\003玉阳大道文件夹_68个\3_玉阳大道节点_预埋件&出图"
dataList = []
for eachRoot, eachDir, eachFile in os.walk(fileDir):
    # print(eachFile)
    for each in eachFile:
        if each[-4:] == ".rvt":
            dataList.append(os.path.join(eachRoot, each))
print(dataList)
print(len(dataList))
arcpy.conversion.BIMFileToGeodatabase(dataList, "E:\松江管廊\新数据0805\新BIM_1009\数据处理\BIM转GIS\BIM入GIS.gdb", "玉阳大道_part1")