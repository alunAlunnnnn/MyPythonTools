import arcpy
import os, sys, datetime, functools

# arcpy.env.overwriteOutput = True


def addMessage(mes):
    print(mes)
    arcpy.AddMessage(mes)


def addWarning(mes):
    print(mes)
    arcpy.AddWarning(mes)


def addError(mes):
    print(mes)
    arcpy.AddError(mes)


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

        for each in args:
            if not isinstance(each, tuple):
                addMessage('Point coord is not tuple type')
                raise pointError

            self.points.append((float(each[0]), float(each[1]), float(each[2])))

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
            raise calKError
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
            addError('ERROR --- calculate k_yz faild, y1 is equal to y2')
            raise calKError
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
            addError('ERROR --- calculate k_xz faild, x1 is equal to x2')
            raise calKError
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
            return None

        if self.b_xy == otherLineObj.b_xy:
            x = 0
            y = self.b_xy
        else:
            x = (otherLineObj.b_xy - self.b_xy) / (self.k_xy - otherLineObj.k_xy)
            y = self.k_xy * x + self.b_xy
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



def detectIntersect(inFC1, inFC2):
    f = open('D:/interDet.txt', 'w')
    with arcpy.da.SearchCursor(inFC1, ['SHAPE@', 'GJ']) as cur:
        with arcpy.da.SearchCursor(inFC2, ['SHAPE@', 'GJ']) as cur1:
            for row in cur:
                x_f = row[0].firstPoint.X
                y_f = row[0].firstPoint.Y
                z_f = row[0].firstPoint.Z
                x_c = row[0].centroid.X
                y_c = row[0].centroid.Y
                z_c = row[0].centroid.Z
                x_l = row[0].lastPoint.X
                y_l = row[0].lastPoint.Y
                z_l = row[0].lastPoint.Z
                print(row[1])
                print(type(row[1]))
                print(row[1][0])
                print(type(row[1][0]))
                # if ',' in row[1]:
                for each in row[1]:
                    print(each)
                row[1] = row[1].strip()
                if row[1] is None:
                    gj = 0.4
                elif 'x' in row[1]:
                    gj = float(row[1].split('x')[1])
                elif 'X' in row[1]:
                    gj = float(row[1].split('X')[1])

                line1 = lineEquation((x_f, y_f, z_f), (x_l, y_l, z_l))

                n = 0
                for row1 in cur1:
                    x_f_det = row1[0].firstPoint.X
                    y_f_det = row1[0].firstPoint.Y
                    z_f_det = row1[0].firstPoint.Z
                    x_c_det = row1[0].centroid.X
                    y_c_det = row1[0].centroid.Y
                    z_c_det = row1[0].centroid.Z
                    x_l_det = row1[0].lastPoint.X
                    y_l_det = row1[0].lastPoint.Y
                    z_l_det = row1[0].lastPoint.Z

                    row[1] = row[1].strip()
                    if row[1] is None:
                        gj_det = 0.4
                    elif 'x' in row[1]:
                        gj_det = float(row1[1].split('x')[1])
                    elif 'X' in row[1]:
                        gj_det = float(row1[1].split('X')[1])

                    line_det = lineEquation((x_f_det, y_f_det, z_f_det),
                                            (x_l_det, y_l_det, z_l_det))
                    res = line1.calculateIntersect(line_det)
                    z1 = line1.calculateZCoord_xz(res[0])
                    z_det = line_det.calculateZCoord_xz(res[0])
                    if z1 > z_det:
                        if z1 - gj/2 > z_det - gj_det/2 and z1 - gj/2 < z_det + gj_det/2:

                            n += 1
                    else:
                        if z1 + gj / 2 > z_det - gj_det / 2 and z1 + gj / 2 < z_det + gj_det / 2:
                            n += 1
                f.write('%s and %s --- %s \n' % (inFC1, inFC2, n))
    f.close()



def main(gdb):
    arcpy.env.workspace = gdb

    feaList = arcpy.ListFeatureClasses()
    # add field
    print(feaList)
    for each in feaList:
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
        print(newFeaList)
        for eachDet in newFeaList:
            # each data
            detectIntersect(each, eachDet)







# ****** parametra

meterial = ['软管', '光纤', 'PVC']
dataGDB = r'E:\南京管线\05南京管线_Multipatch\NJ_GX_ZZ.gdb'

# line1 = lineEquation((329989.8825, 346842.661, 7.3505), (329992.178, 346851.604, 7.361))
# line2 = lineEquation((329988.186, 346841.2545, 6.9525), (329983.494, 346842.673, 7.067))
# print(line1.calculateIntersect(line2))
#
# print(line1.calculateZCoord_xz(329989.42530686007))
main(dataGDB)

