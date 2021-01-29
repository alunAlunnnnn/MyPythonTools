import arcpy
import os
import datetime
import functools


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


def getAllRaster(inputPath):
    rasList = []
    for root, dir, files in os.walk(inputPath):
        if files:
            ras = [os.path.join(root, each) for each in files if each[:3] == "min" and each[-4:] == ".img"]
            # print(ras)
            rasList += ras

    return rasList


def mergeAllRaster(rasList, outputPath, outputName):
    arcpy.MosaicToNewRaster_management(rasList, outputPath, outputName, pixel_type="32_BIT_FLOAT",
                                       number_of_bands=1)

    return os.path.join(outputPath, outputName)


def fillNullAndPlus(inputOriDEM, mosaicRaster, outputPath, outputName):
    myRas = MyRas(inputOriDEM)

    # set compress type is none
    arcpy.env.compression = None
    arcpy.env.snapRaster = inputOriDEM
    arcpy.env.extent = myRas.extentObj

    # data fill null
    fillNullRas = arcpy.sa.Con(arcpy.sa.IsNull(mosaicRaster), 0, mosaicRaster)

    fillNullRas.save(os.path.join(outputPath, "demFillNull.img"))

    # calculate res raster
    resRas = arcpy.sa.Plus(inputOriDEM, fillNullRas)

    resRas.save(os.path.join(outputPath, outputName))


@getRunTime
def main(inputPath, outputPath, mosaicData, outputName):
    rasList = getAllRaster(inputPath)
    print(rasList)
    mosaicRaster = mergeAllRaster(rasList, outputPath, mosaicData)
    fillNullAndPlus(inputOriDEM, mosaicRaster, outputPath, outputName)


inputOriDEM = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\DEM\DEM30.img"
inputPath = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\数据拆分_30米\processing_raster"
outputPath = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\代码debug"
mosaicName = "mosaic_30m.img"
outputName = "dem_yaping_30m.img"

if __name__ == "__main__":
    main(inputPath, outputPath, mosaicName, outputName)
