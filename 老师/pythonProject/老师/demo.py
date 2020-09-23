import math
import os
import arcpy
import functools
import datetime
import arcpy.da
import re

arcpy.env.overwriteOutput = True


# ---------- line class ----------

def _addMessage(mes):
    print(mes)
    arcpy.AddMessage(mes)


def _addWarning(mes):
    print(mes)
    arcpy.AddWarning(mes)


def _addError(mes):
    print(mes)
    arcpy.AddError(mes)


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
                _addMessage('Point coord is not tuple type')
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
            # _addWarning('ERROR --- calculate k_xy faild,'
            #             ' x1 is equal to x2, x1 is {}. x2 is {}'.format(self.x1, self.x2))
            # in math k is infinity / -infinity
            self.k_xy = -999
            return self
            # raise calKError
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
            # _addWarning('ERROR --- calculate k_yz faild, y1 is equal to y2. y1 is %s' % self.y1)
            self.k_yz = -999
            return self
            # raise calKError
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
            # _addWarning('ERROR --- calculate k_xz faild, x1 is equal to x2. x1 is %s' % self.x1)
            self.k_xz = -999
            return self
            # raise calKError
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

    # detect the point can touch the line with a tolerance or not
    def pointTouchDet(self, pnt, tolerance, totalExtent):
        """
        usage: used to detect that, the point is in the line with a tolerance num.
                before use this, please call the function "generateSpatialIndex()" first
        :param pnt:(x, y)
        :param tolerance:
        :return:
        """
        pnt_x, pnt_y = pnt[0], pnt[1]
        pnt_index = None
        spatialIndex_x = 1
        spatialIndex_y = 1
        # generate the spatial index for point
        spaindex_step_x = round(float((totalExtent[2] - totalExtent[0]) / spatialIndex_x), 6) + 0.0001
        spaindex_step_y = round(float((totalExtent[3] - totalExtent[1]) / spatialIndex_y), 6) + 0.0001
        total_ext_ymax = totalExtent[3]
        total_ext_xmax = totalExtent[2]

        # detect whether is out of the ply's extent
        if (self.extent_xmax > totalExtent[2] + 0.0001 or self.extent_ymax > totalExtent[3] + 0.0001
                or self.extent_xmin < totalExtent[0] - 0.0001 or self.extent_ymin < totalExtent[1] - 0.0001):
            if self.extent_xmax > totalExtent[2] + 0.0001:
                print("pnt xxxx1xxxx pnt")
            if self.extent_ymax > totalExtent[3] + 0.0001:
                print("pnt xxxx2xxxx pnt")
            if self.extent_xmin < totalExtent[0] - 0.0001:
                print("pnt xxxx3xxxx pnt")
            if self.extent_ymin < totalExtent[1] - 0.0001:
                print("pnt xxxx4xxxx pnt")
            _addError("Error --- generate spatial index for point failed, "
                      "the point is ({}, {})".format(pnt_x, pnt_y))
            _addError("total extent is {}".format(totalExtent))
            raise GenerateSpatialIndexError

        find_key = False
        # for i in range(1, 11):
        for i in range(1, spatialIndex_y + 1):
            # if spatial index has finded, break the loop
            if find_key:
                break
            if pnt_y >= total_ext_ymax - i * spaindex_step_y:
                pnt_index_y = str(i)
                # for j in range(1, 11):
                for j in range(1, spatialIndex_x + 1):
                    if pnt_x >= total_ext_xmax - j * spaindex_step_x:
                        pnt_index_x = str(j)
                        pnt_index = (str(i) + "," + str(j))
                        find_key = True
                        break

        # no spatial index, no calculate
        assert pnt_index, "there are no spatial index in point"

        # set a default tolerance if None is inputed
        if tolerance is None:
            tolerance = math.sqrt((self.y2 - self.y1) ** 2 + (self.x2 - self.x1) ** 2) / 10000

        # match spatial index
        if pnt_index == self.spaindex:
            # point is in the extent of polyline
            if (self.extent_xmin - tolerance <= pnt_x <= self.extent_xmax + tolerance
                    and self.extent_ymin - tolerance <= pnt_y <= self.extent_ymax + tolerance):
                # point is in the extent of polyline
                # detect whether the point is on the line

                # vertical line
                if self.k_xy == -999:
                    if min(self.x1, self.x2) - tolerance <= pnt_x <= max(self.x1, self.x2) + tolerance:
                        if min(self.y1, self.y2) - tolerance <= pnt_y <= max(self.y1, self.y2) + tolerance:
                            return True
                        else:
                            return False
                    else:
                        return False
                # horizon line
                elif self.k_xy == 0:
                    if min(self.y1, self.y2) - tolerance <= pnt_y <= max(self.y1, self.y2) + tolerance:
                        if min(self.x1, self.x2) - tolerance <= pnt_x <= max(self.x1, self.x2) + tolerance:
                            return True
                        else:
                            return False
                    else:
                        return False
                # calculate the point in line with k_xy
                else:
                    det_y = self.k_xy * pnt_x + self.b_xy
                    if det_y - tolerance <= pnt_y <= det_y + tolerance:
                        return True
                    else:
                        return False
            # point is out of ply's extent
            else:
                return False
        # the spatial index between point and ply is not equal
        else:
            return False

    def generateSpatialIndex(self, totalExtent):
        """
        usage: generate spatial index, now is generate 10*10 grid index.

        index number as this:
         ----------
        |1,10|...|1,2|1,1|
         ----------
        |2,10|...|2,2|2,1|
         ----------
        |...........|
        |.          |
        |.          |
         -----------
        |10,10|...|10,2|10,1|

        :param totalExtent: (xmin, ymin, xmax, ymax)
        :return:
        """
        spatialIndex_x = 1
        spatialIndex_y = 1
        spaindex_step_x = round(float((totalExtent[2] - totalExtent[0]) / spatialIndex_x), 8) + 0.00001
        spaindex_step_y = round(float((totalExtent[3] - totalExtent[1]) / spatialIndex_y), 8) + 0.00001
        total_ext_ymax = totalExtent[3]
        total_ext_xmax = totalExtent[2]

        self.spaind_totalext = totalExtent

        if (self.extent_xmax > totalExtent[2] + 0.0001 or self.extent_ymax > totalExtent[3] + 0.0001
                or self.extent_xmin < totalExtent[0] - 0.0001 or self.extent_ymin < totalExtent[1] - 0.0001):
            if self.extent_xmax > totalExtent[2] + 0.0001:
                print("xxxx1xxxx")
            if self.extent_ymax > totalExtent[3] + 0.0001:
                print("xxxx2xxxx")
            if self.extent_xmin < totalExtent[0] - 0.0001:
                print("xxxx3xxxx")
            if self.extent_ymin < totalExtent[1] - 0.0001:
                print("xxxx4xxxx")
            _addError("Error --- generate spatial index failed, "
                      "line object's extent is not in total extent. "
                      "the line's first point is ({}, {})".format(self.x1, self.y1))
            _addError("total extent is {}".format(totalExtent))
            _addError("ply extent is {}".format(self.extent))
            raise GenerateSpatialIndexError

        find_key = False
        # for i in range(1, 11):
        for i in range(1, spatialIndex_y + 1):
            # if spatial index has finded, break the loop
            if find_key:
                break
            if self.extent_ymax >= total_ext_ymax - i * spaindex_step_y:
                self.spaindex_row = str(i)
                # for j in range(1, 11):
                for j in range(1, spatialIndex_y + 1):
                    if self.extent_xmax >= total_ext_xmax - j * spaindex_step_x:
                        self.spaindex_col = str(j)
                        self.spaindex = (str(i) + "," + str(j))
                        find_key = True
                        break
        return self

    def setPipeSize(self, pipesize):
        if isinstance(pipesize, int) or isinstance(pipesize, float):
            self.pipeSize = pipesize
        else:
            _addWarning("Warning --- pipe size is not a number type, pipe size init failed")
            self.pipeSize = None

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


