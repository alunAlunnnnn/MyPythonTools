import arcpy

data = r"E:\松江管廊\新数据0805\监控点\移动至正确位置\分图层\监控点_总.shp"

codes="""datalist = ["超声波液位仪", "防爆型含氧量检测", "防爆型红外入侵", "防爆型摄像机", "防爆型声光报警", "防爆型温湿度检测",
            "含氧量检测", "红外入侵", "甲烷检测", "硫化氢检测", "摄像机", "声光报警", "温湿度检测", "自动液压井盖"]
newNameList = ["GL_SENSOR_CSBYWY", "GL_SENSOR_FBXHYLJC", "GL_SENSOR_FBXHWRQ", "GL_SENSOR_FBXSXJ",
               "GL_SENSOR_FBXSGBJ", "GL_SENSOR_FBXWSDJC", "GL_SENSOR_HYLJC", "GL_SENSOR_HWRQ",
               "GL_SENSOR_JWJC", "GL_SENSOR_LHQJC", "GL_SENSOR_SXJ", "GL_SENSOR_SGBJ",
               "GL_SENSOR_WSDJC", "GL_SENSOR_ZDYYJG"]
def f(a):
    data = datalist.index(a)
    return newNameList[data]"""

arcpy.CalculateField_management(data, "layernm", "f( !sblx! )", "PYTHON3", codes)