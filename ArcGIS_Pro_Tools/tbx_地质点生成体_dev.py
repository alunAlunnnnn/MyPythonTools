import arcpy, os

arcpy.env.overwriteOutput = True


class DataGenerateFailed(Exception):
    pass


def generatePntDomain(pntFC, outputPath, outputName):
    arcpy.MinimumBoundingGeometry_management(pntFC, os.path.join(outputPath, outputName + '_dom'), 'CONVEX_HULL')
    return os.path.join(outputPath, outputName)


# add x,y,z field
def addField(inFC, fieldName, fieldType):
    fieldType = fieldType.upper()
    if fieldType == 'STRING':
        fieldType = 'TEXT'

    try:
        arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType)


# add messages
def addMessage(mes):
    print(mes)
    arcpy.AddMessage(mes)


# add error
def addError(mes):
    print(mes)
    arcpy.AddError(mes)


# add warning
def addWarning(mes):
    print(mes)
    arcpy.AddWarning(mes)


def reapirePntGeo(pntFC):
    pass


def generateTin(pntFC):
    pass


def testDataExist(inFC):
    if arcpy.Exists(inFC):
        addMessage('Success --- data %s has been generated' % inFC)
    else:
        addError('Error --- data %s generate failed' % inFC)
        raise DataGenerateFailed


# Add data to pro project
def _AddDataTOArcGISPro(inFea):
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    sceneMap = [each for each in aprx.listMaps() if each.mapType == 'SCENE'][0]

    # add data to current aprx
    outlyr = sceneMap.addDataFromPath(inFea)
    return outlyr



def generateCylinder(pntFC, xField, yField, zField, bufDis, outputPath, outputName):
    # make sure data can be created
    tempData = arcpy.CreateUniqueName('buffer_pnt', outputPath)
    sortPlgData = arcpy.CreateUniqueName('buffer_sort', outputPath)
    sortPlgDataZ = arcpy.CreateUniqueName('buffer_sort_z', outputPath)
    tempDataList = [tempData, sortPlgData, sortPlgDataZ]

    bufDis = str(bufDis) + " Meters"
    bufRes = arcpy.Buffer_analysis(pntFC, tempData, bufDis)

    # test whether the data has generated successfully
    testDataExist(tempData)

    sortedData = arcpy.Sort_management(bufRes, sortPlgData, [[xField, 'ASCENDING'], [yField, 'ASCENDING'], [zField, 'DESCENDING']])

    # test whether the data has generated successfully
    testDataExist(sortPlgData)

    addField(sortedData, 'h_temp', 'DOUBLE')
    codes = '''set1 = set()
lastHeight = 0
def f(x, y, z):
    global set1
    global lastHeight
    x = float(x)
    y = float(y)
    z = float(z)
    coord = (x, y)
    if coord in set1:
        height = lastHeight - z
    else:
        set1.add(coord)
        height = 0 - z
    lastHeight = z
    return height'''
    arcpy.CalculateField_management(sortedData, 'h_temp', 'f(!%s!, !%s!, !%s!)' % (xField, yField, zField), 'PYTHON3', codes)

    # convert data to 3d with z
    arcpy.FeatureTo3DByAttribute_3d(sortedData, sortPlgDataZ, zField)

    # add data to aprx adn extrusion
    outlyr = _AddDataTOArcGISPro(sortPlgDataZ)
    outlyr.extrusion('BASE_HEIGHT', '$feature.h_temp')

    # convert to multipatch
    resMul = arcpy.CreateUniqueName(outputName, outputPath)
    arcpy.Layer3DToFeatureClass_3d(outlyr, resMul)

    # apply symbol
    outCutFillLyr = _AddDataTOArcGISPro(resMul)

    # merge multipatch with level field



    if delTempSwitch == 'true':
        for each in tempDataList:
            try:
                arcpy.Delete_management(each)
            except:
                addWarning('Warring --- can not delete feature class %s' % each)


# delTempSwitch = 'false'
# pntFC = r'E:\地质点\钻孔数据\pro_process\拉伸结果\res_temp.gdb\pnt_repaire'
# xField = 'x_pnt'
# yField = 'y_pnt'
# zField = 'z_tab'
# bufDis = '5'
# outputPath = r'E:\地质点\钻孔数据\aprx\地质体生成\test_0702.gdb'
# outputName = 'kaer'


pntFC = arcpy.GetParameterAsText(0)
xField = arcpy.GetParameterAsText(1)
yField = arcpy.GetParameterAsText(2)
zField = arcpy.GetParameterAsText(3)
bufDis = arcpy.GetParameterAsText(4)
outputPath = arcpy.GetParameterAsText(5)
outputName = arcpy.GetParameterAsText(6)
delTempSwitch = arcpy.GetParameterAsText(7)

generateCylinder(pntFC, xField, yField, zField, bufDis, outputPath, outputName)

