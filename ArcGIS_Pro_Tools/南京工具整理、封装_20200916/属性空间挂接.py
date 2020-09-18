import sys
import os
import logging
import datetime

# get arcgis pro toolbox directory
tbxDir = os.path.dirname(sys.argv[0])

# create log directory
logDir = os.path.join(tbxDir, "tbx_log")
try:
    if not os.path.exists(logDir):
        os.makedirs(logDir)
except:
    pass

# make sure this script have rights to create file here
createFileRights = False
fileRightTest = os.path.join(logDir, "t_t_.txt")
logFile = os.path.join(logDir, "tool2_sxkjlj_log.txt")
try:
    with open(fileRightTest, "w", encoding="utf-8") as f:
        f.write("create file rights test")
    createFileRights = True
except:
    createFileRights = False

# init log set config
if createFileRights:
    logging.basicConfig(filename=logFile, filemode="w", level=logging.DEBUG,
                        format="\n\n *** \n %(asctime)s    %(levelname)s ==== %(message)s \n *** \n\n")
else:
    logging.basicConfig(level=logging.DEBUG,
                        format="\n\n *** \n %(asctime)s    %(levelname)s ==== %(message)s \n *** \n\n")

try:
    import arcpy
    import functools
    import inspect

    logging.debug("Module import success")
except BaseException as e:
    logging.error(str(e))

arcpy.env.overwriteOutput = True


# can not get schema lock error
class GetSchemaLockFaild(Exception):
    pass


# fieldType is not valid
class FieldTypeNotValid(Exception):
    pass


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


