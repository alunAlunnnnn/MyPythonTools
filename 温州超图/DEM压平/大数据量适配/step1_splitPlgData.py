import arcpy
import os

arcpy.env.overwriteOutput = True


def getFCOIDName(inFC):
    oIDField = [each.name for each in arcpy.ListFields(inFC) if each.type == "OID"][0]
    return oIDField


# get name and value list of input featureclass
def getFCOIDValue(inFC):
    oIDName = getFCOIDName(inFC)
    oIDValueList = []
    with arcpy.da.SearchCursor(inFC, [oIDName]) as cur:
        for row in cur:
            oIDValueList.append(row[0])
        del row

    return oIDName, oIDValueList


# split input featureclass to multi shape file
def splitData(inputData, splitNum, outputPath, outputName):
    # only accept int number
    if isinstance(splitNum, int):
        splitNum = int(splitNum)

    # get objectid name and all objectid values
    OIDName, OIDValueList = getFCOIDValue(inputData)

    # get min and max value
    minValue, maxValue = min(OIDValueList), max(OIDValueList)
    stepTotal, step = (maxValue - minValue), (maxValue - minValue) / splitNum

    # split data
    for i in range(1, splitNum + 1):
        if i == 1:
            selectSQL = f"{OIDName} < {minValue + step * i}"
        elif i == splitNum:
            selectSQL = f"{OIDName} >= {minValue + step * (i - 1)}"
        else:
            selectSQL = f"{OIDName} >= {minValue + step * (i - 1)} and {OIDName} < {minValue + step * i}"

        print(selectSQL)

        #
        arcpy.Select_analysis(inputData, os.path.join(outputPath, f"{outputName}_{i}"), selectSQL)


inputData = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\输入数据\plg_modified_cgcs2000_all_buffer_30m_single.shp"
splitNum = 6
outputPath = r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\数据拆分_30米\data"
outputName = "split"

splitData(inputData, splitNum, outputPath, outputName)










