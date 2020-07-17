import arcpy, datetime, functools
import pandas as pd

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


# get process time
def getRunTime(func):
    @functools.wraps
    def _getRunTime(func):
        pass

    return _getRunTime



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


# get all attributes from feature class
def getAttrFromFC(inFC):
    global fieldList, fieldTypeList

    # add x, y, z coord to feature class
    coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f', 'y_temp_f', 'z_temp_f', 'x_temp_l', 'y_temp_l', 'z_temp_l']
    for eachField in coordFieldList:
        addField(inFC, eachField, 'DOUBLE')
        addMessage('Success --- the fature "%s" add fields %s success' % (inFC, eachField))

    # calculate centroid point
    arcpy.CalculateField_management(inFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'z_temp_c', '!shape.centroid.Z!', 'PYTHON3')

    # calculate first point
    arcpy.CalculateField_management(inFC, 'x_temp_f', '!shape.firstPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_f', '!shape.firstPoint.Y!', 'PYTHON3')
    # arcpy.CalculateField_management(inFC, 'z_temp_f', '!shape.firstPoint.Z!', 'PYTHON3')

    # calculate last point
    arcpy.CalculateField_management(inFC, 'x_temp_l', '!shape.firstPoint.X!', 'PYTHON3')
    arcpy.CalculateField_management(inFC, 'y_temp_l', '!shape.firstPoint.Y!', 'PYTHON3')
    # arcpy.CalculateField_management(inFC, 'z_temp_l', '!shape.firstPoint.Z!', 'PYTHON3')

    addMessage('Success --- the fature "%s" calculate fields x_temp, y_temp, z_temp success' % inFC)

    # get all fields
    fieldList = [eachField.name for eachField in arcpy.ListFields(inFC) if eachField.name.lower() != 'shape' and eachField.type != 'OID' and eachField.type != 'Geometry']

    fieldTypeList = [eachField.type for eachField in arcpy.ListFields(inFC) if eachField.name.lower() != 'shape' and eachField.type != 'OID' and eachField.type != 'Geometry']

    addMessage('Success --- the fature "%s" get fields list success' % inFC)

    table = arcpy.TableToExcel_conversion(inFC, 'D:/test/tempexcel.xls')

    df = pd.read_excel('D:/test/tempexcel.xls')


    # # save all value from feature class
    # resDict = {}
    # rowNum = 0
    # with arcpy.da.SearchCursor(inFC, fieldList) as cur:
    #     for row in cur:
    #         eachRow = {}
    #         # get the result of each row
    #         for i, each in enumerate(fieldList):
    #             eachRow[each] = row[i]
    #
    #         resDict[rowNum] = eachRow
    #         rowNum += 1
    #
    # addMessage('Success --- the fature "%s" get fields value success ( total %s rows)' % (inFC, rowNum))
    #
    # # delete temp field
    # if delTempField == 'true':
    #     addMessage('Deleting --- temp field delete key is open, now start to delete temp field')
    #
    #     coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f', 'y_temp_f', 'z_temp_f', 'x_temp_l',
    #                       'y_temp_l', 'z_temp_l']
    #     for eachField in coordFieldList:
    #         try:
    #             arcpy.DeleteField_management(inFC, eachField)
    #             addMessage('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
    #         except:
    #             addWarning('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))
    #
    # return resDict
