import os

"""
usage:
    generate batch process file (.bat) and start multi-processer to run py scripts at the same time
"""


def getAllBufferShp(shpDir, shpName):
    dataList = [os.path.join(shpDir, each) for each in os.listdir(shpDir) if each[-4:] == ".shp" and shpName in each]
    print(dataList)
    return dataList


def generateBatchFile(outputPath, pyProcesser, shpDataList, inRas, outRasPath):
    batchFileList = []

    # create batch process dir
    batchDir = os.path.join(outputPath, "batFile")
    if not os.path.exists(batchDir):
        os.makedirs(batchDir)

    for eachShp in shpDataList:

        # create output raster dir
        oRasPath = os.path.join(outRasPath, os.path.splitext(os.path.split(eachShp)[1])[0])
        if not os.path.exists(oRasPath):
            os.makedirs(oRasPath)

        # write batch process file
        batFile = os.path.join(batchDir, os.path.splitext(os.path.split(eachShp)[1])[0] + ".bat")
        batchFileList.append(batFile)
        with open(batFile, "w", encoding="gb2312") as f:
            f.write("@echo\n")
            f.write(f"python {pyProcesser} {inRas} {eachShp} {oRasPath} test.img \n")
            f.write("pause")

    # create main batch process file
    with open(os.path.join(batchDir, "main.bat"), "w", encoding="gb2312") as f:
        f.write("@echo\n")

        for eachBatFile in batchFileList:
            f.write(f"start {eachBatFile} \n")

        f.write("pause")


pyProcesser = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\温州超图\DEM挖坑\大数据量适配\step2_getDEMValueInAllPlg.py"
inputRaster = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\DEM\DEM30.img"
outputPath = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\数据拆分_30米\bat"
outputName = "多进程处理"
shpDir = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\数据拆分_30米\data"
shpName = "split"
outRasPath = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\数据拆分_30米\processing_raster"

# get all splited shp file
shpDataList = getAllBufferShp(shpDir, shpName)

# generate all process
generateBatchFile(outputPath, pyProcesser, shpDataList, inputRaster, outRasPath)