# write function name and params into log file
def logIt(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        logging.info(f" ======================== Start Function {func.__name__} ========================")
        parameters = [each.strip() for each in str(inspect.signature(func))[1:-1].split(",")]
        keyPara = kwargs
        for eachKey in keyPara:
            eachKey = eachKey.strip()
            if eachKey in parameters:
                parameters.remove(eachKey)

        mes = ""
        for i, eachPara in enumerate(parameters):
            mes += f"\n {eachPara}: {args[i]} "

        for eachKey, eachValue in keyPara.items():
            mes += f"\n {eachKey}: {eachValue} "

        logging.debug(mes)
        res = func(*args, **kwargs)

        return res

    return _wrapper


# decorater --- set temp workspace
def setTempWorkspace(workspace):
    def _inner(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # keep origin workspace
            oriWS = None
            if arcpy.env.workspace:
                oriWS = arcpy.env.workspace

            arcpy.env.workspace = workspace
            res = func(*args, **kwargs)

            try:
                if oriWS:
                    arcpy.env.workspace = oriWS
                else:
                    arcpy.ClearEnvironment("workspace")
            except:
                pass
            return res

        return _wrapper

    return _inner


# auto create a available name for feature classes
def availableDataName(outputPath: str, outputName: str) -> str:
    @setTempWorkspace(outputPath)
    def _wrapper(outputPath: str, outputName: str) -> str:
        folderType = arcpy.Describe(outputPath).dataType
        if folderType == "Workspace":
            if outputName[-4:] == ".shp":
                outputName = outputName[:-4]
        # .sde like directory
        elif folderType == "File":
            if outputName[-4:] == ".shp":
                outputName = outputName[:-4]
        else:
            if not outputName[-4:] == ".shp":
                outputName = outputName + ".shp"

        return os.path.join(outputPath, outputName)

    res = _wrapper(outputPath, outputName)
    return res


@logIt
# add x,y,z field
def addField(inFC, fieldName, fieldType):
    fieldType = fieldType.upper()
    if fieldType.lower() == 'string':
        fieldType = 'TEXT'

    try:
        arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType)


# add feature class layer to opening aprx file.
# Input featureclass , lyr name and the parameter index of output lyr in tbx
@logIt
def addDataToPro(inFC, outputName, paraIndex):
    if outputName[-4:] == ".shp":
        outputName = outputName[:-4]
    outLyr = arcpy.MakeFeatureLayer_management(inFC, outputName)
    arcpy.SetParameter(paraIndex, outLyr)


@logIt
# get all attributes from feature class
def getAttrFromFC(inFC):
    global fieldList, fieldTypeList

    # add x, y, z coord to feature class
    coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f',
                      'y_temp_f', 'x_temp_l', 'y_temp_l']

    fieldExpList = ['!shape.centroid.X!', '!shape.centroid.Y!', '!shape.centroid.Z!',
                    '!shape.firstPoint.X!', '!shape.firstPoint.Y!', '!shape.firstPoint.X!',
                    '!shape.firstPoint.Y!']

    for i, eachField in enumerate(coordFieldList):
        addField(inFC, eachField, 'DOUBLE')
        arcpy.CalculateField_management(inFC, eachField, fieldExpList[i], 'PYTHON3')
        logging.debug('Success --- the fature "%s" add fields %s success' % (inFC, eachField))
        addMessage('Success --- the fature "%s" add fields %s success' % (inFC, eachField))

    # get all fields
    fieldList = [each.name for each in arcpy.ListFields(inFC)
                 if each.type != "OID" and each.type != "Geometry"
                 and each.name != "Shape_Length" and each.name != "Shape_Area"]

    fieldTypeList = [each.type for each in arcpy.ListFields(inFC)
                     if each.type != "OID" and each.type != "Geometry"
                     and each.name != "Shape_Length" and each.name != "Shape_Area"]

    logging.debug('Success --- the fature "%s" get fields list success' % inFC)
    addMessage('Success --- the fature "%s" get fields list success' % inFC)

    # save all value from feature class
    resDict = {}
    rowNum = 0
    with arcpy.da.SearchCursor(inFC, fieldList) as cur:
        for row in cur:
            eachRow = {}
            # get the result of each row
            for i, each in enumerate(fieldList):
                eachRow[each] = row[i]

            resDict[rowNum] = eachRow
            rowNum += 1

    logging.debug('Success --- the fature "%s" get fields value success ( total %s rows)' % (inFC, rowNum))
    addMessage('Success --- the fature "%s" get fields value success ( total %s rows)' % (inFC, rowNum))

    # delete temp field
    if delTempField == 'true':
        addMessage('Deleting --- temp field delete key is open, now start to delete temp field')

        coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f',
                          'y_temp_f', 'x_temp_l', 'y_temp_l']
        for eachField in coordFieldList:
            try:
                arcpy.DeleteField_management(inFC, eachField)
                logging.debug('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
                addMessage('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
            except:
                logging.debug('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))
                addWarning('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))

    return resDict


# save fields value to target feature
@logIt
def saveFieldsValue(targetFC, valueDict, tolerance):
    global fieldList, fieldTypeList

    # add x, y, z coord to targetFC
    removeList = ['OBJECTID', 'FID', 'Shape_Length', 'Shape_Area']
    for eachField in removeList:
        if eachField in fieldList:
            fieldTypeList.pop(fieldList.index(eachField))
            fieldList.remove(eachField)

    logging.debug('fieldList is : %s ' % fieldList)
    logging.debug('fieldTypeList is : %s ' % fieldTypeList)
    addMessage(fieldList)
    # todo 正在做： 1、简化代码   2、添加日志功能
    addMessage(fieldTypeList)
    for i, eachField in enumerate(fieldList):
        addField(targetFC, eachField, fieldTypeList[i])
        addMessage('Success --- the fature "%s" add fields %s success' % (targetFC, eachField))

    # calculate x, y, z coord
    arcpy.CalculateField_management(targetFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
    arcpy.CalculateField_management(targetFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')
    arcpy.CalculateField_management(targetFC, 'z_temp_c', '!shape.centroid.Z!', 'PYTHON3')

    # calculate first point
    arcpy.CalculateField_management(targetFC, 'x_temp_f', '!shape.firstPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(targetFC, 'y_temp_f', '!shape.firstPoint.Y!', 'PYTHON3')
    # arcpy.CalculateField_management(targetFC, 'z_temp_f', '!shape.firstPoint.Z!', 'PYTHON3')

    # calculate last point
    arcpy.CalculateField_management(targetFC, 'x_temp_l', '!shape.firstPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(targetFC, 'y_temp_l', '!shape.firstPoint.Y!', 'PYTHON3')
    # arcpy.CalculateField_management(targetFC, 'z_temp_l', '!shape.firstPoint.Z!', 'PYTHON3')

    # addMessage('Success --- the fature "%s" calculate fields x_temp, y_temp, z_temp success' % targetFC)

    tolerance = float(tolerance)
    with arcpy.da.UpdateCursor(targetFC, fieldList) as cur:
        for i, row in enumerate(cur):
            x_c = float(row[-9])
            y_c = float(row[-8])
            z_c = float(row[-7])
            x_f = float(row[-6])
            y_f = float(row[-5])
            # z_f = float(row[-4])
            x_l = float(row[-3])
            y_l = float(row[-2])
            # z_l = float(row[-1])

            x_c_selStart = x_c - tolerance
            x_c_selEnd = x_c + tolerance
            y_c_selStart = y_c - tolerance
            y_c_selEnd = y_c + tolerance
            z_c_selStart = z_c - tolerance
            z_c_selEnd = z_c + tolerance

            x_f_selStart = x_f - tolerance
            x_f_selEnd = x_f + tolerance
            y_f_selStart = y_f - tolerance
            y_f_selEnd = y_f + tolerance
            # z_f_selStart = z_f - tolerance
            # z_f_selEnd = z_f + tolerance

            x_l_selStart = x_l - tolerance
            x_l_selEnd = x_l + tolerance
            y_l_selStart = y_l - tolerance
            y_l_selEnd = y_l + tolerance
            # z_l_selStart = z_l - tolerance
            # z_l_selEnd = z_l + tolerance
            # addMessage('Comparing --- now is comparing the coord between origin feature class and target feature class, centroid point x coord section is [ %s, %s ], y coord section is [ %s, %s ], z coord section is [ %s, %s ]' % (x_c_selStart, x_c_selEnd, y_c_selStart, y_c_selEnd, z_c_selStart, z_c_selEnd))
            for eachKey, eachValue in valueDict.items():
                ori_x_c = float(eachValue['x_temp_c'])
                ori_y_c = float(eachValue['y_temp_c'])
                ori_z_c = float(eachValue['z_temp_c'])

                ori_x_f = float(eachValue['x_temp_f'])
                ori_y_f = float(eachValue['y_temp_f'])
                # ori_z_f = float(eachValue['z_temp_f'])

                ori_x_l = float(eachValue['x_temp_l'])
                ori_y_l = float(eachValue['y_temp_l'])
                # ori_z_l = float(eachValue['z_temp_l'])
                # if durePolyline == 'false':
                #     if ori_x_f >= x_f_selStart and ori_x_f <= x_f_selEnd:
                #         if ori_y_f >= y_f_selStart and ori_y_f <= y_f_selEnd:
                #             if ori_z_f >= z_f_selStart and ori_z_f <= z_f_selEnd:
                #                 if ori_x_l >= x_l_selStart and ori_x_l <= x_l_selEnd:
                #                     if ori_y_l >= y_l_selStart and ori_y_l <= y_l_selEnd:
                #                         if ori_z_l >= z_l_selStart and ori_z_l <= z_l_selEnd:
                #                             if ori_x_c >= x_c_selStart and ori_x_c <= x_c_selEnd:
                #                                 if ori_y_c >= y_c_selStart and ori_y_c <= y_c_selEnd:
                #                                     if ori_z_c >= z_c_selStart and ori_z_c <= z_c_selEnd:
                #                                         addMessage('Coord Match Success')
                #                                         for m in range(len(fieldList) - 9):
                #                                             row[m] = eachValue[fieldList[m]]
                #                                         break
                # else:
                #     if ori_x_f >= x_f_selStart and ori_x_f <= x_f_selEnd:
                #         if ori_y_f >= y_f_selStart and ori_y_f <= y_f_selEnd:
                #             if ori_z_f >= z_f_selStart and ori_z_f <= z_f_selEnd:
                #                 if ori_x_l >= x_l_selStart and ori_x_l <= x_l_selEnd:
                #                     if ori_y_l >= y_l_selStart and ori_y_l <= y_l_selEnd:
                #                         if ori_z_l >= z_l_selStart and ori_z_l <= z_l_selEnd:
                #                             addMessage('Coord Match Success')
                #                             for m in range(len(fieldList) - 9):
                #                                 row[m] = eachValue[fieldList[m]]
                #                             break
                if durePolyline == 'false':
                    if ori_x_f >= x_f_selStart and ori_x_f <= x_f_selEnd:
                        if ori_y_f >= y_f_selStart and ori_y_f <= y_f_selEnd:
                            if ori_x_l >= x_l_selStart and ori_x_l <= x_l_selEnd:
                                if ori_y_l >= y_l_selStart and ori_y_l <= y_l_selEnd:
                                    if ori_x_c >= x_c_selStart and ori_x_c <= x_c_selEnd:
                                        if ori_y_c >= y_c_selStart and ori_y_c <= y_c_selEnd:
                                            if ori_z_c >= z_c_selStart and ori_z_c <= z_c_selEnd:
                                                addMessage('Coord Match Success')
                                                for m in range(len(fieldList) - 9):
                                                    row[m] = eachValue[fieldList[m]]
                                                break
                else:
                    if ori_x_f >= x_f_selStart and ori_x_f <= x_f_selEnd:
                        if ori_y_f >= y_f_selStart and ori_y_f <= y_f_selEnd:
                            if ori_x_l >= x_l_selStart and ori_x_l <= x_l_selEnd:
                                if ori_y_l >= y_l_selStart and ori_y_l <= y_l_selEnd:
                                    addMessage('Coord Match Success')
                                    for m in range(len(fieldList) - 9):
                                        row[m] = eachValue[fieldList[m]]
                                    break
            cur.updateRow(row)

    # delete temp field
    if delTempField == 'true':
        addMessage('Deleting --- temp field delete key is open, now start to delete temp field')

        coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f',
                          'y_temp_f', 'z_temp_f', 'x_temp_l', 'y_temp_l', 'z_temp_l']
        for eachField in coordFieldList:
            try:
                arcpy.DeleteField_management(targetFC, eachField)
                addMessage('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
            except:
                addWarning('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))


# main process
def Main(inFC, targetFC, tolerance):
    valueDict = getAttrFromFC(inFC)
    addMessage(valueDict)

    saveFieldsValue(targetFC, valueDict, tolerance)


fieldList = []
fieldTypeList = []

# # 'true' or 'false', delete temp field or not
# delTempField = 'false'
# inFC = r'D:\b\test.gdb\line'
# targetFC = r'D:\b\test.gdb\line_m_r'
# tolerance = '10'
#
# # 'true' or 'false', compare centroid point or not
# durePolyline = 'false'

inFC = arcpy.GetParameterAsText(0)
targetFC = arcpy.GetParameterAsText(1)
tolerance = arcpy.GetParameterAsText(2)
delTempField = arcpy.GetParameterAsText(3)
durePolyline = arcpy.GetParameterAsText(4)

Main(inFC, targetFC, tolerance)
