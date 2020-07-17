# -*- coding: utf-8 -*-
import arcpy, os, functools, datetime
'''arcmap tools, used to merge multi same name data to one data'''


arcpy.env.overwriteOutput = True


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


def getRunTime(func):
    @functools.wraps(func)
    def _getRunTime(*args, **kwargs):
        startTime = datetime.datetime.now()

        res = func(*args, **kwargs)

        endTime = datetime.datetime.now()
        costTime = endTime - startTime

        addMessage('start time: %s' % startTime)
        addMessage('stop time: %s' % endTime)
        addMessage('cost time: %s' % costTime)
        return res

    return _getRunTime


@getRunTime
def getAllDatas(dataPath):
    global compList

    arcpy.env.workspace = dataPath
    # get all workspaces
    wkList = arcpy.ListWorkspaces()

    datasList = []

    for eachWk in wkList:
        # each workspace dir
        wk = os.path.join(dataPath, eachWk)

        arcpy.env.workspace = wk

        # add dataset into datasetSet if no same name dataset in it
        datasetList = arcpy.ListDatasets('', 'Feature')
        for eachDataset in datasetList:
            # get all datas in dataSet
            dataList = arcpy.ListFeatureClasses('', '', eachDataset)

            # get spatial reference
            sr = arcpy.Describe(eachDataset).spatialReference

            for eachData in dataList:
                datasList.append(os.path.join(wk, eachDataset, eachData))

                compData = eachDataset + '\\' + eachData
                if compData not in compList:
                    compList.append((compData, sr))

    return datasList


def mergeAllDatas(dataPath, dataList):
    global compList
    gdbName = arcpy.CreateUniqueName('resGDB', dataPath)

    # create result gdb
    resGDB = arcpy.CreateFileGDB_management(dataPath, gdbName)

    for eachSet in compList:
        eachSet = eachSet[0]
        sr = eachSet[1]
        # group each data in same dataset name and data name
        mergeData = []
        for eachData in dataList:
            if eachSet in eachData:
                mergeData.append(eachData)

        if len(mergeData) > 0:
            # create feature data set
            datasetName = eachSet.split('\\')[0]
            if not arcpy.Exists(os.path.join(dataPath, gdbName, datasetName)):
                resDataset = arcpy.CreateFeatureDataset_management(resGDB, datasetName, sr)

        # if only one data in mergeData, just copy data
        if len(mergeData) == 1:
            arcpy.CopyFeatures_management(mergeData[0], os.path.join(resGDB, eachSet))
        # if more than one data in mergeData, get the max number of fields, and copy it as append target
        elif len(mergeData) > 1:
            fieldList = []
            copyData = ''

            # define which data will be copy
            for eachMerData in mergeData:
                fieldList_tmp = [eachField for eachField in arcpy.ListFields(eachMerData)]
                if len(fieldList_tmp) > len(fieldList):
                    fieldList = fieldList_tmp
                    copyData = eachMerData

            arcpy.CopyFeatures_management(copyData, os.path.join(resGDB, eachSet))

            # remove the data have been copied
            mergeData.remove(copyData)

            # 



dataPath = r'E:/ArcMapDustbin'
compList = []

# get all datas in each
dataList = getAllDatas(dataPath)
print(getAllDatas(dataPath))
print(compList)




