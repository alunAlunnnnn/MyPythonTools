import arcpy, os

arcpy.env.overwriteOutput = True

class AddFieldFaild(Exception):
    pass


def addMessage(mes):
    print(mes)
    arcpy.AddMessage(mes)


def addWarning(mes):
    print(mes)
    arcpy.AddWarning(mes)


def addError(mes):
    print(mes)
    arcpy.AddError(mes)


def addField(inFC, fieldName, fieldType):
    try:
        try:
            arcpy.AddField_management(inFC, fieldName, fieldType)
        except:
            arcpy.DeleteField_management(inFC, fieldName)
            arcpy.AddField_management(inFC, fieldName, fieldType)
    except:
        addError('Error --- feature class %s add field %s failed, please check whether the feature class is using by other app or not' % (inFC, fieldName))
        raise AddFieldFaild


def processPnt()

