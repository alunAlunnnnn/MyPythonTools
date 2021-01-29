import arcpy
import datetime
import functools
import os
import math

arcpy.env.overwriteOutput = True


class NoFieldError(Exception):
    pass


class pointError(Exception):
    pass


class calKError(Exception):
    pass


class GenerateSpatialIndexError(Exception):
    pass


class lineEquation:
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


class MyRas:
    def __init__(self, inRas):
        self.inRas = inRas
        self.getInfoFromRas(inRas)

    # get raster information
    def getInfoFromRas(self, inRas):
        oRas = arcpy.Raster(inRas)
        self.sr = oRas.spatialReference
        self.extent = [oRas.extent.XMin, oRas.extent.YMin, oRas.extent.XMax, oRas.extent.YMax]
        self.extentObj = oRas.extent
        self.lowerLeft = oRas.extent.lowerLeft
        self.nodata = oRas.noDataValue
        if oRas.format.lower() == "imagine image":
            self.format = ".img"
        elif oRas.format.lower() == "tiff":
            self.format = ".tif"
        elif oRas.format.lower() == "fgdbr":
            self.format = ""
        else:
            self.format = oRas.format
        self.maxValue = oRas.maximum
        self.minValue = oRas.minimum
        self.meanValue = oRas.mean
        self.meanCellWidth = oRas.meanCellWidth
        self.meanCellHeight = oRas.meanCellHeight
        self.dataPath = oRas.path
        self.pixelType = oRas.pixelType
        return self

    def toNDArray(self):
        ndArray = arcpy.RasterToNumPyArray(self.inRas)
        return ndArray


# get function runs time
def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        print(f"Start run function {func.__name__}, at {start}")

        res = func(*args, **kwargs)

        end = datetime.datetime.now()
        cost = end - start

        print("*" * 16)
        print(f"Function {func.__name__} run infomation")
        print(f"Start: {start}")
        print(f"End: {end}")
        print(f"Cost: {cost}")
        print("*" * 16)

        return res

    return _wrapper


# pause
def rasterProcessWithNumpy(inRas, outRas):
    oRas = arcpy.Raster(inRas)
    sr = oRas.spatialReference
    print("nodata value: ", oRas.noDataValue)
    print("sr: ", sr.name)

    # convert raster to numpy array
    ndArray = arcpy.RasterToNumPyArray(inRas, nodata_to_value=None)
    print(ndArray)

    # get the couner coord of left bottom
    lowerLeft = arcpy.Point(oRas.extent.XMin, oRas.extent.YMin)
    # get cell size
    cellWidth = oRas.meanCellWidth
    cellHeight = oRas.meanCellHeight

    # save ndArray to raster
    resRas = arcpy.NumPyArrayToRaster(ndArray, lowerLeft, cellWidth, cellHeight, value_to_nodata=oRas.noDataValue)
    resRas.save(outRas)


def getFCOIDName(inFC):
    oIDField = [each.name for each in arcpy.ListFields(inFC) if each.type == "OID"][0]
    return oIDField


def getFCOIDValue(inFC):
    oIDName = getFCOIDName(inFC)
    oIDValueList = []
    with arcpy.da.SearchCursor(inFC, [oIDName]) as cur:
        for row in cur:
            oIDValueList.append(row[0])
        del row

    return oIDName, oIDValueList


def _addConvertField(inFC):
    try:
        arcpy.AddField_management(inFC, "HSCONF_", "SHORT")
    except:
        arcpy.DeleteField_management(inFC, "HSCONF_")
        arcpy.AddField_management(inFC, "HSCONF_", "SHORT")

    if len([each.name for each in arcpy.ListFields(inFC) if each.name == "HSCONF_"]) > 0:
        arcpy.CalculateField_management(inFC, "HSCONF_", "1", "PYTHON_9.3")
        return inFC
    else:
        print(f"No Such Field Named HSCONF_ In Feature Class {inFC}")
        raise NoFieldError


def _delTempData(inFC, tmpDir):
    try:
        arcpy.DeleteField_management(inFC, "HSCONF_")
    except:
        pass

    # keep origin worksapce
    oriWorkspace = None
    if arcpy.env.workspace:
        oriWorkspace = arcpy.env.workspace

    # delete temp data
    arcpy.env.workspace = tmpDir

    tmpFCList = arcpy.ListFeatureClasses()
    tmpRasList = arcpy.ListRasters()

    for each in tmpFCList:
        try:
            arcpy.Delete_management(each)
        except:
            pass

    for each in tmpRasList:
        try:
            arcpy.Delete_management(each)
        except:
            pass

    if oriWorkspace:
        arcpy.env.workspace = oriWorkspace
    else:
        arcpy.ClearEnvironment("workspace")

    tmpFCList = arcpy.ListFeatureClasses()