# auto create a available name for feature classes
def availableDataName(outputPath, outputName):
    @setTempWorkspace(outputPath)
    def _wrapper(outputPath, outputName):
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


# add a filed named "unic_id_" and calculate the unic id
def _addUnicIDField(inFeaShp, startNum):
    _addField(inFeaShp, "unic_id_", "LONG")
    codes = """a = {}
def calUnicField():
    global a
    a += 1
    return a""".format(int(startNum) - 1)
    arcpy.CalculateField_management(inFeaShp, "unic_id_", "calUnicField()", "PYTHON_9.3", codes)
    return inFeaShp


def _copyFeature(inFC, outputPath, outputName):
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


def _addIDField(inFeaShp, startNum):
    addFiled(inFeaShp, "unic_id_", "LONG")
    codes = """a = {}
def calUnicField():
    global a
    a += 1
    return a""".format(int(startNum) - 1)
    arcpy.CalculateField_management(inFeaShp, "unic_id_", "calUnicField()", "PYTHON_9.3", codes)
    return inFeaShp


# count all features
def getFeaCount(inFC):
    num = int(arcpy.GetCount_management(inFC)[0])
    return num


# get the nearest point from road line to school
def getNearestPoint(inPnt, inPly):
    # make sure there are only once feature put into this method
    assert getFeaCount(inPnt) == 1, "The feature number of point feature class is not 1"
    assert getFeaCount(inPly) == 1, "The feature number of polyline feature class is not 1"

    # save the nearest point coordinate into school point feature class's attribute
    res = arcpy.Near_analysis(inPnt, inPly, location="LOCATION")
    with arcpy.da.SearchCursor(res, ["NEAR_X", "NEAR_Y"]) as cur:
        for row in cur:
            x, y = row[0], row[1]

    res = (x, y)
    print(res)

    return res


def initProcessFC(inFC, outputPath):
    @setTempWorkspace(outputPath)
    def _wrapper(inFC, outputPath):
        outputName = arcpy.Describe(inFC).name
        startNum = 1
        copyFC = _copyFeature(inFC, outputPath, outputName)
        _addUnicIDField(copyFC, startNum)
        pntCount = getFeaCount(copyFC)

        return copyFC, pntCount

    res = _wrapper(inFC, outputPath)

    return res


