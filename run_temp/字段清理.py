import arcpy

data = r"D:\temp\AIR_INFOREGION.gdb\AIR_INFOREGION_WORLD2"

filedList = [each for each in arcpy.ListFields(data) if each.type != "OID"
             and each.name.lower() != "shape_length" and each.name.lower() != "shape_area"
             and each.name != "SHAPE"]

for eachField in filedList:
    fieldNameO = eachField.name
    fieldName = eachField.name.strip("_1")
    try:
        arcpy.DeleteField_management(data, fieldName)
    except:
        pass
    print(eachField)
    arcpy.AlterField_management(data, fieldNameO, fieldName)
    # try:
    #     arcpy.AddField_management(data, fieldName, fieldType)
    # except:
    #     arcpy.DeleteField_management(data, fieldName)
    #     arcpy.AddField_management(data, fieldName, fieldType)
    # print(fieldName)
    # arcpy.CalculateField_management(data, fieldName, f"!{fieldNameO}!", "PYTHON3")
    #
    # arcpy.DeleteField_management(data, fieldNameO)