def makeTempDir(outputPath):
    tmpDir = os.path.join(outputPath, "tmdRunDir_")

    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)

    return tmpDir


def vailOutdataFormat(outputPath, myRasObj, outputName):
    if outputPath[-4:] == ".gdb" or outputPath[-4:] == ".mdb":
        myRasObj.format = ""

        if outputName[-4:].lower() == ".tif" or outputName[-4:].lower() == ".img":
            outputName = outputName[:-4]

    return outputName


@getRunTime
def main(inRas, inPlg, outputPath, outputName):
    # get raster infomation
    myRas = MyRas(inRas)

    # make temp directory to save processing datas
    tmpDir = makeTempDir(outputPath)

    # get the objectid value
    oIDName, oIDValueList = getFCOIDValue(inPlg)

    # add a field "HSCONF_" with value 1
    inPlg = _addConvertField(inPlg)

    # set snap raster environment
    arcpy.env.snapRaster = inRas

    # # set fill None extent
    # arcpy.env.extent = myRas.extentObj

    # set compress type is none
    arcpy.env.compression = None

    # make sure the name of result raster is available
    outputName = vailOutdataFormat(outputPath, myRas, outputName)

    # create constant raster
    constantRas = arcpy.sa.CreateConstantRaster(0, "INTEGER", myRas.meanCellWidth, myRas.extentObj)

    arcpy.SetProgressor("step", "processing...", 0, len(oIDValueList) + 10, 1)

    plgLyr = arcpy.MakeFeatureLayer_management(inPlg)
    for eachValue in oIDValueList:
        # set processing
        arcpy.SetProgressorPosition()

        # select each feature
        selLyr = arcpy.SelectLayerByAttribute_management(plgLyr, "NEW_SELECTION", f"{oIDName} = {eachValue}")

        # convert eachplg to raster
        print(myRas.format)
        tmpRas = os.path.join(tmpDir, f"ras_{eachValue}{myRas.format}")
        print(tmpRas)
        arcpy.PolygonToRaster_conversion(selLyr, "HSCONF_", tmpRas,
                                         cellsize=min(myRas.meanCellWidth, myRas.meanCellHeight))

        # plg area raste mutilple dem data
        demTimeSave = os.path.join(tmpDir, f"demTime_{eachValue}{myRas.format}")
        demTimePlg = arcpy.sa.Times(arcpy.Raster(tmpRas), arcpy.Raster(inRas))
        # demTimePlg.save(demTimeSave)

        # calculate the value need to min
        minusRas = arcpy.sa.Con(demTimePlg >= round(demTimePlg.mean), (round(demTimePlg.mean) - demTimePlg),
                                -(demTimePlg - round(demTimePlg.mean)))

        tmpMinRas = os.path.join(tmpDir, f"min_{eachValue}{myRas.format}")
        minusRas.save(tmpMinRas)

        # # fill null data with zero to single raster
        # minFillRas = arcpy.sa.Con(arcpy.sa.IsNull(minusRas), 0, minusRas)
        #
        # # save single raster
        # singleMinusRas = os.path.join(tmpDir, f"singleMin_{eachValue}{myRas.format}")
        # minFillRas.save(singleMinusRas)

    #     tempPlusRas = arcpy.sa.Plus(constantRas, minFillRas)
    #
    #     constantRas = tempPlusRas
    #
    # singleMinusRas = os.path.join(outputPath, f"finPlusRas{myRas.format}")
    # # tempPlusRas.save(singleMinusRas)
    #
    # # dem plus total process raster
    # resDem = os.path.join(outputPath, outputName)
    # resDemObj = arcpy.sa.Plus(inRas, tempPlusRas)
    # resDemObj.save(resDem)
    #
    # arcpy.SetProgressorPosition()

    # clear snap raster environment
    # arcpy.ClearEnvironment("snapRaster")
    # arcpy.ClearEnvironment("extent")

    # delete temp field
    # _delTempData(inPlg, tmpDir)


inRas = arcpy.GetParameterAsText(0)
inPlg = arcpy.GetParameterAsText(1)
outputPath = arcpy.GetParameterAsText(2)
outputName = arcpy.GetParameterAsText(3)

if __name__ == "__main__":
    runData = datetime.datetime.now()
    limit = datetime.datetime.strptime("2021-03-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    if limit > runData:
        main(inRas, inPlg, outputPath, outputName)
    else:
        arcpy.AddError("failed")
