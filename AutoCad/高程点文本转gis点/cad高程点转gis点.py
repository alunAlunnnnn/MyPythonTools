from pyautocad import Autocad
import arcpy

arcpy.env.overwriteOutput = True

data = r"E:\ArcGIS_Dustbin\cad\cadText.dwg"
outputPath = r"E:\ArcGIS_Dustbin\cad\res"
outputName = "XBQY_CAD"

# 实例化cad对象，需要cad保持打开状态
acad = Autocad()

# cad的控制台中打印的内容
acad.prompt("Hello, Autocad from Python\n")

# acad.doc 是当前cad中正在处于激活状态的图纸
print(acad.doc.Name)

pntList = []
# 找到所有文本对象的插入点及文本内容
for i, text in enumerate(acad.iter_objects('Text')):
    pntList.append((text.InsertionPoint[0], text.InsertionPoint[1], float(text.TextString)))

    if i % 500 == 1:
        print(i)

print(pntList)
sr = arcpy.SpatialReference(3857)
tempPoint = arcpy.CreateFeatureclass_management(outputPath, outputName + "_temp", "POINT", spatial_reference=sr)
resPoint = arcpy.CreateFeatureclass_management(outputPath, outputName, "POINT", spatial_reference=sr)

try:
    arcpy.AddField_management(tempPoint, "GCZ", "DOUBLE")
except:
    arcpy.DeleteField_management(tempPoint, "GCZ")
    arcpy.AddField_management(tempPoint, "GCZ", "DOUBLE")

with arcpy.da.InsertCursor(tempPoint, ["SHAPE@XY", "GCZ"]) as cur:
    points = [arcpy.Point(*(each[:-1])) for each in pntList]
    for i, each in enumerate(points):
        cur.insertRow([each, pntList[i][-1]])

arcpy.FeatureTo3DByAttribute_3d(tempPoint, resPoint, "GCZ")
arcpy.Delete_management(tempPoint)