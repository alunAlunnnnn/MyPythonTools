import arcpy
import os, sys, datetime, functools
from numba import jit

# arcpy.env.overwriteOutput = True


def addMessage(mes):
    print(mes)
    # arcpy.AddMessage(mes)


def addWarning(mes):
    print(mes)
    # arcpy.AddWarning(mes)


def addError(mes):
    print(mes)
    # arcpy.AddError(mes)


# get run time for each function
def getRunTime(func):
    @functools.wraps(func)
    def _getRunTime(*args, **kwargs):
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        finish = datetime.datetime.now()
        cost = finish - start
        addMessage('start at: %s, finish at: %s \n cost : %s' % (start, finish, cost))
        return res
    return _getRunTime


# points type is not tuple
class pointError(Exception):
    pass


class calKError(Exception):
    pass


class lineEquation:
    def __init__(self, *args):
        # save all points
        self.points = []

        for each in args[:2]:
            if not isinstance(each, tuple):
                addMessage('Point coord is not tuple type')
                raise pointError

            self.points.append((float(each[0]), float(each[1]), float(each[2])))

        self.extent_xmin = args[2][0]
        self.extent_ymin = args[2][1]
        self.extent_xmax = args[2][2]
        self.extent_ymax = args[2][3]

        # get point number, start with 1
        self.pntNum = len(args)

        # set coord of start point and finish point
        self.x1 = self.points[0][0]
        self.y1 = self.points[0][1]
        self.z1 = self.points[0][2]
        self.x2 = self.points[-1][0]
        self.y2 = self.points[-1][1]
        self.z2 = self.points[-1][2]

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
            addError('ERROR --- calculate k_xy faild, x1 is equal to x2')
            self.k_xy = 0
            return self
            # raise calKError
        k = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.k_xy = k
        return self

    # calculate b --- y1 - k * x1
    def calculateB_xy(self):
        b = self.y1 - self.k_xy * self.x1
        self.b_xy = b
        return self

    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_yz(self):
        if self.y1 == self.y2:
            # addError('ERROR --- calculate k_yz faild, y1 is equal to y2. y1 is %s' % self.y1)
            self.k_yz = 0
            return self
            # raise calKError
        k = (self.z2 - self.z1) / (self.y2 - self.y1)
        self.k_yz = k
        return self

    # calculate b --- z1 - k * y1
    def calculateB_yz(self):
        b = self.z1 - self.k_yz * self.y1
        self.b_yz = b
        return self

    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_xz(self):
        if self.x1 == self.x2:
            # addError('ERROR --- calculate k_xz faild, x1 is equal to x2')
            self.k_xz = 0
            return self
            # raise calKError
        k = (self.z2 - self.z1) / (self.x2 - self.x1)
        self.k_xz = k
        return self

    # calculate b --- z1 - k * y1
    def calculateB_xz(self):
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


def addField(inFC, fieldName, fieldType):
    fieldType = fieldType.upper()
    if fieldType.lower() == 'string':
        fieldType = 'TEXT'
    try:
        arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType)


def addPoints(endPntCoord, intersecPntCoord, targetZ):
    pass


