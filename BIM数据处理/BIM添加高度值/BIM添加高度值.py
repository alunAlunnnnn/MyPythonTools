import arcpy

selFea = r"D:\Users\lyce\Documents\ArcGIS\Projects\管廊BIM\管廊BIM.gdb\plg_bll_total"
selLyr = arcpy.MakeFeatureLayer_management(selFea)

aprx = arcpy.mp.ArcGISProject("CURRENT")
scene = aprx.listMaps("Scene4")[0]

lyrs = scene.listLayers()

for each in lyrs:
    if each.isFeatureLayer:
        desc = arcpy.Describe(each)
        print(each)
        print(each.name)
        seldLyr = arcpy.SelectLayerByLocation_management(each, "INTERSECT", selLyr)
        codes = """def f(a):
        if a <= -4.9:
            return 2
        else:
            return 3"""
        arcpy.CalculateField_management(each, "BldgLevel", "f(!shape.centroid.z!)", "PYTHON3", codes)


# 用的使用改 第三行 的面数据 第七行的 "Scene" 和 18行的高度