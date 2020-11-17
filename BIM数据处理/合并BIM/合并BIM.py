import arcpy
import os


def _getFCFields(inFC):
    # 获取所有字段名
    fieldNameList = [each.name for each in arcpy.ListFields(inFC) if each.type.lower() != "oid" and
                     each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
                     each.name.lower() != "shape_area"]

    # 获取所有字段值
    fieldTypeList = [each.type for each in arcpy.ListFields(inFC) if each.type.lower() != "oid" and
                     each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
                     each.name.lower() != "shape_area"]

    # 将字段信息保存为 {‘字段名’: ‘字段值’, ....} 的形式
    fieldsDict = dict(list(zip(fieldNameList, fieldTypeList)))

    print(inFC)
    print(fieldsDict)
    print(" ")
    return fieldsDict


def _getAllFCFields(inGDB, pWildcards):
    oriWorkspace = None
    if arcpy.env.workspace:
        oriWorkspace = arcpy.env.workspace

    # 设置函数内工作空间
    arcpy.env.workspace = inGDB

    # 获取每个要素集
    datasetDict = {}
    for each in pWildcards:
        fcDict = {}
        # 确保要素集存在
        dataset = arcpy.ListDatasets(each)

        if len(dataset) > 0:
            fcList = arcpy.ListFeatureClasses("", "Multipatch", each)

            if len(fcList) > 0:
                for eachFC in fcList:
                    lyrName = eachFC.split("_")[0]
                    fieldsInfo = _getFCFields(inFC)
                    fcDict[lyrName] = fieldsInfo
        datasetDict[each] = fcDict
    # 清除工作空间
    if not oriWorkspace:
        arcpy.env.workspace = oriWorkspace
    else:
        arcpy.ClearEnvironment("workspace")

    print(datasetDict)
    return datasetDict


def unifyFCFields(inGDB, pWildcards):
    # fcFields = _getAllFCFields(inGDB, pWildcards)
    fieldsKeep = ['Category', 'Family', 'FamilyType', 'ObjectId',
                  'BldgLevel', 'BldgLevel_Elev', 'CreatedPhase',
                  'BaseCategory', 'Mark', 'InstanceElev', 'RefLevel',
                  'RefLevel_IsBuildingStory', 'RefLevel_RoomOffset',
                  'RefLevel_Elev', 'RefLevel_Desc', 'StructUsage', 'Comments',
                  'ElevationInstance', 'ROAD_NAME', 'ROAD_ID', 'GIS_X_MIN',
                  'GIS_Y_MIN', 'GIS_Z_MIN', 'GIS_X_CEN', 'GIS_Y_CEN', 'GIS_Z_CEN',
                  'GIS_X_MAX', 'GIS_Y_MAX', 'GIS_Z_MAX', 'Discipline']

    oriWorkspace = None
    if arcpy.env.workspace:
        oriWorkspace = arcpy.env.workspace

    # 设置函数内工作空间
    arcpy.env.workspace = inGDB

    # 获取每个要素集

    for eachDataSet in pWildcards:

        # 确保要素集存在
        dataset = arcpy.ListDatasets(eachDataSet)

        if len(dataset) > 0:
            fcList = arcpy.ListFeatureClasses("", "Multipatch", eachDataSet)

            if len(fcList) > 0:
                for eachFC in fcList:
                    fieldNameList = [eachField.name for eachField in arcpy.ListFields(eachFC) if
                                     eachField.type.lower() != "oid" and
                                     eachField.type.lower() != "geometry" and eachField.name.lower() != "shape_length" and
                                     eachField.name.lower() != "shape_area"]
                    delfields = []
                    for eachdelField in fieldNameList:
                        if eachdelField not in fieldsKeep:
                            delfields.append(eachdelField)
                    if len(delfields) > 0:
                        print(delfields)
                        arcpy.DeleteField_management(eachFC, delfields)
    # 清除工作空间
    if not oriWorkspace:
        arcpy.env.workspace = oriWorkspace
    else:
        arcpy.ClearEnvironment("workspace")

    return None


# def _addField(inFC, fieldName, fieldType, fieldAlias, fieldLength):
def _addField(inFC, fieldName, fieldType):
    # try:
    arcpy.AddField_management(inFC, fieldName, fieldType)
    # except:
    #     arcpy.DeleteField_management(inFC, fieldName)
    #     arcpy.AddField_management(inFC, fieldName, fieldType, field_alias=fieldAlias, field_length=fieldLength)

    field = arcpy.ListFields(inFC, fieldName)
    if len(field) > 0:
        print(f"数据   '{inFC}'   添加字段   '{fieldName}'   成功！")
    else:
        print(f"数据   '{inFC}'   添加字段   '{fieldName}'   失败！！！！")


