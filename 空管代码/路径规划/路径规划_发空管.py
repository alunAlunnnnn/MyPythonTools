# -*- coding: utf-8 -*-
import arcpy
import datetime

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

# solve the route
solveRes = arcpy.Solve_na(routeLayer)

# save route as a layer file
savRes = arcpy.SaveToLayerFile_management(routeLayer, "D:/Solve.lyr")

# calculate total runtime
b = datetime.datetime.now()
res = b - a
print(res)
