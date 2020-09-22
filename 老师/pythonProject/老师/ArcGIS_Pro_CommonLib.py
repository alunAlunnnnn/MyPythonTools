import pprint
import inspect
import arcpy
import os
import functools
import datetime
import math
import logging


# points type is not tuple
class pointError(Exception):
    pass


class calKError(Exception):
    pass


class GenerateSpatialIndexError(Exception):
    pass


class lineEquation:
    """
    usage: generate a line object
    :param args: accept as
     --- (fp_x, fp_y, fp_z), (lp_x, lp_y, lp_z), (ex_xin, ex_ymin, ex_xmax, ex_ymax)
    firstPoint --- fp
    lastPoint --- lp
    extent --- ex
    """

    def __init__(self, *args):
        # save all points
        self.points = []

        for each in args[:2]:
            if not isinstance(each, tuple):
                raise pointError

            self.points.append((float(each[0]), float(each[1]), float(each[2])))

        self.extent_xmin = args[2][0]
        self.extent_ymin = args[2][1]
        self.extent_xmax = args[2][2]
        self.extent_ymax = args[2][3]
        self.extent = args[2]

        # get point number, start with 1
        self.pntNum = len(args)

        # init pipe size
        self.pipeSize = None

        # set coord of start point and finish point
        self.x1 = self.points[0][0]
        self.y1 = self.points[0][1]
        self.z1 = self.points[0][2]
        self.x2 = self.points[-1][0]
        self.y2 = self.points[-1][1]
        self.z2 = self.points[-1][2]

        # extent available detect
        self._extentAvailableDetect()

        self.spaindex = None
        self.spaindex_row = None
        self.spaindex_col = None
        self.spaind_totalext = None

        self.calculateK_xy()
        self.calculateB_xy()

        self.calculateK_yz()
        self.calculateB_yz()

        self.calculateK_xz()
        self.calculateB_xz()

        self.generateEquation()

    # calculate k --- ( y2 - y1 ) / ( x2 - x1 )
    def calculateK_xy(self):
        if self.x1 == self.x2:
            self.k_xy = -999
            return self
        k = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.k_xy = k
        return self

    # calculate b --- y1 - k * x1
    def calculateB_xy(self):
        if self.k_xy == -999:
            self.b_xy = -999
        else:
            b = self.y1 - self.k_xy * self.x1
            self.b_xy = b
        return self

    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_yz(self):
        if self.y1 == self.y2:
            self.k_yz = -999
            return self
        k = (self.z2 - self.z1) / (self.y2 - self.y1)
        self.k_yz = k
        return self

    # calculate b --- z1 - k * y1
    def calculateB_yz(self):
        if self.k_yz == -999:
            self.b_yz = -999
        else:
            b = self.z1 - self.k_yz * self.y1
            self.b_yz = b
        return self

    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_xz(self):
        if self.x1 == self.x2:
            self.k_xz = -999
            return self
        k = (self.z2 - self.z1) / (self.x2 - self.x1)
        self.k_xz = k
        return self

    # calculate b --- z1 - k * y1
    def calculateB_xz(self):
        if self.k_xz == -999:
            self.b_xz = -999
        else:
            b = self.z1 - self.k_xz * self.x1
            self.b_xz = b
        return self

    # generate function equation
    def generateEquation(self):
        self.euqation_xy = '%s * x + %s' % (self.k_xy, self.b_xy)
        self.euqation_yz = '%s * x + %s' % (self.k_yz, self.b_yz)
        self.euqation_xz = '%s * x + %s' % (self.k_xz, self.b_xz)
        return self

    # calculate the intersect point
    def calculateIntersect(self, otherLineObj):
        if self.k_xy == otherLineObj.k_xy:
            self.intersect = 'false'
            otherLineObj.intersect = 'false'
            return None

        if self.b_xy == otherLineObj.b_xy:
            x = 0
            y = self.b_xy
        else:
            x = (otherLineObj.b_xy - self.b_xy) / (self.k_xy - otherLineObj.k_xy)
            y = self.k_xy * x + self.b_xy

        # detect whether the point in the rectangle of self line
        if x > self.extent_xmin and x < self.extent_xmax:
            if y > self.extent_ymin and y < self.extent_ymax:
                self.intersect = 'true'
            else:
                self.intersect = 'false'
        else:
            self.intersect = 'false'

        # detect whether the point in the rectangle of another line
        if x > otherLineObj.extent_xmin and x < otherLineObj.extent_xmax:
            if y > otherLineObj.extent_ymin and y < otherLineObj.extent_ymax:
                otherLineObj.intersect = 'true'
            else:
                otherLineObj.intersect = 'false'
        else:
            otherLineObj.intersect = 'false'

        return x, y

    # calculate z value in intersect x,y
    def calculateZCoord_yz(self, x, y):
        if self.k_yz != -999:
            z = self.k_yz * y + self.b_yz
        else:
            if self.k_xz != -999:
                z = self.k_xz * x + self.b_xz
            # the line is totally vertical to the floor(x, y)
            else:
                z = -999
        return z

    # calculate z value in intersect x,y
    def calculateZCoord_xz(self, x, y):
        if self.k_xz != -999:
            z = self.k_xz * x + self.b_xz
        else:
            if self.k_yz != -999:
                z = self.k_yz * y + self.b_yz
            else:
                z = -999
        return z

    # make sure the x_min, y_min is less or equal than x_max, y_max in extent
    def _extentAvailableDetect(self):
        assert int(self.extent_xmin * 10 ** 8) <= int(
            self.extent_xmax * 10 ** 8), "Error --- Extent of line object is not available"
        assert int(self.extent_ymin * 10 ** 8) <= int(
            self.extent_ymax * 10 ** 8), "Error --- Extent of line object is not available"

    def calDisFromPnt(self, firstPoint):
        """
        usage: 使用第一个点坐标及 k 、 b 值来生成 line 对象
        :param firstPoint: Tuple --- 点坐标（x, y, z）
        :return: Double --- 距离值
        """
        x, y, z = firstPoint[0], firstPoint[1], firstPoint[2]

        # get k value
        originK = self.k_xy
        if originK == -999:
            k = 0
        elif -0.0001 <= originK <= 0.0001:
            k = -999
        else:
            k = -1 / originK

        # origin line is y = n
        if k == -999:
            # x = n (k is infinity)
            originY = self.k_xy * x + self.b_xy
            dis_xy = abs(y - originY)
            interY = self.b_xy
            interX = y
            interZ = self.calculateZCoord_yz(interX, interY)
        # origin line is x = n (k is -999, b is -999)
        elif k == 0:
            dis_xy = abs(x - self.extent_xmin)
            interY = y
            interX = self.extent_xmin
            interZ = self.calculateZCoord_yz(interX, interY)
        else:
            b = y - k * x
            calX = self.extent_xmin
            calY = k * calX + b
            calZ = self.calculateZCoord_yz(calX, calY)

            ext = (min(x, calX), min(y, calY), max(x, calX), max(y, calY))

            # calculate the point of intersect between line and it's vertical line
            newlineObj = lineEquation((x, y, z), (calX, calY, calZ), ext)
            interX, interY = self.calculateIntersect(newlineObj)
            interZ = self.calculateZCoord_yz(interX, interY)

            # calculate x, y, z in the point of intersect between two line obj
            dis_xy = math.sqrt((y - interY) ** 2 + (x - interX) ** 2)

        if interZ != -999:
            dis = math.sqrt(dis_xy ** 2 + (z - interZ) ** 2)
        else:
            dis = dis_xy

        return dis


