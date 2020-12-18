import arcpy
import numpy as np
import pandas as pd
import datetime
import functools
import os

arcpy.env.overwriteOutput = True


class NoFieldError(Exception):
    pass


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
            self.format = "img"
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

    # set fill None extent
    arcpy.env.extent = myRas.extentObj

    # create constant raster
    constantRas = arcpy.sa.CreateConstantRaster(0, "INTEGER", myRas.meanCellWidth, myRas.extentObj)

    plgLyr = arcpy.MakeFeatureLayer_management(inPlg)
    singleMinRasLst = []
    for eachValue in oIDValueList:
        # select each feature
        selLyr = arcpy.SelectLayerByAttribute_management(plgLyr, "NEW_SELECTION", f"{oIDName} = {eachValue}")

        # convert eachplg to raster
        print(myRas.format)
        tmpRas = os.path.join(tmpDir, f"ras_{eachValue}.{myRas.format}")
        print(tmpRas)
        arcpy.PolygonToRaster_conversion(selLyr, "HSCONF_", tmpRas,
                                         cellsize=min(myRas.meanCellWidth, myRas.meanCellHeight))

        # plg area raste mutilple dem data
        demTimeSave = os.path.join(tmpDir, f"demTime_{eachValue}.{myRas.format}")
        demTimePlg = arcpy.sa.Times(arcpy.Raster(tmpRas), arcpy.Raster(inRas))
        demTimePlg.save(demTimeSave)

        # calculate the value need to min
        minusRas = arcpy.sa.Con(demTimePlg >= round(demTimePlg.mean), (round(demTimePlg.mean) - demTimePlg), -(demTimePlg - round(demTimePlg.mean)))

        tmpMinRas = os.path.join(tmpDir, f"min_{eachValue}.{myRas.format}")
        minusRas.save(tmpMinRas)

        # fill null data with zero to single raster
        minFillRas = arcpy.sa.Con(arcpy.sa.IsNull(minusRas), 0, minusRas)

        # # save single raster
        singleMinusRas = os.path.join(tmpDir, f"singleMin_{eachValue}.{myRas.format}")
        minFillRas.save(singleMinusRas)
        #
        # # get all single minus rasters
        # singleMinRasLst.append(singleMinusRas)

        #
        # tempPlusRas = arcpy.sa.Con(constantRas + minFillRas)
        tempPlusRas = arcpy.sa.Plus(constantRas, minFillRas)

        constantRas = tempPlusRas

    singleMinusRas = os.path.join(outputPath, f"finPlusRas.{myRas.format}")
    tempPlusRas.save(singleMinusRas)

    # dem plus total process raster
    resDem = os.path.join(outputPath, outputName)
    resDemObj = arcpy.sa.Plus(inRas, tempPlusRas)
    resDemObj.save(resDem)

    # clear snap raster environment
    arcpy.ClearEnvironment("snapRaster")
    arcpy.ClearEnvironment("extent")

    # delete temp field
    # _delTempData(inPlg, tmpDir)


inRas = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_中间数据\ASTGTM_N28E120X.img"
outRas = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_中间数据\ASTGTM_N28E120X_process.img"
# inPlg = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_原始数据\建筑.gdb\plg_buffer"
inPlg = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_原始数据\建筑.gdb\plg_buffer"
outputPath = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_中间数据\tempRas"
outputName = r"aa"

main(inRas, inPlg, outputPath, outputName)

# todo test the raster format with .img .tif and esri grid