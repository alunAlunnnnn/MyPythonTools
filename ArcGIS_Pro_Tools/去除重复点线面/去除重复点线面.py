# -*- coding: utf-8 -*-
import arcpy
import os


def addField(inFC, fieldName, fieldType):
    try:
        arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType)


def main_pnt(inFC):
    addField(inFC, "temp_x_", "DOUBLE")
    addField(inFC, "temp_y_", "DOUBLE")
    addField(inFC, "repeat_", "SHORT")

    arcpy.CalculateField_management(inFC, "temp_x_", "!shape.centroid.X!", "PYTHON_9.3")
    arcpy.CalculateField_management(inFC, "temp_y_", "!shape.centroid.Y!", "PYTHON_9.3")

    fieldList = ["temp_x_", "temp_y_"]
    valueList = []
    with arcpy.da.SearchCursor(inFC, fieldList) as cur:
        for row in cur:
            x_t, y_t = row[0], row[1]
            coord = (round(x_t, 6), round(y_t, 6))
            valueList.append(coord)
        del row

    codes = """list1 = {}
def f(fieldX, fieldY):
    global list1
    coord = (round(fieldX, 6), round(fieldY, 6))
    if list1.count(coord) > 1:
        return 2
    else:
        return 1""".format(valueList)

    arcpy.CalculateField_management(inFC, "repeat_", "f(!temp_x_!, !temp_y_!)", "PYTHON_9.3", codes)


def main_ply(inFC):
    addField(inFC, "temp_x_", "DOUBLE")
    addField(inFC, "temp_y_", "DOUBLE")
    addField(inFC, "repeat_", "SHORT")

    arcpy.CalculateField_management(inFC, "temp_x_", "!shape.centroid.X!", "PYTHON_9.3")
    arcpy.CalculateField_management(inFC, "temp_y_", "!shape.centroid.Y!", "PYTHON_9.3")

    fieldList = ["temp_x_", "temp_y_", "Shape_Length"]
    valueList = []
    with arcpy.da.SearchCursor(inFC, fieldList) as cur:
        for row in cur:
            x_t, y_t, length = row[0], row[1], row[2]
            coord = (round(x_t, 6), round(y_t, 6), round(length, 6))
            valueList.append(coord)
        del row

    codes = """list1 = {}
def f(fieldX, fieldY, length):
    global list1
    coord = (round(fieldX, 6), round(fieldY, 6), round(length, 6))
    if list1.count(coord) > 1:
        return 2
    else:
        return 1""".format(valueList)

    arcpy.CalculateField_management(inFC, "repeat_", "f(!temp_x_!, !temp_y_!, !Shape.Length!)", "PYTHON_9.3", codes)


def main_plg(inFC):
    addField(inFC, "temp_x_", "DOUBLE")
    addField(inFC, "temp_y_", "DOUBLE")
    addField(inFC, "repeat_", "SHORT")

    arcpy.CalculateField_management(inFC, "temp_x_", "!shape.centroid.X!", "PYTHON_9.3")
    arcpy.CalculateField_management(inFC, "temp_y_", "!shape.centroid.Y!", "PYTHON_9.3")

    fieldList = ["temp_x_", "temp_y_", "Shape_Length", "Shape_Area"]
    valueList = []
    with arcpy.da.SearchCursor(inFC, fieldList) as cur:
        for row in cur:
            x_t, y_t, length, area = row[0], row[1], row[2], row[3]
            coord = (round(x_t, 6), round(y_t, 6), round(length, 6), round(area, 6))
            valueList.append(coord)
        del row

    codes = """list1 = {}
def f(fieldX, fieldY, length, area):
    global list1
    coord = (round(fieldX, 6), round(fieldY, 6), round(length, 6), round(area, 6))
    if list1.count(coord) > 1:
        return 2
    else:
        return 1""".format(valueList)

    arcpy.CalculateField_management(inFC, "repeat_", "f(!temp_x_!, !temp_y_!, !Shape.Length!, !Shape.Area!)", "PYTHON_9.3", codes)


print("Step1 --- Start process")
inGDB = r"E:\sjgl_sjgx\res\最后数据\200729.gdb"
arcpy.env.workspace = inGDB
dataSets = arcpy.ListDatasets()
print("Step2 --- Datasets get")
for each in dataSets:
    print("Now is processing dataset --- {}, {}/{}".format(each, dataSets.index(each) + 1, len(dataSets) + 1))
    dataPath = os.path.join(inGDB, each)
    arcpy.env.workspace = dataPath
    pntList = arcpy.ListFeatureClasses("", "Point")
    plyList = arcpy.ListFeatureClasses("", "Polyline")
    plgList = arcpy.ListFeatureClasses("", "Polygon")
    for eachPnt in pntList:
        main_pnt(eachPnt)
    for eachPly in plyList:
        main_ply(eachPly)
    for eachPlg in plgList:
        main_plg(eachPlg)
print("Finish")