# ---------- show message in toolbox ----------

def _addMessage(mes: str) -> None:
    print(mes)
    arcpy.AddMessage(mes)
    return None


def _addWarning(mes: str) -> None:
    print(mes)
    arcpy.AddWarning(mes)
    return None


def _addError(mes: str) -> None:
    print(mes)
    arcpy.AddError(mes)
    return None


def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        print(f"Method {func.__name__} start running ! ")
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        stop = datetime.datetime.now()
        cost = stop - start
        print("*" * 30)
        print(f"Method {func.__name__} start at {start}")
        print(f"Method {func.__name__} finish at {stop}")
        print(f"Method {func.__name__} total cost {cost}")
        print("*" * 30)
        return res

    return _wrapper


# used in python2
def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        print("Start function '{}' at : {}".format(func.__name__, start))
        res = func(*args, **kwargs)
        end = datetime.datetime.now()
        print("*" * 30)
        print("Start function '{}' at : {}".format(func.__name__, start))
        print("Finish function '{}' at : {}".format(func.__name__, end))
        print("Function '{}' total cost  at : {}".format(func.__name__, end - start))
        print("*" * 30)
        return res

    return _wrapper


# ---------- data fields process ----------

def _addField(*args, **kwargs):
    try:
        arcpy.AddField_management(*args, **kwargs)
    except:
        arcpy.DeleteField_management(*(args[:2]))
        arcpy.AddField_management(*args, **kwargs)


