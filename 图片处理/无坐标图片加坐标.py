import arcpy

arcpy.env.overwriteOutput = True

outputPath = r"E:\松江管廊\新数据0805\图片动态地图服务\images_new"
outputName = "area"

pnts = [[108.5, 21], [108.5, 42], [129.5, 42], [129.5, 21]]

sr = arcpy.SpatialReference(4326)

shp = arcpy.CreateFeatureclass_management(outputPath, outputName, "POLYGON", spatial_reference=sr)

with arcpy.da.InsertCursor(shp, ["SHAPE@"]) as cur:
    plg = arcpy.Polygon(arcpy.Array([arcpy.Point(*each) for each in pnts]))
    cur.insertRow([plg])


arcpy.Delete_management()