import os, arcpy

arcpy.env.overwriteOutput = True

# dataList = ["tin_1", "tin_2", "tin_3", "tin_4", "tin_5", "tin_6", "tin_7"]
# boundry = r"E:\地质点\钻孔数据\process\process.gdb\boundry_pro"
# outPutGDB = r'E:\地质点\钻孔数据\pro_process\拉伸结果\result.gdb'


dataList = arcpy.GetParameter(0)
boundry = arcpy.GetParameterAsText(1)
outputName = arcpy.GetParameterAsText(2)
outPutGDB = arcpy.GetParameterAsText(3)

arcpy.env.workspace = outPutGDB

maxPro = len(dataList)
arcpy.SetProgressor('step', 'powerd by hispatial GIS', 0, maxPro)

i = 0
j = 1
while j < maxPro:
    # get tin layer or feature class
    tin1 = dataList[i]
    tin2 = dataList[j]

    # get tin name from tin catalogPath
    tinData1 = os.path.basename(arcpy.Describe(tin1).catalogPath)
    tinData2 = os.path.basename(arcpy.Describe(tin2).catalogPath)

    # get reult name from tin name
    if '_' in tinData1:
        if '_' in tinData2:
            data = tinData1.split('_')[-1] + '_' + tinData2.split('_')[-1]
        else:
            data = tinData1.split('_')[-1] + '_' + str(j)
    else:
        if '_' in tinData2:
            data = tinData2.split('_')[-1] + '_' + str(j)
        else:
            data = str(j)

    outFC = os.path.join(outPutGDB, outputName + '_' + data.replace(' ', '').replace('-', '_'))
    if arcpy.Exists(outFC):
        arcpy.Delete_management(outFC)
    arcpy.ddd.ExtrudeBetween(tin1, tin2, boundry, outFC)
    i += 1
    j += 1
    arcpy.SetProgressorPosition()




# def f(a):
#     a = a[:1]
#     if a == "①":
#         return 1
#     elif a == "②":
#         return 2
#     elif a == "③":
#         return 3
#     elif a == "④":
#         return 4
#     elif a == "⑤":
#         return 5
#     elif a == "⑥":
#         return 6
#     elif a == "⑦":
#         return 7
#     elif a == "1":
#         return 1
#     elif a == "2":
#         return 2
#     else:
#         return None
