import arcpy
import os

bld = r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\aprx\温州超图_粗模数据处理\温州超图_粗模数据处理.gdb\RES_PY_Height_Project1"
grid = r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\aprx\温州超图_粗模数据处理\温州超图_粗模数据处理.gdb\grid_Project_Buffer"
outputPath = r"F:\工作项目\项目_温州超图\任务_粗摸制作\processData\total"

oIdName = [each.name for each in arcpy.ListFields(grid) if each.type == "OID"][0]
print(oIdName)

gridLyr = arcpy.MakeFeatureLayer_management(grid, "gridLyr")
bldLyr = arcpy.MakeFeatureLayer_management(bld, "bldLyr")
with arcpy.da.SearchCursor(grid, [oIdName]) as cur:
    for row in cur:
        selLyr = arcpy.SelectLayerByAttribute_management(gridLyr, "NEW_SELECTION", f"{oIdName} = {row[0]}")
        selBldLyr = arcpy.SelectLayerByLocation_management(bldLyr, "INTERSECT", selLyr)
        arcpy.ExportCAD_conversion(selBldLyr, "DWG_R2010", f"{os.path.join(outputPath, 'bld_' + str(row[0]) + '.dwg')}")

