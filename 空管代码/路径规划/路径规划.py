# -*- coding: utf-8 -*-
import arcpy, os, sys, datetime

a = datetime.datetime.now()

arcpy.env.overwriteOutput = True

netDataSet = r"D:\老电脑数据\瀚世老笔记本\工作任务_预研\机场路径规划_实时\处理数据\zspd.gdb\progress_1\progress_1_ND"
netDataSet1 = r"D:\老电脑数据\瀚世老笔记本\工作任务_预研\机场路径规划_实时\处理数据\zspd.gdb\line"
pnt = r"D:\老电脑数据\瀚世老笔记本\工作任务_预研\机场路径规划_实时\处理数据\zspd.gdb\progress_1\pnt"
selPnt = r"D:\老电脑数据\瀚世老笔记本\工作任务_预研\机场路径规划_实时\处理数据\zspd.gdb\pnts"


# Create route layer
impedanceAttribute = u"长度"

# USE_INPUT_ORDER —— order by pnt、FIND_BEST_ORDER —— reorder to find the best way
findBestOrder = "USE_INPUT_ORDER"

# this Parameter is available when para "findBestOrder" is "FIND_BEST_ORDER"
orderingType = ""
routeLayer = arcpy.MakeRouteLayer_na(netDataSet, "netLayer", impedanceAttribute, findBestOrder, orderingType)

# Add stop location
subLayer = u"停靠点"
fieldMapping = ""
test = arcpy.AddLocations_na(routeLayer, subLayer, pnt, fieldMapping, "5000 Meters")
# print(test)
# print(test.maxSeverity)
# print(type(test))
# print(test[0])
# print(type(test[0]))
# print(test[0].name)

# outNALayer = "qwewqewq"
# Solve the location of route
solveRes = arcpy.Solve_na(routeLayer)
# print(solveRes.getOutput (0))
# print(solveRes.getOutput (1))

# print(id(routeLayer))
# print(type(routeLayer))
# print(id(test[0]))
# print(id(solveRes[0]))

# print(solveRes.getOutput (1))
# print(solveRes[0].getOutput()[1])
# res = arcpy.na.GetNAClassNames(solveRes)
# print(res)
# print(solveRes)
# print(type(solveRes))
# print(solveRes[0])
# print(type(solveRes[0]))
# print(type(solveRes[1]))
# print(solveRes[-1])
# q = arcpy.MakeFeatureLayer_management(selPnt, "Q")
# print("*****")
# lyrList = arcpy.mapping.ListLayers(solveRes[0])
# print(lyrList)
# pntList = []
# for i, each in enumerate(solveRes[0]):
#     print(each.name.encode("utf-8"))
#     if i == 2:
#         print(each.name.encode("utf-8"))
#         temp = arcpy.SelectLayerByLocation_management(q, "INTERSECT", each)
#         with arcpy.da.SearchCursor(temp, ["x", "y"]) as cur:
#             for row in cur:
#                 pntList.append((row[0], row[1]))
# print(solveRes[0][2].name.encode("utf-8"))
# arcpy.CopyFeatures_management(selPnt, "D:/QQQ.shp")

# arcpy.CopyFeatures_management(solveRes[0], "D:/w.shp")

# arcpy.CopyFeatures_management(temp, "D:/qwer.shp")


savRes = arcpy.SaveToLayerFile_management(routeLayer, "D:/Solve.lyr")

# feaRes = arcpy.CopyFeatures_management(savRes, "D:/save.shp")



# denRes = arcpy.Densify_edit(feaRes, "DISTANCE", "3")

# arcpy.FeatureVerticesToPoints_management(denRes, "D:/test.shp")

# q = arcpy.MakeFeatureLayer_management(selPnt, "selpnt")
# q2 = arcpy.MakeFeatureLayer_management(netDataSet1, "selpnt2")
# print(q)
# print(solveRes)
# r = arcpy.mapping.Layer("D:/Solve.lyr")
# print()
#
# path = arcpy.Describe(solveRes).dataType
# print(path)
# print(solveRes[0])
# print(solveRes[1])
# # print(solveRes[2])
# # print(solveRes[3])
# # res = arcpy.CopyFeatures_management(r, "in_memory/ttt")
# # w = arcpy.MakeFeatureLayer_management(res, "tttt")
# # solveRes[0].export("Routes", "D:/")
# temp = arcpy.SelectLayerByLocation_management(q, "INTERSECT", solveRes[0])
#
# temp1 = arcpy.CopyFeatures_management(temp, "in_memory/tempdata")
#
# pntList = []
# with arcpy.da.SearchCursor(temp1, ["x", "y"]) as cur:
#     for row in cur:
#         pntList.append((row[0], row[1]))

b = datetime.datetime.now()

res = b - a
print(res)
# print(pntList)