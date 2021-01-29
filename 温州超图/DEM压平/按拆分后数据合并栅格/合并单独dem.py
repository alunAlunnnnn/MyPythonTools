import arcpy
import os


def getAllSingleRaster(rasDir):
    mergeRasList = []

    for root, dirs, files in os.walk(rasDir):
        # get all raster files
        if files:
            # get all
            singleMergeRasList = [os.path.join(root, eachFiles) for eachFiles in files
                                  if "min_" in eachFiles and "aux.xml" not in eachFiles and ".rrd" not in eachFiles]
            mergeRasList += singleMergeRasList

    return mergeRasList

#
def mosicAllRaster(mergeRasList, outputPath, outputName):
    mergeRasLyrList = [arcpy.Raster(each) for each in mergeRasList]

    arcpy.MosaicToNewRaster_management(mergeRasLyrList, outputPath, outputName, pixel_type="32_BIT_FLOAT",
                                       number_of_bands=1)

    return os.path.join(outputPath, outputName)


def main(rasDir, outputPath, outputName):
    # get all single raster list
    mergeRasList = getAllSingleRaster(rasDir)

    # copy all rasters to a same directory


    # mosic to new raster
    mosaicedRas = mosicAllRaster(mergeRasList, outputPath, outputName)




rasDir = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_分块运算结果存放"
outputPath = r"F:\工作项目\项目_温州超图\研发_DEM挖坑\数据_DEM处理_温州市\数据_临时合并"
outputName = "mosaiced.img"

main(rasDir, outputPath, outputName)

