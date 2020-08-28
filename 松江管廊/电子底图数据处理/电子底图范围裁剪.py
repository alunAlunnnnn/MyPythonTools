import arcpy
import os

arcpy.env.overwriteOutput = True


# make date target directory
def makeDataDir(originDir, newDir):
    for root, dirs, file in os.walk(originDir):
        print(root, dirs, file)
        cDirs = root.split(originDir)[1][1:]
        # child directory is exist
        if len(cDirs) > 0:
            # if directory is not exist, create it
            if (not os.path.exists(os.path.join(newDir, cDirs))
                    and cDirs[-4:] != ".gdb" and cDirs[-4:] != ".mdb"):
                os.makedirs(os.path.join(newDir, cDirs))


# clip all datas to new directories
def copyAllDatas(originDir, newDir, clipData):
    n = 1
    for root, dirs, files in os.walk(originDir):
        arcpy.env.workspace = root
        cDirs = root.split(originDir)[1][1:]
        resDir = os.path.join(newDir, cDirs)
        print("******")
        print(resDir)
        print(os.path.join(os.path.dirname(resDir), os.path.basename(resDir)))
        print("******")
        gdbKey = False

        if root[-4:] == ".gdb" or root[-4:] == ".mdb":
            if not arcpy.Exists(os.path.join(os.path.dirname(resDir), os.path.basename(resDir))):
                gdb = arcpy.CreateFileGDB_management(os.path.dirname(resDir), os.path.basename(resDir))
            gdbKey = True

        # get all datas in the directories
        dataList = arcpy.ListFeatureClasses()

        for eachData in dataList:
            # if data has not spatial reference
            desc = arcpy.Describe(eachData)
            sr = desc.spatialReference
            if sr.name == "Unknown":
                try:
                    arcpy.DefineProjection_management(eachData, "4326")
                except:
                    pass

            # clip data
            # if gdbKey:
            #     outputPath = os.path.join(os.path.dirname(root), os.path.basename(root))
            # else:
            #     outputPath = root
            try:
                arcpy.Clip_analysis(eachData, clipData, os.path.join(resDir, eachData))
            except:
                print("ERROR --- %s " % os.path.join(resDir, eachData))
                pass
            n += 1
            print(n)


# compare origin directory and new directory, make sure all data has pushed into new dir
def compareDir(originDir, targetDir):
    newDir = targetDir
    originDirList = []
    originFileList = []
    for root, dirs, files in os.walk(originDir):
        originDirList.append(root)
        for eachFile in files:
            originFileList.append(os.path.join(root, eachFile))

    targetDirList = []
    targetFileList = []
    for root, dirs, files in os.walk(targetDir):
        targetDirList.append(root)
        for eachFile in files:
            targetFileList.append(os.path.join(root, eachFile))

    print(originDirList)
    print(originFileList)
    print(targetDirList)
    print(targetFileList)

    for eachFile in originFileList:
        eachFile = eachFile.replace(originDir, "")[1:]
        # print(eachFile)
        tarFile = os.path.join(newDir, eachFile)
        print(tarFile)
        try:
            ind = targetFileList.index(str(tarFile).replace("\\", "\\\\"))
            targetFileList.remove(ind)
        except:
            pass

    print(targetFileList)
    print(len(targetFileList))


datadir = r"E:\上海电子底图\Basemap2013V2.1_1204"
newdir = r"E:\上海电子底图\new_basemap"
shp_xzbj = r"E:\松江管廊\新数据0805\影像裁剪\aprx\松江影像裁剪\松江影像裁剪.gdb\松江区行政边界"

# makeDataDir(datadir, newdir)

# copyAllDatas(datadir, newdir, shp_xzbj)

compareDir(datadir, newdir)
