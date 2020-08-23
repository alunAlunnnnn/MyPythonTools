import arcpy
import os

gdb = r'E:\sjgl_sjgx\res\最后数据\data2019.gdb'
oriGDB = r'E:\sjgl_sjgx\res\最后数据\200729.gdb'
arcpy.env.workspace = gdb

dataSet = arcpy.ListDatasets()


# for eachFC in feaList:
#     field1 = arcpy.ListFields(eachFC, "T*_*")[0].name
#     try:
#         field = arcpy.ListFields(eachFC, "*_PipeID")[0].name
#         # arcpy.AlterField_management(eachFC, field, field.split("_")[1], field.split("_")[1])
#         arcpy.DeleteField_management(eachFC, field)
#     except:
#         pass
#     #
#     # try:
#     #     field1 = arcpy.ListFields(eachFC, "*_OBJEC")[0].name
#     #     arcpy.DeleteField_management(eachFC, field1)
#     # except:
#     #     pass
#     print(eachFC, ":", field1)
#     arcpy.DeleteField_management(eachFC, field1)


def _addYearField(inFC):
    try:
        arcpy.AddField_management(inFC, "CURRENT_YEAR", "LONG")
    except:
        arcpy.DeleteField_management(inFC, "CURRENT_YEAR")
        arcpy.AddField_management(inFC, "CURRENT_YEAR", "LONG")


def _calculateField(inFC, year):
    arcpy.CalculateField_management(inFC, "CURRENT_YEAR", "%s" % year, "PYTHON_9.3")


def _detectFields(inFC1, inFC2):
    fieldList1 = [aa.name for aa in arcpy.ListFields(inFC1)]
    fieldList2 = [bb.name for bb in arcpy.ListFields(inFC2)]
    for eachField1 in fieldList1:
        if eachField1 in fieldList2:
            print("匹配成功： 数据 --- %s， 数据 --- %s, field --- %s" % (inFC1, inFC2, eachField1))
            fieldList2.remove(eachField1)
        # else:
        #     print("%s 字段 %s，不在%s中" % (inFC1, eachField1, inFC2))

    if len(fieldList2) > 0:
        print("%s 数据中的字段'%s'不在 %s中" % (inFC2, [a.name for a in fieldList2], inFC1))

# # add current year field
# for eachDataSet in dataSet:
#     arcpy.env.workspace = os.path.join(gdb, eachDataSet)
#     feaList = arcpy.ListFeatureClasses()
#     print(feaList)
#     for each in feaList:
#         _addYearField(each)
#         _calculateField(each, 2019)


# detect whether tableName in fields' name
# for eachDataSet in dataSet:
#     arcpy.env.workspace = os.path.join(gdb, eachDataSet)
#     feaList = arcpy.ListFeatureClasses()
#     for each in feaList:
#         fieldList = [eachField.name for eachField in arcpy.ListFields(each)]
#         for eachF in fieldList:
#             if "T" in eachF[:3] and "_" in eachF:
#                 print(eachF)
#             else:
#                 pass


# detect whether the field name is same between origin data and 2018 or 2019
for eachDataSet in dataSet:
    arcpy.env.workspace = os.path.join(gdb, eachDataSet)
    feaList = arcpy.ListFeatureClasses()
    for each in feaList:
        arcpy.env.workspace = os.path.join(gdb, eachDataSet)
        fieldList = [eachField.name for eachField in arcpy.ListFields(each)]

        # origin data
        arcpy.env.workspace = oriGDB
        dataSets = arcpy.ListDatasets()
        print(dataSets)
        #
        dataType = each.split("_")[0]
        if dataType in dataSets:
            arcpy.env.workspace = os.path.join(oriGDB, dataType)
            fcList = arcpy.ListFeatureClasses()
            for eachData in fcList:
                if each == eachData:
                    print("%s --- %s" % (os.path.join(gdb, eachDataSet, each), os.path.join(oriGDB, dataType, eachData)))
                    arcpy.Append_management(os.path.join(gdb, eachDataSet, each), os.path.join(oriGDB, dataType, eachData), "NO_TEST")
                    # _detectFields(each, eachData)
                # else:
                #     print("数据集中无匹配：", each)

        # else:
        #     print("gdb中无匹配： ", dataType)


        # for eachF in fieldList:
        #     if "T" in eachF[:3] and "_" in eachF:
        #         print(eachF)
        #     else:
        #         pass

