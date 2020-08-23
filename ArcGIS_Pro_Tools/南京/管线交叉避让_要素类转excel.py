import arcpy
import os, sys, datetime, functools

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

@getRunTime
def generateUnicIDField(inFC):
    addMessage('generate unicid --- %s' % inFC)
    addField(inFC, 'unic_id_', 'LONG')
    codes = '''a = -1
def f():
    global a
    a += 1
    return a'''
    arcpy.CalculateField_management(inFC, 'unic_id_', 'f()', 'PYTHON3', codes)


@getRunTime
def addCoordFields_part(inFC):
    # coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f', 'y_temp_f', 'z_temp_f',
                      # 'x_temp_l', 'y_temp_l', 'z_temp_l']
    addMessage('add field --- %s' % inFC)

    coordFieldList = ['x_temp_f', 'y_temp_f', 'z_temp_f',
                      'x_temp_l', 'y_temp_l', 'z_temp_l']
    for eachField in coordFieldList:
        addField(inFC, eachField, 'DOUBLE')

    # # calculate centroid point
    # arcpy.CalculateField_management(inFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
    # arcpy.CalculateField_management(inFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')
    # arcpy.CalculateField_management(inFC, 'z_temp_c', '!shape.centroid.Z!', 'PYTHON3')

    # calculate first point
    arcpy.CalculateField_management(inFC, 'x_temp_f', '!shape.firstPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_f', '!shape.firstPoint.Y!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'z_temp_f', '!shape.firstPoint.Z!', 'PYTHON3')

    # calculate last point
    arcpy.CalculateField_management(inFC, 'x_temp_l', '!shape.lastPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_l', '!shape.lastPoint.Y!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'z_temp_l', '!shape.lastPoint.Z!', 'PYTHON3')


@getRunTime
def addCoordFields_ext(inFC):
    # coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f', 'y_temp_f', 'z_temp_f',
                      # 'x_temp_l', 'y_temp_l', 'z_temp_l']
    addMessage('add extent fields --- %s' % inFC)

    coordFieldList = ['ext_xmin', 'ext_xmax', 'ext_ymin',
                      'ext_ymax']

    for eachField in coordFieldList:
        addField(inFC, eachField, 'DOUBLE')

    # calculate first point
    arcpy.CalculateField_management(inFC, 'ext_xmin', '!shape.extent.XMin!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'ext_xmax', '!shape.extent.XMax!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'ext_ymin', '!shape.extent.YMin!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'ext_ymax', '!shape.extent.YMax!', 'PYTHON3')


@getRunTime
def main(gdb):
    global outdir
    arcpy.env.workspace = gdb

    feaList = arcpy.ListFeatureClasses()

    # add field
    for each in feaList:
        addMessage('Main process --- %s' % each)

        # 创建管径
        recalGJ(each)

        fields = [eachf.name for eachf in arcpy.ListFields(each) if
                  eachf.name.lower() != 'shape' and eachf.type != 'OID' and eachf.type != 'Geometry' and eachf.name.lower() != 'shape_length' and eachf.name.lower() != 'shape_area']
        fields.remove('GJ_TEMP_')
        print(fields)
        try:
            arcpy.management.DeleteField(each, fields)
        except:
            pass

        # add coord fields
        addCoordFields_part(each)

        # add unic id field
        generateUnicIDField(each)

        # add extent coord
        addCoordFields_ext(each)

        arcpy.TableToExcel_conversion(each, os.path.join(outdir, each + '.xlsx'), 'NAME')




# ****** parametra

meterial = ['软管', '光纤', 'PVC']
dataGDB = r'E:\南京管线\05南京管线_Multipatch\NJ_GX_ZZ_2.gdb'
outdir = r'E:\南京管线\excel_new_frompy'

main(dataGDB)

