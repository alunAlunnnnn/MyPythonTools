import arcpy
import os
import functools
import datetime


# ---------- show message in toolbox ----------

def _addMessage(mes):
    print(mes)
    arcpy.AddMessage(mes)


def _addWarning(mes):
    print(mes)
    arcpy.AddWarning(mes)


def _addError(mes):
    print(mes)
    arcpy.AddError(mes)


def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        print("start at: {} ".format(start))
        res = func(*args, **kwargs)
        finish = datetime.datetime.now()
        print("finish at: {}".format(finish))
        cost = finish - start
        print("total cost: {}".format(cost))
        return res
    return _wrapper


# ---------- data fields process ----------

def _addField(inFeaShp, fieldName, fieldType):
    try:
        arcpy.AddField_management(inFeaShp, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFeaShp, fieldName)
        arcpy.AddField_management(inFeaShp, fieldName, fieldType)


# add a filed named "unic_id_" and calculate the unic id
def _addUnicIDField(inFeaShp):
    _addField(inFeaShp, "unic_id_", "LONG")
    codes = """a = 0
def calUnicField():
    global a
    a += 1
    return a"""
    arcpy.CalculateField_management(inFeaShp, "unic_id_", "calUnicField()", "PYTHON3", codes)


# add coord fields
def _addCoordFields(inFC, feaType):
    if feaType == "point":
        fieldList = ["x_cen_", "y_cen_", "z_cen_"]
        expList = ["!shape.centroid.X!", "!shape.centroid.Y!", "!shape.centroid.Z!"]
        for i, each in enumerate(fieldList):
            _addField(inFC, each, "DOUBLE")
            arcpy.CalculateField_management(inFC, each, expList[i], "PYTHON3")
    elif feaType == "line":
        fieldList = ["x_f_", "y_f_", "z_f_", "x_l_", "y_l_", "z_l_"]
        expList = ["!shape.firstPoint.X!", "!shape.firstPoint.Y!", "!shape.firstPoint.Z!",
                   "!shape.lastPoint.X!", "!shape.lastPoint.Y!", "!shape.lastPoint.Z!"]
        for i, each in enumerate(fieldList):
            _addField(inFC, each, "DOUBLE")
            arcpy.CalculateField_management(inFC, each, expList[i], "PYTHON3")


# ---------- line class ----------

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
            _addWarning('ERROR --- calculate k_xy faild,'
                        ' x1 is equal to x2, x1 is {}. x2 is {}'.format(self.x1, self.x2))
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
            _addWarning('ERROR --- calculate k_yz faild, y1 is equal to y2. y1 is %s' % self.y1)
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
            _addWarning('ERROR --- calculate k_xz faild, x1 is equal to x2. x1 is %s' % self.x1)
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
    def calculateZCoord_yz(self, y):
        z = self.k_yz * y + self.b_yz
        return z

    # calculate z value in intersect x,y
    def calculateZCoord_xz(self, x):
        z = self.k_xz * x + self.b_xz
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
                before use this, please call the function "generateSpatialIndex()" yet
        :param pnt:
        :param tolerance:
        :return:
        """
        pnt_x, pnt_y = pnt[0], pnt[1]
        pnt_index = None

        # generate the spatial index for point
        spaindex_step_x = round(float((totalExtent[2] - totalExtent[0]) / 10), 6) + 0.0001
        spaindex_step_y = round(float((totalExtent[3] - totalExtent[1]) / 10), 6) + 0.0001
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
        for i in range(1, 11):
            # if spatial index has finded, break the loop
            if find_key:
                break
            if pnt_y >= total_ext_ymax - i * spaindex_step_y:
                pnt_index_y = str(i)
                for j in range(1, 11):
                    if pnt_x >= total_ext_xmax - j * spaindex_step_x:
                        pnt_index_x = str(j)
                        pnt_index = (str(i) + "," + str(j))
                        find_key = True
                        break

        # no spatial index, no calculate
        assert pnt_index, "there are no spatial index in point"

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
        spaindex_step_x = round(float((totalExtent[2] - totalExtent[0]) / 10), 6) + 0.0001
        spaindex_step_y = round(float((totalExtent[3] - totalExtent[1]) / 10), 6) + 0.0001
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
        for i in range(1, 11):
            # if spatial index has finded, break the loop
            if find_key:
                break
            if self.extent_ymax >= total_ext_ymax - i * spaindex_step_y:
                self.spaindex_row = str(i)
                for j in range(1, 11):
                    if self.extent_xmax >= total_ext_xmax - j * spaindex_step_x:
                        self.spaindex_col = str(j)
                        self.spaindex = (str(i) + "," + str(j))
                        find_key = True
                        break
        return self
