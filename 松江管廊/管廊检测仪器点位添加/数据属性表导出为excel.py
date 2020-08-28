import arcpy, os

dir = r"C:\Users\lyce\AppData\Roaming\ESRI\Desktop10.7\ArcCatalog\连接到 192.168.174.6.sde\WZWSDB.GL_SJ"
arcpy.env.workspace = dir
dataList = arcpy.ListFeatureClasses()
print(dataList)
outputDir = r"E:\松江管廊\新数据0805\服务发布\对应关系表\发向\所有数据属性表"
for each in dataList:
    arcpy.TableToExcel_conversion(each, os.path.join(outputDir, each + ".xls"))