import arcpy

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


# add x,y,z field
def addField(inFC, fieldName, fieldType):
    fieldType = fieldType.upper()
    if fieldType.lower() == 'string':
        fieldType = 'TEXT'

    # make sure the field will be add is a valid field type
    # fieldTypeList = ['TEXT', 'FLOAT', 'DOUBLE', 'SHORT', 'LONG', 'DATE', 'BLOB', 'RASTER', 'GUID']
    # if fieldType not in fieldTypeList:
    #     addError('Error --- the field type is not valid, in add field %s to %s' % (fieldName, inFC))
    #     raise FieldTypeNotValid

    # test whether can get schema lock from current feature class
    # if arcpy.TestSchemaLock(inFC):
    try:
        arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFC, fieldName)
        arcpy.AddField_management(inFC, fieldName, fieldType)
    # else:
    #     addError('Error --- can not get schema lock from %s' % inFC)
    #     raise GetSchemaLockFaild


# get all attributes from feature class
def getAttrFromFC(inFC):
    global fieldList, fieldTypeList

    # add x, y, z coord to feature class
    # coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f', 'y_temp_f', 'z_temp_f', 'x_temp_l', 'y_temp_l', 'z_temp_l']
    coordFieldList = ['x_temp_c', 'y_temp_c']
    for eachField in coordFieldList:
        addField(inFC, eachField, 'DOUBLE')
        addMessage('Success --- the fature "%s" add fields %s success' % (inFC, eachField))

    # calculate centroid point
    arcpy.CalculateField_management(inFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')


    addMessage('Success --- the fature "%s" calculate fields x_temp, y_temp, z_temp success' % inFC)

    # get all fields
    fieldList = [eachField.name for eachField in arcpy.ListFields(inFC) if eachField.name.lower() != 'shape' and eachField.type != 'OID' and eachField.type != 'Geometry']
    fieldTypeList = [eachField.type for eachField in arcpy.ListFields(inFC) if eachField.name.lower() != 'shape' and eachField.type != 'OID' and eachField.type != 'Geometry']

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

    addMessage('Success --- the fature "%s" get fields value success ( total %s rows)' % (inFC, rowNum))

    # delete temp field
    if delTempField == 'true':
        addMessage('Deleting --- temp field delete key is open, now start to delete temp field')

        coordFieldList = ['x_temp_c', 'y_temp_c']
        for eachField in coordFieldList:
            try:
                arcpy.DeleteField_management(inFC, eachField)
                addMessage('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
            except:
                addWarning('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))

    return resDict


# save fields value to target feature
def saveFieldsValue(targetFC, valueDict, tolerance):
    global fieldList, fieldTypeList

    # add x, y, z coord to targetFC
    try:
        try:
            index = fieldList.index('OBJECTID')
        except:
            pass
        fieldList.remove('OBJECTID')
        fieldTypeList.pop(index)
    except:
        pass

    try:
        try:
            index = fieldList.index('FID')
        except:
            pass
        fieldList.remove('FID')
        fieldTypeList.pop(index)
    except:
        pass

    try:
        try:
            index = fieldList.index('Shape_Length')
        except:
            pass
        fieldList.remove('Shape_Length')
        fieldTypeList.pop(index)
    except:
        pass

    try:
        try:
            index = fieldList.index('Shape_Area')
        except:
            pass
        fieldList.remove('Shape_Area')
        fieldTypeList.pop(index)
    except:
        pass

    maxNum = int(arcpy.GetCount_management(targetFC)[0]) + len(fieldList)
    arcpy.SetProgressor('step', 'running', 0, maxNum)
    addMessage(fieldList)
    addMessage(fieldTypeList)
    for i, eachField in enumerate(fieldList):
        addField(targetFC, eachField, fieldTypeList[i])
        addMessage('Success --- the fature "%s" add fields %s success' % (targetFC, eachField))
        arcpy.SetProgressorPosition()
    # calculate x, y, z coord
    arcpy.CalculateField_management(targetFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
    arcpy.CalculateField_management(targetFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')

    tolerance = float(tolerance)

    with arcpy.da.UpdateCursor(targetFC, fieldList) as cur:
        for i, row in enumerate(cur):
            arcpy.SetProgressorPosition()
            x_c = float(row[-2])
            y_c = float(row[-1])

            x_c_selStart = x_c - tolerance
            x_c_selEnd = x_c + tolerance
            y_c_selStart = y_c - tolerance
            y_c_selEnd = y_c + tolerance

            for eachKey, eachValue in valueDict.items():
                ori_x_c = float(eachValue['x_temp_c'])
                ori_y_c = float(eachValue['y_temp_c'])

                if durePolyline == 'false':
                    if ori_x_c >= x_c_selStart and ori_x_c <= x_c_selEnd:
                        if ori_y_c >= y_c_selStart and ori_y_c <= y_c_selEnd:
                            # addMessage('Coord Match Success')
                            for m in range(len(fieldList) - 2):
                                row[m] = eachValue[fieldList[m]]
                                # addWarning(fieldList[m])
                                cur.updateRow(row)
                            valueDict.pop(eachKey)
                            break
                else:
                    if ori_x_c >= x_c_selStart and ori_x_c <= x_c_selEnd:
                        if ori_y_c >= y_c_selStart and ori_y_c <= y_c_selEnd:
                            # addMessage('Coord Match Success')
                            for m in range(len(fieldList) - 2):
                                row[m] = eachValue[fieldList[m]]
                                cur.updateRow(row)
                            valueDict.pop(eachKey)
                            break
            # cur.updateRow(row)

    # delete temp field
    if delTempField == 'true':
        addMessage('Deleting --- temp field delete key is open, now start to delete temp field')

        coordFieldList = ['x_temp_c', 'y_temp_c']
        for eachField in coordFieldList:
            try:
                arcpy.DeleteField_management(targetFC, eachField)
                addMessage('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
            except:
                addWarning('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))


# main process
def Main(inFC, targetFC, tolerance):
    valueDict = getAttrFromFC(inFC)
    # addMessage(valueDict)

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

# inFC = arcpy.GetParameterAsText(0)
# targetFC = arcpy.GetParameterAsText(1)
# tolerance = arcpy.GetParameterAsText(2)
# delTempField = arcpy.GetParameterAsText(3)
# durePolyline = arcpy.GetParameterAsText(4)

inFC = arcpy.GetParameterAsText(0)
targetFC = arcpy.GetParameterAsText(1)
tolerance = arcpy.GetParameterAsText(2)
delTempField = arcpy.GetParameterAsText(3)
durePolyline = arcpy.GetParameterAsText(4)

Main(inFC, targetFC, tolerance)