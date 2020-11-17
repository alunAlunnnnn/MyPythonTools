import arcpy
import re

# # used in ArcGIS Pro running Project
# def checkFiledExists(sceneName):
#     aprx = arcpy.mp.ArcGISProject("CURRENT")
#     map = aprx.listMaps(sceneName)[0]
#     lyrList = map.listLayers()
#
#     for eachLyr in lyrList:
#         fields = arcpy.ListFields(eachLyr, "")


# def setDefinition(sql):
#     aprx = arcpy.mp.ArcGISProject("CURRENT")
#     scene = aprx.listMaps("Scene")[0]
#
#     lyrs = scene.listLayers()
#
#     for each in lyrs:
#         if each.isFeatureLayer:
#             try:
#                 each.setDefinition(sql)
#             except:
#                 pass
#
# sql = "BldgLevel = 1"
# setDefinition(sql)



def _addField(inFC, fieldName, fieldType, field_alias=None):
    if field_alias is None:
        field_alias = fieldName
    try:
        arcpy.AddField_management(inFC, fieldName, fieldType, field_alias=field_alias)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType, field_alias=field_alias)
    finally:
        fieldList = arcpy.ListFields(inFC, fieldName)
        if len(fieldList) > 0:
            return True
        else:
            return False


# used in ArcGIS Pro running Project
def addSymField():
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    map = aprx.listMaps("Scene")[0]
    pipeFitLyr = map.listLayers("*PipeFitting*")
    print(pipeFitLyr)

    for each in pipeFitLyr:
        print(each.name)
        # 添加字段成功
        if _addField(each, "SYMBOL", "TEXT", field_alias="管件类型"):
            codes = """def f(sysType, famType):
	value = sysType
	if value is not None:
		value = value.strip()
		if value != "":
			return sysType
		else:
			return famType
	else:
		return famType"""
            arcpy.CalculateField_management(each, "SYMBOL", "f(!SystemType!, !FamilyType!)",
                                            "PYTHON3", codes)
        # 添加字段失败
        else:
            pass


import arcpy







