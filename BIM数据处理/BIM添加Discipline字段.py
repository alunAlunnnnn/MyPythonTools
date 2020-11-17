import arcpy
import json
import os

gdb = r"E:\松江管廊\新数据0805\新BIM_1009\数据处理\BIM转GIS\BIM入GIS.gdb"
bll = r"E:\松江管廊\新数据0805\新BIM_1009\数据处理\BIM转GIS\BIM入GIS.gdb\白粮路"
qtl = r"E:\松江管廊\新数据0805\新BIM_1009\数据处理\BIM转GIS\BIM入GIS.gdb\旗亭路"
yydd = r"E:\松江管廊\新数据0805\新BIM_1009\数据处理\BIM转GIS\BIM入GIS.gdb\玉阳大道"
dataList = [bll, qtl, yydd]

arcpy.env.workspace = gdb

resDict = {}
resSet = set()
for each in dataList:
    eachNew = os.path.split(each)[1]
    eachNew = eachNew.replace("白粮路", "白粮路_1").replace("旗亭路", "旗亭路_1_1").replace("玉阳大道", "玉阳大道_1")

    arcpy.env.workspace = each
    fcList = arcpy.ListFeatureClasses("", "Multipatch")
    tmpDict = {}
    print(fcList)
    print(dataList)
    for i, eachFc in enumerate(fcList):
        eachFcNew = eachFc.replace("白粮路", "白粮路_1").replace("旗亭路", "旗亭路_1_1").replace("玉阳大道", "玉阳大道_1")

        fieldFmy = arcpy.ListFields(eachFc, "ObjectId")[0].name
        fieldDis = arcpy.ListFields(eachFc, "Discipline")[0].name
        resList = []
        print(f"i: {i}", eachFc)
        print(f"i: {i}", fieldFmy)
        print(f"i: {i}", fieldDis)
        if fieldDis and fieldFmy:
            resTup = {}
            print(eachFc)
            with arcpy.da.SearchCursor(eachFc, [fieldFmy, fieldDis]) as cur:
                for row in cur:
                    resSet.add(row[1])
                    resTup[row[0]] = row[1]

            tmpDict[eachFcNew] = resTup
    resDict[eachNew] = tmpDict

with open(r"F:\工作项目\项目_松江管廊\补漏_多删字段保留_Dis\res.txt", "w", encoding="utf-8") as f:
    f.write(str(resDict))

with open(r"F:\工作项目\项目_松江管廊\补漏_多删字段保留_Dis\res.json", "w", encoding="utf-8") as f:
    json.dump(resDict, fp=f, ensure_ascii=False, indent=4)

print(resSet)


gdb = "F:\\工作项目\\项目_松江管廊\\数据_松江管廊BIM转GIS\\数据\\松江管廊BIM结果数据.gdb"
bll = "F:\\工作项目\\项目_松江管廊\\数据_松江管廊BIM转GIS\\数据\\松江管廊BIM结果数据.gdb\\白粮路_1"
qtl = "F:\\工作项目\\项目_松江管廊\\数据_松江管廊BIM转GIS\\数据\\松江管廊BIM结果数据.gdb\\旗亭路_1_1"
yydd = "F:\\工作项目\\项目_松江管廊\\数据_松江管廊BIM转GIS\\数据\\松江管廊BIM结果数据.gdb\\玉阳大道_1"
dataList = [bll, qtl, yydd]

resSet = set()
for each in dataList:
    arcpy.env.workspace = each
    fcList = arcpy.ListFeatureClasses("", "Multipatch")
    tmpDict = {}
    print(fcList)
    print(dataList)
    fcDict = resDict[os.path.split(each)[1]]
    for i, eachFc in enumerate(fcList):
        try:
            arcpy.AddField_management(eachFc, "Discipline", "TEXT")
        except:
            arcpy.DeleteField_management(eachFc, "Discipline")
            arcpy.AddField_management(eachFc, "Discipline", "TEXT")
        fieldFmy = arcpy.ListFields(eachFc, "FamilyType")[0].name
        fieldDis = arcpy.ListFields(eachFc, "Discipline")[0].name
        resList = []
        print(f"i: {i}", eachFc)
        print(f"i: {i}", fieldFmy)
        print(f"i: {i}", fieldDis)
        if fieldDis and fieldFmy:
            print(eachFc)
            try:
                fieldDict = fcDict[eachFc]
            except:
                continue
            codes = f"""def f(fieldFmy):
    try:
        return {fieldDict}[fieldFmy]
    except:
        return 'Architectural'"""
            arcpy.CalculateField_management(eachFc, "Discipline", "f(!ObjectId!)", "PYTHON3", codes)
# #
# def f(fieldFmy):
#     try:
#         return {fieldDict}[fieldFmy]
#     except:
#         return 'Architectural'