#
#
# def saveFieldsValue(targetFC, valueDict, tolerance):
#     global fieldList, fieldTypeList
#
#     # add x, y, z coord to targetFC
#     try:
#         try:
#             index = fieldList.index('OBJECTID')
#         except:
#             pass
#         fieldList.remove('OBJECTID')
#         fieldTypeList.pop(index)
#     except:
#         pass
#
#     try:
#         try:
#             index = fieldList.index('FID')
#         except:
#             pass
#         fieldList.remove('FID')
#         fieldTypeList.pop(index)
#     except:
#         pass
#
#     try:
#         try:
#             index = fieldList.index('Shape_Length')
#         except:
#             pass
#         fieldList.remove('Shape_Length')
#         fieldTypeList.pop(index)
#     except:
#         pass
#
#     try:
#         try:
#             index = fieldList.index('Shape_Area')
#         except:
#             pass
#         fieldList.remove('Shape_Area')
#         fieldTypeList.pop(index)
#     except:
#         pass
#
#
#     addMessage(fieldList)
#     addMessage(fieldTypeList)
#     for i, eachField in enumerate(fieldList):
#         addField(targetFC, eachField, fieldTypeList[i])
#         addMessage('Success --- the fature "%s" add fields %s success' % (targetFC, eachField))
#
#     # calculate x, y, z coord
#     arcpy.CalculateField_management(targetFC, 'x_temp_c', '!shape.centroid.X!', 'PYTHON3')
#     arcpy.CalculateField_management(targetFC, 'y_temp_c', '!shape.centroid.Y!', 'PYTHON3')
#     arcpy.CalculateField_management(targetFC, 'z_temp_c', '!shape.centroid.Z!', 'PYTHON3')
#
#     # calculate first point
#     arcpy.CalculateField_management(targetFC, 'x_temp_f', '!shape.firstPoint.X!', 'PYTHON3')
#     arcpy.CalculateField_management(targetFC, 'y_temp_f', '!shape.firstPoint.Y!', 'PYTHON3')
#     # arcpy.CalculateField_management(targetFC, 'z_temp_f', '!shape.firstPoint.Z!', 'PYTHON3')
#
#     # calculate last point
#     arcpy.CalculateField_management(targetFC, 'x_temp_l', '!shape.firstPoint.X!', 'PYTHON3')
#     arcpy.CalculateField_management(targetFC, 'y_temp_l', '!shape.firstPoint.Y!', 'PYTHON3')
#     # arcpy.CalculateField_management(targetFC, 'z_temp_l', '!shape.firstPoint.Z!', 'PYTHON3')
#
#     # addMessage('Success --- the fature "%s" calculate fields x_temp, y_temp, z_temp success' % targetFC)
#
#     tolerance = float(tolerance)
#     with arcpy.da.UpdateCursor(targetFC, fieldList) as cur:
#         for i, row in enumerate(cur):
#             x_c = float(row[-9])
#             y_c = float(row[-8])
#             z_c = float(row[-7])
#             x_f = float(row[-6])
#             y_f = float(row[-5])
#             # z_f = float(row[-4])
#             x_l = float(row[-3])
#             y_l = float(row[-2])
#             # z_l = float(row[-1])
#
#             # center point coord add tolerance
#             x_c_selStart = x_c - tolerance
#             x_c_selEnd = x_c + tolerance
#             y_c_selStart = y_c - tolerance
#             y_c_selEnd = y_c + tolerance
#             z_c_selStart = z_c - tolerance
#             z_c_selEnd = z_c + tolerance
#
#             # first point coord add tolerance
#             x_f_selStart = x_f - tolerance
#             x_f_selEnd = x_f + tolerance
#             y_f_selStart = y_f - tolerance
#             y_f_selEnd = y_f + tolerance
#             # z_f_selStart = z_f - tolerance
#             # z_f_selEnd = z_f + tolerance
#
#             # last point coord add tolerance
#             x_l_selStart = x_l - tolerance
#             x_l_selEnd = x_l + tolerance
#             y_l_selStart = y_l - tolerance
#             y_l_selEnd = y_l + tolerance
#             # z_l_selStart = z_l - tolerance
#             # z_l_selEnd = z_l + tolerance
#             # addMessage('Comparing --- now is comparing the coord between origin feature class and target feature class, centroid point x coord section is [ %s, %s ], y coord section is [ %s, %s ], z coord section is [ %s, %s ]' % (x_c_selStart, x_c_selEnd, y_c_selStart, y_c_selEnd, z_c_selStart, z_c_selEnd))
#             for eachKey, eachValue in valueDict.items():
#                 ori_x_c = float(eachValue['x_temp_c'])
#                 ori_y_c = float(eachValue['y_temp_c'])
#                 ori_z_c = float(eachValue['z_temp_c'])
#
#                 ori_x_f = float(eachValue['x_temp_f'])
#                 ori_y_f = float(eachValue['y_temp_f'])
#                 # ori_z_f = float(eachValue['z_temp_f'])
#
#                 ori_x_l = float(eachValue['x_temp_l'])
#                 ori_y_l = float(eachValue['y_temp_l'])
#                 # ori_z_l = float(eachValue['z_temp_l'])
#
#
#                 if durePolyline == 'false':
#                     if ori_x_f >= x_f_selStart and ori_x_f <= x_f_selEnd:
#                         if ori_y_f >= y_f_selStart and ori_y_f <= y_f_selEnd:
#                             if ori_x_l >= x_l_selStart and ori_x_l <= x_l_selEnd:
#                                 if ori_y_l >= y_l_selStart and ori_y_l <= y_l_selEnd:
#                                     if ori_x_c >= x_c_selStart and ori_x_c <= x_c_selEnd:
#                                         if ori_y_c >= y_c_selStart and ori_y_c <= y_c_selEnd:
#                                             if ori_z_c >= z_c_selStart and ori_z_c <= z_c_selEnd:
#                                                 addMessage('Coord Match Success')
#                                                 for m in range(len(fieldList) - 9):
#                                                     row[m] = eachValue[fieldList[m]]
#                                                 break
#                 else:
#                     if ori_x_f >= x_f_selStart and ori_x_f <= x_f_selEnd:
#                         if ori_y_f >= y_f_selStart and ori_y_f <= y_f_selEnd:
#                             if ori_x_l >= x_l_selStart and ori_x_l <= x_l_selEnd:
#                                 if ori_y_l >= y_l_selStart and ori_y_l <= y_l_selEnd:
#                                     addMessage('Coord Match Success')
#                                     for m in range(len(fieldList) - 9):
#                                         row[m] = eachValue[fieldList[m]]
#                                     break
#             cur.updateRow(row)
#
#     # delete temp field
#     if delTempField == 'true':
#         addMessage('Deleting --- temp field delete key is open, now start to delete temp field')
#
#         coordFieldList = ['x_temp_c', 'y_temp_c', 'z_temp_c', 'x_temp_f',
#                           'y_temp_f', 'z_temp_f', 'x_temp_l', 'y_temp_l', 'z_temp_l']
#         for eachField in coordFieldList:
#             try:
#                 arcpy.DeleteField_management(targetFC, eachField)
#                 addMessage('Success --- the fature "%s" delete field %s success' % (inFC, eachField))
#             except:
#                 addWarning('Warning --- the fature "%s" delete field %s faild' % (inFC, eachField))
#
#
#
#
#
#
# # main process
# def Main(inFC, targetFC, tolerance):
#     valueDict = getAttrFromFC(inFC)
#     addMessage(valueDict)
#
#     saveFieldsValue(targetFC, valueDict, tolerance)
#



fieldList = []
fieldTypeList = []

# inFC = arcpy.GetParameterAsText(0)
# targetFC = arcpy.GetParameterAsText(1)
# tolerance = arcpy.GetParameterAsText(2)
# delTempField = arcpy.GetParameterAsText(3)
# durePolyline = arcpy.GetParameterAsText(4)
inFC = r'C:\Users\lyce\Documents\ArcGIS\Projects\南京管道属性连接\南京管道属性连接.gdb\line_small'
targetFC = r'C:\Users\lyce\Documents\ArcGIS\Projects\南京管道属性连接\南京管道属性连接.gdb\mul_small'
tolerance = '10'
delTempField = 'true'
durePolyline = 'false'

# Main(inFC, targetFC, tolerance)

getAttrFromFC(inFC)