import math
import arcpy

arcpy.env.overwriteOutput = True


def convert(coordTuple):
    return coordTuple[0] + coordTuple[1] / 60 + coordTuple[2] / 3600


def addField(inFC, fieldName, fieldType):
    try:
        arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType)


# coordList = [((25, 56, 57.61), (119, 40, 17.87)), ((25, 56, 26.38),
#                                                    (119, 41, 17.72)), ((25, 55, 13.38), (119, 39, 19.13)),
#              ((25, 54, 42.15), (119, 40, 18.97))]

coordList = [((119, 40, 17.87), (25, 56, 57.61)), ((119, 41, 17.72), (25, 56, 26.38)),
             ((119, 39, 19.13), (25, 55, 13.38)), ((119, 40, 18.97), (25, 54, 42.15))]
res = []
for eachPnt in coordList:
    resList = []
    for eachCoor in eachPnt:
        cor = convert(eachCoor)
        resList.append(cor)
    res.append(resList)
print(res)

outputPath = r"E:\新机场\处理数据\矢量数据处理.gdb"
outputName = "tarPnt"
sr = arcpy.SpatialReference(4326)
resData = arcpy.CreateFeatureclass_management(outputPath, outputName, "POINT", spatial_reference=sr)

with arcpy.da.InsertCursor(resData, ["SHAPE@XY"]) as cur:
    for eachPnt in res:
        cur.insertRow([eachPnt])

fieldList = ["X", "Y", "Z"]
fieldExpt = ["!shape.centroid.X!", "!shape.centroid.Y!", "!shape.centroid.Z!"]
for i, eachField in enumerate(fieldList):
    addField(resData, eachField, "DOUBLE")
    arcpy.CalculateField_management(resData, eachField, fieldExpt[i], "PYTHON3")

print("finish!")