def addFiled(inFC: str, fieldName: str, fieldType: str, fieldLength: int = None, fieldPrec: int = None) -> str:
    if fieldLength:
        if fieldPrec:
            _addField(inFC, fieldName, fieldType, field_length=fieldLength, field_precision=fieldPrec)
        else:
            _addField(inFC, fieldName, fieldType, field_length=fieldLength)
    else:
        _addField(inFC, fieldName, fieldType)
    return inFC


# add a filed named "unic_id_" and calculate the unic id
def _addUnicIDField(inFeaShp: str, startNum: int) -> str:
    _addField(inFeaShp, "unic_id_", "LONG")
    codes = """a = 0
def calUnicField():
    global a
    a += 1
    return a"""
    arcpy.CalculateField_management(inFeaShp, "unic_id_", "calUnicField()", "PYTHON3", codes)
    return inFeaShp


# add coord fields
def _addCoordFields(inFC, feaType):
    fieldList = []
    expList = []
    if feaType == "point":
        fieldList = ["x_cen_", "y_cen_", "z_cen_"]
        expList = ["!shape.centroid.X!", "!shape.centroid.Y!", "!shape.centroid.Z!"]
    elif feaType == "line":
        fieldList = ["x_f_", "y_f_", "z_f_", "x_l_", "y_l_", "z_l_"]
        expList = ["!shape.firstPoint.X!", "!shape.firstPoint.Y!", "!shape.firstPoint.Z!",
                   "!shape.lastPoint.X!", "!shape.lastPoint.Y!", "!shape.lastPoint.Z!"]

    assert len(fieldList) > 0 and len(expList) > 0, f"Parameter 'feaType' --- {feaType} is not available"

    for i, each in enumerate(fieldList):
        _addField(inFC, each, "DOUBLE")
        arcpy.CalculateField_management(inFC, each, expList[i], "PYTHON3")


# --------------------------------- detect -----------------------------------

def fieldExist(inFC, fieldName):
    fieldList = arcpy.ListFields(inFC, fieldName)
    fieldCount = len(fieldList)
    if fieldCount == 1:
        return True
    else:
        return False


# get all feature count
def get_feature_count(feature_class, query):
    fields = arcpy.ListFields(feature_class)
    count = 0

    with arcpy.da.SearchCursor(feature_class, str(fields[0].name), query) as cursor:
        for row in cursor:
            count += 1

    return count


# statistic unic value of table
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def _copyFeature(inFC: str, outputPath: str, outputName: str) -> str:
    # keep origin workspace
    oriWS = None
    if arcpy.env.workspace:
        oriWS = arcpy.env.workspace

    folderType = arcpy.Describe(outputPath).dataType
    if folderType == "Workspace":
        if outputName[-4:] == ".shp":
            outputName = outputName[:-4]
    # .sde like directory
    elif folderType == "File":
        if outputName[-4:] == ".shp":
            outputName = outputName[:-4]
    else:
        if not outputName[-4:] == ".shp":
            outputName = outputName + ".shp"

    arcpy.CopyFeatures_management(inFC, os.path.join(outputPath, outputName))

    try:
        if oriWS:
            arcpy.env.workspace = oriWS
        else:
            arcpy.ClearEnvironment("workspace")
    except:
        pass

    return os.path.join(outputPath, outputName)


