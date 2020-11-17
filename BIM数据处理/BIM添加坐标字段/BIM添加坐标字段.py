import arcpy


def _addCoordField(inFC):
    fieldName = ["ROAD_NAME", "ROAD_ID", "GIS_X_MIN",
                 "GIS_Y_MIN", "GIS_Z_MIN", "GIS_X_CEN",
                 "GIS_Y_CEN", "GIS_Z_CEN", "GIS_X_MAX",
                 "GIS_Y_MAX", "GIS_Z_MAX"]
    fieldType = ["TEXT", "SHORT", "DOUBLE", "DOUBLE",
                 "DOUBLE", "DOUBLE", "DOUBLE", "DOUBLE",
                 "DOUBLE", "DOUBLE", "DOUBLE"]
    express = ["'玉阳大道'", 1, "!shape.extent.XMin!", "!shape.extent.YMin!",
               "!shape.extent.ZMin!", "!shape.centroid.x!", "!shape.centroid.y!",
               "!shape.centroid.z!", "!shape.extent.XMax!", "!shape.extent.YMax!",
               "!shape.extent.ZMax!"]

    for i, each in enumerate(fieldName):
        try:
            arcpy.AddField_management(inFC, each, fieldType[i])
        except:
            arcpy.DeleteField_management(inFC, each)
            arcpy.AddField_management(inFC, each, fieldType[i])
        arcpy.CalculateField_management(inFC, each, f"{express[i]}", "PYTHON3")


def _calField2(inFC):
    fieldName = ["ROAD_NAME", "ROAD_ID"]
    express = ["'旗亭路'", 2]
    for i, each in enumerate(fieldName):
        arcpy.CalculateField_management(inFC, each, f"{express[i]}", "PYTHON3")


def _calField3(inFC):
    arcpy.CalculateField_management(inFC, "BldgLevel_Elev", "!shape.centroid.z!", "PYTHON3")


aprx = arcpy.mp.ArcGISProject("CURRENT")
scene = aprx.listMaps("Scene")[0]

lyrs = scene.listLayers()

for each in lyrs:
    if each.isFeatureLayer:
        print(each)
        print(each.name)
        # _addCoordField(each)
        # _calField2(each)
        _calField3(each)
