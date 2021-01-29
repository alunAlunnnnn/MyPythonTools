import numpy
import arcpy
import os

arcpy.env.overwriteOutput = True

def addUnicField(inputFC, unicField):
    # add unic field
    try:
        arcpy.AddField_management(inputFC, unicField, "SHORT")
    except:
        arcpy.DeleteField_management(inputFC, unicField)
        arcpy.AddField_management(inputFC, unicField, "SHORT")

    # give unic value to unic field
    codes = """i = 0
def calUnicField():
    global i
    i += 1
    return i """
    arcpy.CalculateField_management(inputFC, unicField, "calUnicField()", "PYTHON3", codes)

    return inputFC


def addColorField(inputFC):
    # add unic field
    try:
        arcpy.AddField_management(inputFC, "COLOR", "SHORT")
    except:
        arcpy.DeleteField_management(inputFC, "COLOR")
        arcpy.AddField_management(inputFC, "COLOR", "SHORT")

    return inputFC


def getNearFeature(inputFC, unicField, nearField, outputPath, outputName):
    # add unic field
    try:
        arcpy.AddField_management(inputFC, nearField, "TEXT")
    except:
        arcpy.DeleteField_management(inputFC, nearField)
        arcpy.AddField_management(inputFC, nearField, "TEXT")

    # copy a temp data
    tempData = arcpy.CopyFeatures_management(inputFC, os.path.join(outputPath, "temp"))

    # generate a field mapping
    mps = arcpy.FieldMappings()

    mp1 = arcpy.FieldMap()
    mp1.addInputField(inputFC, unicField)
    mp1.addInputField(tempData, unicField)
    mp1.mergeRule = "Join"
    mp1.joinDelimiter = ","
    mp1.outputField = arcpy.ListFields(inputFC, nearField)[0]

    mps.addFieldMap(mp1)

    print(mps.exportToString())
    # get all near data to each feature
    arcpy.SpatialJoin_analysis(inputFC, tempData, os.path.join(outputPath, outputName),
                               "JOIN_ONE_TO_ONE", field_mapping=mps, match_option="INTERSECT")

    return os.path.join(outputPath, outputName)


def main(inputFC, unicField, nearField, outputPath, outputName):

    addUnicField(inputFC, unicField)

    getNearFeature(inputFC, unicField, nearField, outputPath, outputName)

    addColorField(inputFC)


inputFC = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\Algorithm\回溯算法_四色填充\datas\process\china.shp"
unicField = "unic_field"
nearField = "near_field"
outputPath = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\Algorithm\回溯算法_四色填充\datas\output"
outputName = "china"

main(inputFC, unicField, nearField, outputPath, outputName)