import inspect
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
logFile = os.path.join(logDir, "tool1_gxthdem_log.txt")
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

    logging.debug("Module import success")
except BaseException as e:
    logging.error(str(e))

arcpy.env.overwriteOutput = True


# ---------- show message in toolbox ----------

def _addMessage(mes: str) -> None:
    print(mes)
    arcpy.AddMessage(mes)
    return None


def _addWarning(mes: str) -> None:
    print(mes)
    arcpy.AddWarning(mes)
    return None


def _addError(mes: str) -> None:
    print(mes)
    arcpy.AddError(mes)
    return None


def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        print(f"Method {func.__name__} start running ! ")
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        stop = datetime.datetime.now()
        cost = stop - start
        print("*" * 30)
        print(f"Method {func.__name__} start at {start}")
        print(f"Method {func.__name__} finish at {stop}")
        print(f"Method {func.__name__} total cost {cost}")
        print("*" * 30)
        return res

    return _wrapper


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


def _addField(*args, **kwargs):
    try:
        arcpy.AddField_management(*args, **kwargs)
    except:
        arcpy.DeleteField_management(*(args[:2]))
        arcpy.AddField_management(*args, **kwargs)


def addFiled(inFC, fieldName, fieldType, fieldLength=None, fieldPrec=None):
    if fieldLength:
        if fieldPrec:
            _addField(inFC, fieldName, fieldType, field_length=fieldLength, field_precision=fieldPrec)
        else:
            _addField(inFC, fieldName, fieldType, field_length=fieldLength)
    else:
        _addField(inFC, fieldName, fieldType)
    return inFC


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
def interShape3D(inDEM, inFC, outputPath, outputName):
    @setTempWorkspace(outputPath)
    def _wrapper(inDEM, inFC, outputPath, outputName):
        # logging.debug(f" ------ start function interShape3D ------")
        # logging.debug(f" --- \n inDEM: {inDEM} \n inFC: {inFC} \n"
        #               f" outputPath: {outputPath} \n outputName: {outputName} \n ")
        # get a available data, in different workspace
        outputData = availableDataName(outputPath, outputName)

        # main fuction process start
        arcpy.InterpolateShape_3d(inDEM, inFC, outputData)

        return outputData

    res = _wrapper(inDEM, inFC, outputPath, outputName)
    return res


# add format field to feature classes
def addFormatField(inFC, QDMS, ZDMS):
    """
    usage: add four format field into line feature class, and calculate it in sub method.
    :param inFC: feature class, pipe line(2d) feature classes .
    :param QDMS: field, the buried depth field of the first point in the line.
    :param ZDMS: field, the buried depth field of the last point in the line.
    :return: string, the directory of feature class have inputed.
    """
    logging.debug(f" ------ start function addFormatField ------")
    logging.debug(f" --- \n inFC: {inFC} \n QDMS: {QDMS} \n"
                  f" ZDMS: {ZDMS} \n")
    fieldName = ["ori_z_f", "ori_z_l", "tar_z_f", "tar_z_l"]
    fieldType = "DOUBLE"

    # the field 'depth of firstPoint' and 'depth of lastPoint', the values in them mean that
    # greater than zero --- under the floor, less than zero --- on the floor
    fieldExp = ["!shape.firstPoint.z!", "!shape.lastPoint.z!",
                f"!ori_z_f! - !{QDMS}!", f"!ori_z_l! - !{ZDMS}!"]

    for i, eachField in enumerate(fieldName):
        logging.debug(f"start add field_{i} {eachField}")
        addFiled(inFC, eachField, fieldType)
        logging.debug(f"success add field {eachField},"
                      f" and start calculate it by expression {fieldExp[i]}")
        arcpy.CalculateField_management(inFC, eachField, fieldExp[i], "PYTHON3")
        logging.debug(f"success calculate filed {eachField}")
    return inFC


def convertTo3DWithAttr(inFC, outputPath, outputName):
    logging.debug(f" ------ start function convertTo3DWithAttr ------")
    logging.debug(f" --- \n inFC: {inFC} \n outputPath: {outputPath} \n"
                  f" outputName: {outputName} \n")

    resData = availableDataName(outputPath, outputName)

    logging.debug("start process feature class to 3d")
    arcpy.FeatureTo3DByAttribute_3d(inFC, resData, "tar_z_f", "tar_z_l")
    logging.debug("success process feature class to 3d")

    return resData


@getRunTime
def main(inDEM, inFC, outputPath, outputName, QDMS, ZDMS):
    logging.info("Step1 --- start interpolate 3d to feature class.")
    # award the height of dem to polyline
    outFC = interShape3D(inDEM, inFC, outputPath, outputName + "_temp")

    logging.info("Step2 --- add and calculate format field.")
    # add and calculate four format field to feature class
    outFC = addFormatField(outFC, QDMS, ZDMS)

    logging.info("Step3 --- convert data to 3d type")
    convertTo3DWithAttr(outFC, outputPath, outputName)

    try:
        arcpy.Delete_management(outFC)
    except:
        pass


inDEM = r"E:\南京工具\工具交活整理_0916\测试数据\工具1_DEM起伏\0813现状.dem"
inFC = r"E:\南京工具\工具交活整理_0916\测试数据\工具1_DEM起伏\line.shp"
outputPath = r"E:\南京工具\工具交活整理_0916\测试数据\工具1_DEM起伏\res"
outputName = "test"
QDMS = "QDMS"
ZDMS = "ZDMS"
if __name__ == "__main__":
    try:
        logging.info(" ======================== Start ========================")
        logging.debug(f" --- \n inDEM: {inDEM} \n inFC: {inFC} \n"
                      f" outputPath: {outputPath} \n outputName: {outputName} \n"
                      f" QDMS: {QDMS} \n ZDMS: {ZDMS}")
        main(inDEM, inFC, outputPath, outputName, QDMS, ZDMS)
        logging.info("Tool Runs Successful")
    except BaseException as e:
        logging.error(str(e))
        _addError(str(e))