def varifyFields(tarFC, appFC):
    # 目标数据
    tarFieldNameList = [each.name for each in arcpy.ListFields(tarFC) if each.type.lower() != "oid" and
                        each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
                        each.name.lower() != "shape_area"]

    tarFieldTypeList = [each.type for each in arcpy.ListFields(tarFC) if each.type.lower() != "oid" and
                        each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
                        each.name.lower() != "shape_area"]

    # tarFieldaNameList = [each.aliasName for each in arcpy.ListFields(tarFC) if each.type.lower() != "oid" and
    #                      each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
    #                      each.name.lower() != "shape_area"]
    #
    # tarFieldLengthList = [each.length for each in arcpy.ListFields(tarFC) if each.type.lower() != "oid" and
    #                       each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
    #                       each.name.lower() != "shape_area"]

    # 追加数据
    appFieldNameList = [each.name for each in arcpy.ListFields(appFC) if each.type.lower() != "oid" and
                        each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
                        each.name.lower() != "shape_area"]

    appFieldTypeList = [each.type for each in arcpy.ListFields(appFC) if each.type.lower() != "oid" and
                        each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
                        each.name.lower() != "shape_area"]

    # appFieldaNameList = [each.aliasName for each in arcpy.ListFields(appFC) if each.type.lower() != "oid" and
    #                      each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
    #                      each.name.lower() != "shape_area"]
    #
    # appFieldLengthList = [each.length for each in arcpy.ListFields(appFC) if each.type.lower() != "oid" and
    #                       each.type.lower() != "geometry" and each.name.lower() != "shape_length" and
    #                       each.name.lower() != "shape_area"]

    # # 给追加数据添加缺失的字段
    for i, eachTarField in enumerate(tarFieldNameList):
        if eachTarField not in appFieldNameList:
            _addField(appFC, eachTarField, appFieldTypeList[i])


    for i, eachAppField in enumerate(appFieldNameList):
        if eachAppField not in tarFieldNameList:
            _addField(tarFC, eachAppField, tarFieldTypeList[i])

    # # 给追加数据添加缺失的字段
    # for i, eachTarField in enumerate(tarFieldNameList):
    #     if eachTarField not in appFieldNameList:
    #         arcpy.DeleteField_management(tarFC, eachTarField)
    #
    # for i, eachAppField in enumerate(appFieldNameList):
    #     if eachAppField not in tarFieldNameList:
    #         arcpy.DeleteField_management(appFC, eachAppField)


def appendFC(inGDB, tarFCSet, inputFCSets):
    arcpy.env.workspace = inGDB
    resDict = {}
    tarFCList = arcpy.ListFeatureClasses("", "", tarFCSet)
    print(tarFCSet, tarFCList)
    for eachTarFC in tarFCList:
        tarLyrName = eachTarFC.split("_")[0]

        # 寻找其他数据里对应的图层
        for eachFCS in inputFCSets:
            resList = []
            appFCList = arcpy.ListFeatureClasses("", "", eachFCS)
            print(eachFCS, appFCList)
            for eachAppFC in appFCList:
                appLyrName = eachAppFC.split("_")[0]

                # 匹配成功
                if appLyrName == tarLyrName:
                    print("匹配成功", eachAppFC)
                    # varifyFields(eachTarFC, eachAppFC)
                    arcpy.Append_management([eachAppFC], eachTarFC, "NO_TEST")
                else:
                    resList.append(eachAppFC)
            resDict[eachFCS] = resList
    print(resDict)



def modifyAlias(inGDB):
    oriWorkspace = None
    if arcpy.env.workspace:
        oriWorkspace = arcpy.env.workspace

    # 设置函数内工作空间
    arcpy.env.workspace = inGDB

    dataset = [os.path.join(inGDB, "SH_SJ_GL_3D_BIM1", each) for each in arcpy.ListFeatureClasses("", "", "SH_SJ_GL_3D_BIM1")]
    print(dataset)
    for each in dataset:
        arcpy.AlterAliasName(each, os.path.split(each)[1].split("_")[0])

    # 清除工作空间
    if not oriWorkspace:
        arcpy.env.workspace = oriWorkspace
    else:
        arcpy.ClearEnvironment("workspace")


inFC = r"F:\工作项目\项目_松江管廊\数据_松江管廊BIM转GIS\数据\BIM合并测试.gdb\白粮路_1_1\StructuralFraming_白粮路_1_1"
inGDB = r"F:\工作项目\项目_松江管廊\数据_松江管廊BIM转GIS\数据\BIM合并测试.gdb"
pWildcards = ["白粮路_1", "旗亭路_1_1", "玉阳大道_1"]
tarFCSet = "SH_SJ_GL_3D_BIM"
inputFCSets = ["白粮路_1", "旗亭路_1_1"]

# _getFCFields(inFC)
# unifyFCFields(inGDB, pWildcards)
modifyAlias(inGDB)
# appendFC(inGDB, tarFCSet, inputFCSets)
