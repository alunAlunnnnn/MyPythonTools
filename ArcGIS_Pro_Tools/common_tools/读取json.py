import json
# import arcpy
import re
import requests


# arcpy.env.overwriteOutput = True

jsonFile = r"E:\公司GIS共用\DXGX\json\res\res.json"

with open(jsonFile, "r", encoding="utf-8") as f:
    data = f.read()


    data_json = json.loads(data)



# data = r"D:\test.shp"
#
# arcpy.AddField_management(data, "test1", "TEXT")
#
#
# codes = """def f(fieldA):
#     if fieldA in data_json:
#         return data_json[fieldA]
#     else:
#         return 'a'"""
# arcpy.CalculateField_management(data, "test1", "f(!FEAT!)", "PYTHON3", codes)


# def f(fieldA):
#     if fieldA in data_json:
#         return data_json[fieldA]
#     else:
#         return 'a'