def addCoordFields(inFC):
    coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f', 'y_temp_f', 'z_temp_f',
                      'x_temp_l', 'y_temp_l', 'z_temp_l']
    for eachField in coordFieldList:
        addField(inFC, eachField, 'DOUBLE')

    # calculate centroid point
    arcpy.CalculateField_management(inFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'z_temp_c', '!shape.centroid.Z!', 'PYTHON3')

    # calculate first point
    arcpy.CalculateField_management(inFC, 'x_temp_f', '!shape.firstPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_f', '!shape.firstPoint.Y!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'z_temp_f', '!shape.firstPoint.Z!', 'PYTHON3')

    # calculate last point
    arcpy.CalculateField_management(inFC, 'x_temp_l', '!shape.lastPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_l', '!shape.lastPoint.Y!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'z_temp_l', '!shape.lastPoint.Z!', 'PYTHON3')


#
def recalGJ(inFC1):
    addField(inFC1, 'GJ_TEMP_', 'DOUBLE')
    codes = '''def f(a):
    	try:
    		data = a.strip()
    		if data is None:
    			data = 20
    		elif float(data) == 0:
    			data = 20
    		return float(data) / 1000
    	except:
    		return 0.02'''
    arcpy.CalculateField_management(inFC1, 'GJ_TEMP_', 'f(!GJ!)', 'PYTHON3', codes)


def generateUnicIDField(inFC):
    addField(inFC, 'unic_id_', 'LONG')
    codes = '''a = -1
def f():
    global a
    a += 1
    return a'''
    arcpy.CalculateField_management(inFC, 'unic_id_', 'f()', 'PYTHON3', codes)


@getRunTime
def detectIntersect(inFC1, inFC2, interDetectFile):
    addMessage('now is processing data %s and %s' % (inFC1, inFC2))

    # add a field named 'GJ_TEMP_', calculate the field from GJ
    recalGJ(inFC1)
    recalGJ(inFC2)

    # generate unic id field named 'unic_id_'
    generateUnicIDField(inFC1)
    generateUnicIDField(inFC2)

    rowNum1 = -1
    with arcpy.da.SearchCursor(inFC1, ['SHAPE@', 'GJ_TEMP_', 'unic_id_']) as cur:
        rowNum1 += 1
        with arcpy.da.SearchCursor(inFC2, ['SHAPE@', 'GJ_TEMP_', 'unic_id_']) as cur1:
            for row in cur:
                rowNum2 = -1
                x_f = row[0].firstPoint.X
                y_f = row[0].firstPoint.Y
                z_f = row[0].firstPoint.Z
                x_c = row[0].centroid.X
                y_c = row[0].centroid.Y
                z_c = row[0].centroid.Z
                x_l = row[0].lastPoint.X
                y_l = row[0].lastPoint.Y
                z_l = row[0].lastPoint.Z

                extent_xmin_row0 = row[0].extent.XMin
                extent_xmax_row0 = row[0].extent.XMax
                extent_ymin_row0 = row[0].extent.YMin
                extent_ymax_row0 = row[0].extent.YMax

                extent = (extent_xmin_row0, extent_ymin_row0,
                          extent_xmax_row0, extent_ymax_row0)

                gj = float(row[1])

                line1 = lineEquation((x_f, y_f, z_f), (x_l, y_l, z_l), extent)

                n = 0
                cur1.reset()
                for row1 in cur1:
                    rowNum2 += 1
                    x_f_det = row1[0].firstPoint.X
                    y_f_det = row1[0].firstPoint.Y
                    z_f_det = row1[0].firstPoint.Z
                    x_c_det = row1[0].centroid.X
                    y_c_det = row1[0].centroid.Y
                    z_c_det = row1[0].centroid.Z
                    x_l_det = row1[0].lastPoint.X
                    y_l_det = row1[0].lastPoint.Y
                    z_l_det = row1[0].lastPoint.Z

                    extent_xmin_row1 = row1[0].extent.XMin
                    extent_xmax_row1 = row1[0].extent.XMax
                    extent_ymin_row1 = row1[0].extent.YMin
                    extent_ymax_row1 = row1[0].extent.YMax
                    extent = (extent_xmin_row1, extent_ymin_row1,
                              extent_xmax_row1, extent_ymax_row1)

                    gj_det = float(row1[1])

                    try:
                        line_det = lineEquation((x_f_det, y_f_det, z_f_det),
                                                (x_l_det, y_l_det, z_l_det),
                                                extent)
                    except:
                        addError('ERROR --- inFC1 is %s - in row %s,'
                                 ' inFC2 is %s - in row %s' % (inFC1, rowNum1, inFC2, rowNum2))
                        raise

                    # get the result of intersect point
                    res = line1.calculateIntersect(line_det)
                    if line1.intersect == 'true' and line_det.intersect == 'true':
                        if line1.k_xz != 0:
                            z1 = line1.calculateZCoord_xz(res[0])
                        else:
                            z1 = line1.calculateZCoord_yz(res[0])

                        if line_det.k_xz != 0:
                            z_det = line_det.calculateZCoord_xz(res[0])
                        else:
                            z_det = line_det.calculateZCoord_yz(res[0])

                        z1 = float(z1)
                        z_det = float(z_det)
                        gj = float(gj) * 0.9
                        gj_det = float(gj_det) * 0.9

                        if z1 > z_det:
                            if (z1 - gj/2) < (z_det + gj_det/2):
                                interDetectFile.write('data %s - %s and %s'
                                                      ' - %s \n' % (inFC1, row[2], inFC2, row1[2]))
                                n += 1
                        else:
                            if (z1 + gj/2) > (z_det - gj_det/2):
                                interDetectFile.write('data %s - %s and %s'
                                                      ' - %s \n' % (inFC1, row[2], inFC2, row1[2]))
                                n += 1


def main(gdb):
    arcpy.env.workspace = gdb

    feaList = arcpy.ListFeatureClasses()
    # add field
    for each in feaList:
        print('feaList is : ', feaList)
        # get all feature
        newFeaList = feaList[:]
        feaType = each[:2]
        special = False

        if feaType == 'XX':
            feaType = each[3:6]
            special = True

        # del data self
        delIndex = newFeaList.index(each)
        newFeaList.pop(delIndex)

        # del same type data
        for eachFea in newFeaList:
            if special:
                if eachFea[3:6] == feaType:
                    delIndex_t = newFeaList.index(eachFea)
                    newFeaList.pop(delIndex_t)
            else:
                if eachFea[:2] == feaType:
                    delIndex_t = newFeaList.index(eachFea)
                    newFeaList.pop(delIndex_t)
        print('newFeaList is : ', newFeaList)
        for eachDet in newFeaList:
            # write result to a txt file
            interDetectFile = open(r'D:/gxjc/%s_%s.txt' % (each, eachDet), 'w')

            # each data
            detectIntersect(each, eachDet, interDetectFile)

            interDetectFile.close()

        # delete the data have been detected
        delIndex = feaList.index(each)
        feaList.pop(delIndex)


# ****** parametra

meterial = ['软管', '光纤', 'PVC']
dataGDB = r'E:\南京管线\05南京管线_Multipatch - 副本\gdb.gdb'
# dataGDB = r'E:\南京管线\05南京管线_Multipatch\NJ_GX_ZZ_1.gdb'

# line1 = lineEquation((329989.8825, 346842.661, 7.3505), (329992.178, 346851.604, 7.361))
# line2 = lineEquation((329988.186, 346841.2545, 6.9525), (329983.494, 346842.673, 7.067))
# print(line1.calculateIntersect(line2))
#
# print(line1.calculateZCoord_xz(329989.42530686007))
main(dataGDB)