# 带参装饰器，用于将函数执行时的 arcgis 工作空间和函数外的工作空间隔离开来
# 将需要设置工作空间的函数上加上该装饰器，并将函数整体外再嵌套一层大函数，用于动态传递工作空间即可
def setTempWorkspace(workspace):
    def _inner(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # keep origin workspace
            oriWS = None
            if arcpy.env.workspace:
                oriWS = arcpy.env.workspace

            arcpy.env.workspace = workspace
            res = func(*args, **kwargs)

            try:
                if oriWS:
                    arcpy.env.workspace = oriWS
                else:
                    arcpy.ClearEnvironment("workspace")
            except:
                pass
            return res

        return _wrapper

    return _inner


# 设置临时工作空间的带参装饰器的使用示例
def demo_temp_workspace(outputPath, outputName):
    @setTempWorkspace(outputPath)
    def _wrapper(outputPath, outputName):
        print("当前环境为：", arcpy.env.workspace)
        print("输出数据名为：", availableDataName(outputPath, outputName))

    res = _wrapper(outputPath, outputName)
    print("当前环境为：", arcpy.env.workspace)
    return res


# auto create a available name for feature classes
def availableDataName(outputPath: str, outputName: str) -> str:
    @setTempWorkspace(outputPath)
    def _wrapper(outputPath: str, outputName: str) -> str:
        folderType = arcpy.Describe(outputPath).dataType
        if folderType == "Workspace":
            if outputName[-4:] == ".shp":
                outputName = outputName[:-4]
        # .sde like directory
        elif folderType == "File":
            if outputName[-4:] == ".shp":
                outputName = outputName[:-4]
        else:
            if not outputName[-4:] == ".shp":
                outputName = outputName + ".shp"

        return os.path.join(outputPath, outputName)

    res = _wrapper(outputPath, outputName)
    return res


# outputPath = r"D:\a\test.gdb"
# outputName = "test"
# demo_temp_workspace(outputPath, outputName)


def test(para1: str, para2: str) -> str:
    pass

def test1(para1, para2):
    pass

def qq(aa, bb, c, d):
    print(locals())
    # print(args)
    # print(type(args))
    # print(kwargs)
    # print(type(kwargs))

qq(1,2,c=3,d=4)

# print(test.__annotations__)
inspect.signature(test)
inspect.signature(test1)
sig = inspect.signature(test1)
print(sig.parameters)
parameters = [each.strip() for each in str(inspect.signature(qq))[1:-1].split(",")]
print(parameters)


# logging 装饰器
def logIt(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        logging.info(f" ======================== Start Function {func.__name__} ========================")
        parameters = [each.strip() for each in str(inspect.signature(func))[1:-1].split(",")]
        keyPara = kwargs
        for eachKey in keyPara:
            eachKey = eachKey.strip()
            if eachKey in parameters:
                parameters.remove(eachKey)

        mes = ""
        for i, eachPara in enumerate(parameters):
            mes += f"\n {eachPara}: {args[i]} "

        for eachKey, eachValue in keyPara.items():
            mes += f"\n {eachKey}: {eachValue} "

        logging.debug(mes)
        res = func(*args, **kwargs)

        return res

    return _wrapper



### 代码块区域

# ## ArcGIS Pro工具箱日志初始化
# import sys
# import os
# import logging
#
# # get arcgis pro toolbox directory
# tbxDir = os.path.dirname(sys.argv[0])
#
# # create log directory
# logDir = os.path.join(tbxDir, "tbx_log")
# try:
#     if not os.path.exists(logDir):
#         os.makedirs(logDir)
# except:
#     pass
#
# # make sure this script have rights to create file here
# createFileRights = False
# fileRightTest = os.path.join(logDir, "t_t_.txt")
# logFile = os.path.join(logDir, "tool1_gxthdem_log.txt")
# try:
#     with open(fileRightTest, "w", encoding="utf-8") as f:
#         f.write("create file rights test")
#     rights = True
# except:
#     rights = False
#
# if createFileRights:
#     logging.basicConfig(filename=logFile, filemode="w", level=logging.DEBUG,
#                         format="\n\n *** \n %(asctime)s    %(levelname)s ==== %(message)s \n *** \n\n")
# else:
#     logging.basicConfig(level=logging.DEBUG,
#                         format="\n\n *** \n %(asctime)s    %(levelname)s ==== %(message)s \n *** \n\n")
#
# try:
#     import arcpy
#     import functools
#
#     logging.debug("Module import success")
# except BaseException as e:
#     logging.error(str(e))