def getFullExtentOfFC(inFC):
    with arcpy.da.SearchCursor(inFC, ["SHAPE@"]) as cur:
        xMinList, yMinList, xMaxList, yMaxList = [], [], [], []
        for row in cur:
            xMinList.append(row[0].extent.XMin)
            yMinList.append(row[0].extent.YMin)
            xMaxList.append(row[0].extent.XMax)
            yMaxList.append(row[0].extent.YMax)
    xMin, yMin, xMax, yMax = min(xMinList), min(yMinList), max(xMaxList), max(yMaxList)
    res = (xMin, yMin, xMax, yMax)

    return res


def getCoordFromWKT(WKTString):
    obj = re.search('[\(].*', WKTString)
    if obj:
        tarStr = " " + obj.group()[2:-2]
        tempList = [each[1:] for each in tarStr.split(",") if each.startswith(" ")]
        coordList = [tuple(map(float, each.split(" "))) for each in tempList]

        return coordList
    else:
        _addError("")
        raise


def getPntIndexOfLinePart(lineCoordList, pntCoord, plyExtent):
    pntNum = len(lineCoordList)
    for i in range(pntNum - 1):
        j = i + 1

        x1, y1 = lineCoordList[i]
        x2, y2 = lineCoordList[j]

        lineObj = lineEquation((x1, y1, 0), (x2, y2, 0),
                               (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
        lineObj.generateSpatialIndex(plyExtent)
        detRes = lineObj.pointTouchDet(pntCoord, None, plyExtent)
        if detRes:
            return (i, j)
    else:
        _addError("Point is not touch any part of the line selected")
        raise


def generateServiceArea(sr, nearCoord, lineCorLst, startIndexLeft, startIndexRight):
    pntLeft = lineCorLst[startIndexLeft]

    # *** Directory1 --- from coord point to road's start point ***
    coordsListLeft = [lineCorLst[i] for i in range(startIndexLeft, -1, -1)]
    coordsListLeft.insert(0, nearCoord)
    for i in range(len(coordsListLeft) - 1):
        pntFrom = coordsListLeft[i]
        pntTo = coordsListLeft[i + 1]
        lenFirstLeft = math.sqrt((pntFrom[1] - pntTo[1]) ** 2 + (pntFrom[0] - pntTo[0]) ** 2)

        # this is radians not degrees
        alpha = math.asin((pntFrom[1] - pntTo[1]) / lenFirstLeft)

        if lenFirstLeft < sr:
            sp = sr - lenFirstLeft

            rad = math.pi / 2 + alpha
            yNew = sp * math.sin(rad) + pntTo[1]
            xNew = sp * math.cos(rad) + pntTo[0]

            rad = 3 * math.pi / 2 + alpha
            yNew = sp * math.sin(rad) + pntTo[1]
            xNew = sp * math.cos(rad) + pntTo[0]

            sr -= lenFirstLeft
        else:
            yEndLeft = pntFrom[1] - sr * math.sin(alpha)
            xEndLeft = pntFrom[0] - sr * math.cos(alpha)


    # *** Directory2 --- from coord point to road's end point ***



def main(inPnt, inPly, outputPath):
    processPnt, pntFeaCount = initProcessFC(inPnt, outputPath)
    processPly, plyFeaCount = initProcessFC(inPly, outputPath)

    print(pntFeaCount)
    print(plyFeaCount)

    plyExt = getFullExtentOfFC(processPly)

    for i in range(1, pntFeaCount + 1):
        pntLyr = arcpy.MakeFeatureLayer_management(processPnt, "pnt_lyr")
        arcpy.SelectLayerByAttribute_management(pntLyr, "NEW_SELECTION", "unic_id_={}".format(i))
        for j in range(1, plyFeaCount + 1):
            plyLyr = arcpy.MakeFeatureLayer_management(processPly, "ply_lyr")
            arcpy.SelectLayerByAttribute_management(plyLyr, "NEW_SELECTION", "unic_id_={}".format(j))

            # (x, y) --- x, y is Double --- get the nearest point from road line to school
            nearCoord = getNearestPoint(pntLyr, plyLyr)

            # get eachLine's coord
            with arcpy.da.SearchCursor(plyLyr, ["SHAPE@WKT"]) as cur:
                for row in cur:
                    WKTString = row[0]

            lineCoordList = getCoordFromWKT(WKTString)

            # get a copy
            lineCorLst = lineCoordList[:]

            print(lineCoordList)
            # get the nearest point's left and right road vertices index
            startPntIndex1, startPntIndex2 = getPntIndexOfLinePart(lineCoordList, nearCoord, plyExt)
            print(nearCoord)
            print(startPntIndex1, startPntIndex2)
            print(lineCoordList)



dataSchool = r"..\demo\school.shp"
dataRoads = r"..\demo\roads.shp"
outputPath = r"..\demo\res"
s = 100

if __name__ == "__main__":
    main(dataSchool, dataRoads, outputPath)
