import arcpy, os, sys, re

arcpy.env.overwriteOutput = True

try:
    arcpy.CheckOutExtension("3D")
except:
    print("error in 3D License")

try:
    arcpy.CheckOutExtension("spatial")
except:
    print("error in spatial License")



def GetNewTableName(data):
    resDic = {}
    with open(data, "r") as f:
        lines = f.readlines()
        i = 0
        for each in lines:
            reTabName = None
            reTabNameNew = None

            # match OldTableName
            reTabNameCom = re.compile(r"T\d*")
            reTabNameMo = reTabNameCom.search(each)
            if reTabNameMo:
                reTabName = reTabNameMo.group()

            # match NewTableName
            reTabNameNewCom = re.compile(r"\w*_\w*_\w*")
            reTabNameNewMo = reTabNameNewCom.search(each)
            if reTabNameMo:
                reTabNameNew = reTabNameNewMo.group()

            resDic[reTabName] = reTabNameNew
            i += 1
    return resDic


def DistincTable(gdb):
    arcpy.AddMessage("table is grouping......")
    tabSet = set()
    arcpy.env.workspace = gdb
    tableList = arcpy.ListTables()
    # print tableList
    for each in tableList:
        if "T810" in each:
            tabSet.add(each[:-1])
    # print tabSet
    return tabSet



def _AddField(inFeaShp, fieldName, fieldType):
    try:
        arcpy.AddField_management(inFeaShp, fieldName, fieldType)
    except:
        arcpy.DeleteField_management(inFeaShp, fieldName)
        arcpy.AddField_management(inFeaShp, fieldName, fieldType)



def _CopyTab(inTab, outTab):
    try:
        resTab = arcpy.CopyRows_management(inTab, outTab)
    except:
        arcpy.Delete_management(inTab)
        resTab = arcpy.CopyRows_management(inTab, outTab)
    return resTab



def CreateGDB(outPath, outName):
    arcpy.AddMessage("Creating the output gdb ......")
    if os.path.isdir(outPath) and os.path.exists(outPath):
        pass
    elif os.path.isdir(outPath):
        os.makedirs(outPath)
    else:
        print("an error outPath entered")

    if not os.path.exists(os.path.join(outPath, outName + ".gdb")):
        print(os.path.join(outPath, outName))
        resGDB = arcpy.CreateFileGDB_management(outPath, outName)
        resGDB = arcpy.Describe(resGDB).catalogPath
    else:
        resGDB = os.path.join(outPath, outName + ".gdb")
    return resGDB



def tab2ply(tabGDB, tabset, resGDB, conAttr, fieldX, fieldY, fieldH, spatialReferencePRJ):

    resTotal = {"notEmpty": [], "empty": []}
    arcpy.env.workspace = tabGDB
    for each in tabset:
        plyTab = each + '1'
        pntTab = each + '2'

        count = int(arcpy.GetCount_management(pntTab)[0])
        print(count)

        if count:
            print("notEmpty")
            resTotal["notEmpty"].append(each)
            print(resGDB)
            resGDB = str(resGDB)

            outPlyStartTab = os.path.join(str(resGDB), "plyConPnt_{}_Start".format(plyTab))
            outPlyStopTab = os.path.join(resGDB, "plyConPnt_{}_Stop".format(plyTab))
            pntRes = os.path.join(resGDB, "pnt_{}".format(plyTab))
            plyRes = os.path.join(resGDB, "ply_{}".format(plyTab))
            plyResWithAttr = os.path.join(resGDB, "ply_{}_withAttr".format(plyTab))

            # outPlyStartTab = resGDB + "\\" + "plyConPnt_{}_Start".format(plyTab)
            # outPlyStopTab = resGDB + "\\" + "plyConPnt_{}_Stop".format(plyTab)
            # pntRes = resGDB + "\\" + "pnt_{}".format(plyTab)
            # plyRes = resGDB + "\\" + "ply_{}".format(plyTab)
            # plyResWithAttr = resGDB + "\\" + "ply_{}_withAttr".format(plyTab)
            print(plyTab)
            print(pntTab)

            arcpy.AddMessage("making view layer......")
            plyTabLayer = arcpy.MakeTableView_management(plyTab, "plyTabView")
            pntTabLayer = arcpy.MakeTableView_management(pntTab, "pntTabView")
            arcpy.AddJoin_management(plyTabLayer, u"FirPoint", pntTabLayer, u"TEXT")

            _AddField(plyTab, "x_pnt", "DOUBLE")
            _AddField(plyTab, "y_pnt", "DOUBLE")
            _AddField(plyTab, "h_pnt", "DOUBLE")
            _AddField(plyTab, "AAA", "SHORT")
            arcpy.AddMessage("first point, calculating fields......")
            arcpy.CalculateField_management(plyTabLayer, "x_pnt", "!{}.{}!".format(pntTab, fieldX), "PYTHON_9.3")
            arcpy.CalculateField_management(plyTabLayer, "y_pnt", "!{}.{}!".format(pntTab, fieldY), "PYTHON_9.3")
            if fieldH:
                arcpy.CalculateField_management(plyTabLayer, "h_pnt", "!{}.{}!".format(pntTab, fieldH), "PYTHON_9.3")
            arcpy.CalculateField_management(plyTabLayer, "AAA", "1", "PYTHON_9.3")

            arcpy.RemoveJoin_management(plyTabLayer)

            resTabStart = _CopyTab(plyTabLayer, outPlyStartTab)

            arcpy.AddMessage("second point, calculating fields......")

            arcpy.AddJoin_management(plyTabLayer, u"SecPoint", pntTabLayer, u"TEXT")
            arcpy.CalculateField_management(plyTabLayer, "x_pnt", "!{}.{}!".format(pntTab, fieldX), "PYTHON_9.3")
            arcpy.CalculateField_management(plyTabLayer, "y_pnt", "!{}.{}!".format(pntTab, fieldY), "PYTHON_9.3")
            if fieldH:
                arcpy.CalculateField_management(plyTabLayer, "h_pnt", "!{}.H!".format(pntTab, fieldH), "PYTHON_9.3")
            arcpy.CalculateField_management(plyTabLayer, "AAA", "2", "PYTHON_9.3")

            arcpy.RemoveJoin_management(plyTabLayer)

            resTabStop = _CopyTab(plyTabLayer, outPlyStopTab)

            arcpy.AddMessage("table merging......")

            resTab = arcpy.Append_management(resTabStop, resTabStart, "NO_TEST")


            arcpy.AddMessage("defining coordinate system......")

            SR = arcpy.SpatialReference(spatialReferencePRJ)

            pntLayer = arcpy.MakeXYEventLayer_management(resTab, "x_pnt", "y_pnt", "pntLayer", SR)

            arcpy.AddMessage("copy data......")

            arcpy.CopyFeatures_management(pntLayer, pntRes)

            arcpy.AddMessage("polyline generating......")

            resPly = arcpy.PointsToLine_management(pntRes, plyRes, "PipeID", "AAA")

            fields = ["x_pnt", "y_pnt", "h_pnt", "AAA"]
            datas = [plyTab, plyTabLayer]
            try:
                for data in datas:
                    for field in fields:
                        arcpy.DeleteField_management(data, field)
            except:
                pass

            arcpy.AddMessage("attributes adding......")

            if conAttr:
                resPlyLayer = arcpy.MakeFeatureLayer_management(resPly, "resPlyLayer")
                resPlyLayer = arcpy.AddJoin_management(resPlyLayer, "PipeID", plyTabLayer, "PipeID")
                arcpy.CopyFeatures_management(resPlyLayer, plyResWithAttr)

                try:
                    if arcpy.AlterField_management:
                        fieldList = arcpy.ListFields(plyResWithAttr)
                        for eachField in fieldList:
                            if "T810" in eachField.name:
                                fieldName = eachField.name.split("_")[-1]
                                try:
                                    arcpy.AlterField_management(plyResWithAttr, eachField.name, fieldName)
                                except:
                                    continue
                except:
                    pass
            arcpy.AddMessage("temp data, deleting.....")
            tempDataList = [outPlyStartTab, outPlyStopTab, pntRes, plyRes]
            for each in tempDataList:
                arcpy.AddMessage("deleting {}".format(each))
                arcpy.Delete_management(each)


        else:
            print("Empty")
            resTotal["empty"].append(each)
        # sys.exit()

    print(resTotal)
    arcpy.AddMessage("run log writing....")
    with open(os.path.join(os.path.split(resGDB)[0], "tableStatistic_ply.txt"), "w") as f:
        f.write(str(resTotal))

    print("finish")



def tab2plg(tabGDB, tabset, resGDB, fieldSerialNumber, spatialReferencePRJ, tabNameMapping):
    resTotal = {"notEmpty": [], "empty": [], "plgEnable": [], "plgAble": []}
    arcpy.env.workspace = tabGDB
    for each in tabset:
        plyTab = each + u'1'
        pntTab = each + u'2'
        plgTab = each + u'3'

        count = int(arcpy.GetCount_management(pntTab)[0])
        print(pntTab)

        if count:
            print("notEmpty")
            resTotal["notEmpty"].append(each)

            pntTemp = os.path.join(resGDB, "pntTemp_%s" % pntTab)
            plgRes = os.path.join(resGDB, "plg_%s" % plgTab)
            pntRes = os.path.join(resGDB, "pnt_%s" % pntTab)
            plyRes = os.path.join(resGDB, "ply_%s" % plyTab)
            plgResSpatialJoin = os.path.join(resGDB, tabNameMapping[plgTab])

            _AddField(pntTab, "BBB", "STRING")
            _AddField(pntTab, "CCC", "STRING")
            arcpy.CalculateField_management(pntTab, "BBB", "!%s![:-1]" % fieldSerialNumber, "PYTHON_9.3")
            arcpy.CalculateField_management(pntTab, "CCC", "!%s![-1:]" % fieldSerialNumber, "PYTHON_9.3")

            pntTabLayer = arcpy.MakeTableView_management(pntTab, "pntTabView")

            arcpy.AddMessage("defining coordinate system......")

            SR = arcpy.SpatialReference(spatialReferencePRJ)

            pntLayer = arcpy.MakeXYEventLayer_management(pntTabLayer, "Y", "X", "pntLayer", SR)

            arcpy.Select_analysis(pntLayer, pntTemp,
                                  "\"CCC\" IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q')")

            if int(arcpy.GetCount_management(pntTemp)[0]):
                resTotal["plgAble"].append(each)

                arcpy.CopyFeatures_management(pntTemp, pntRes)

                arcpy.AddMessage("polygon generating......")

                resPly = arcpy.PointsToLine_management(pntRes, plyRes, "BBB", "CCC", "CLOSE")

                arcpy.FeatureToPolygon_management(resPly, plgRes)

                arcpy.AddMessage("attributes adding......")

                arcpy.SpatialJoin_analysis(plgRes, pntRes, plgResSpatialJoin)


                try:
                    arcpy.DeleteField_management(pntTab, "BBB")
                    arcpy.DeleteField_management(pntTab, "CCC")
                except:
                    pass


            else:
                resTotal["plgEnable"].append(each)
                continue

            arcpy.AddMessage("temp data, deleting.....")
            # tempDataList = [pntTemp, plgRes, pntRes, plyRes]
            tempDataList = [pntTemp, plgRes, plyRes]
            for each in tempDataList:
                arcpy.AddMessage("deleting {}".format(each))
                arcpy.Delete_management(each)


        else:
            print("Empty")
            resTotal["empty"].append(each)
        # sys.exit()

    print("finish")


    print(resTotal)
    with open(os.path.join(os.path.split(resGDB)[0], "tableStatistic_plg.txt"), "w") as f:
        f.write(str(resTotal))


gdb = arcpy.GetParameterAsText(0)
outPath = arcpy.GetParameterAsText(1)
outName = arcpy.GetParameterAsText(2)
fieldSerialNumber = arcpy.GetParameterAsText(3)
spatialReferencePRJ = arcpy.GetParameterAsText(4)
tabNameTxt = arcpy.GetParameterAsText(5)

# gdb = r"E:\arcmapTest\progress\process_1.gdb"
# outPath = r"E:\arcmapTest\res"
# outName = "v"
# fieldX = "X"
# fieldY = "Y"
# fieldH = "H"
# conAttr = True


# codeType = "utf-8"
# gdb = gdb.decode(codeType)
# outPath = outPath.decode(codeType)
# outName = outName.decode(codeType)

if tabNameTxt:
    arcpy.AddMessage("table name mapping matching......")
    try:
        tabNameMapping = GetNewTableName(tabNameTxt)
        arcpy.AddMessage("table name match done")
    except BaseException as e:
        tabNameMapping = {None: None, 'T81010101': 'DL_GD_L', 'T81010102': 'DL_GD_P', 'T81010103': 'DL_GD_A', 'T81010201': 'DL_LD_L', 'T81010202': 'DL_LD_P', 'T81010203': 'DL_LD_A', 'T81010301': 'DL_DC_L', 'T81010302': 'DL_DC_P', 'T81010303': 'DL_DC_A', 'T81010401': 'DL_JTXHD_L', 'T81010402': 'DL_JTXHD_P', 'T81010403': 'DL_JTXHD_A', 'T81010501': 'DL_GGJGD_L', 'T81010502': 'DL_GGJGD_P', 'T81010503': 'DL_GGJGD_A', 'T81010601': 'DL_ZLZYXL_L', 'T81010602': 'DL_ZLZYXL_P', 'T81010603': 'DL_ZLZYXL_A', 'T81010701': 'DL_DLTX_L', 'T81010702': 'DL_DLTX_P', 'T81010703': 'DL_DLTX_A', 'T81019901': 'DL_QT_L', 'T81019902': 'DL_QT_P', 'T81019903': 'DL_QT_A', 'T81020101': 'TX_DXDL_L', 'T': 'QT_ZHGG_P', 'T81020103': 'TX_DXDL_A', 'T81020201': 'TX_GBDS_L', 'T81020202': 'TX_GBDS_P', 'T81020203': 'TX_GBDS_A', 'T81020301': 'TX_XX_L', 'T81020302': 'TX_XX_P', 'T81020303': 'TX_XX_A', 'T81020401': 'TX_JK_L', 'T81020402': 'TX_JK_P', 'T81020403': 'TX_JK_A', 'T81020501': 'TX_ZX_L', 'T81020502': 'TX_ZX_P', 'T81020503': 'TX_ZX_A', 'T81029901': 'TX_QT_L', 'T81029902': 'TX_QT_P', 'T81029903': 'TX_QT_A', 'T81030101': 'JS_SS_L', 'T81030102': 'JS_SS_P', 'T81030103': 'JS_SS_A', 'T81030201': 'JS_YS_L', 'T81030202': 'JS_YS_P', 'T81030203': 'JS_YS_A', 'T81030301': 'JS_ZS_L', 'T81030302': 'JS_ZS_P', 'T81030303': 'JS_ZS_A', 'T81030401': 'JS_XF_L', 'T81030402': 'JS_XF_P', 'T81030403': 'JS_XF_A', 'T81030501': 'JS_LH_L', 'T81030502': 'JS_LH_P', 'T81030503': 'JS_LH_A', 'T81039901': 'JS_QT_L', 'T81039902': 'JS_QT_P', 'T81039903': 'JS_QT_A', 'T81040101': 'PS_YS_L', 'T81040102': 'PS_YS_P', 'T81040103': 'PS_YS_A', 'T81040201': 'PS_WS_L', 'T81040202': 'PS_WS_P', 'T81040203': 'PS_WS_A', 'T81040301': 'PS_YWHL_L', 'T81040302': 'PS_YWHL_P', 'T81040303': 'PS_YWHL_A', 'T81049901': 'PS_QT_L', 'T81049902': 'PS_QT_P', 'T81049903': 'PS_QT_A', 'T81050101': 'RQ_MQ_L', 'T81050102': 'RQ_MQ_P', 'T81050103': 'RQ_MQ_A', 'T81050201': 'RQ_TRQ_L', 'T81050202': 'RQ_TRQ_P', 'T81050203': 'RQ_TRQ_A', 'T81050301': 'RQ_YHQ_L', 'T81050302': 'RQ_YHQ_P', 'T81050303': 'RQ_YHQ_A', 'T81059901': 'RQ_QT_L', 'T81059902': 'RQ_QT_P', 'T81059903': 'RQ_QT_A', 'T81060101': 'RL_ZQ_L', 'T81060102': 'RL_ZQ_P', 'T81060103': 'RL_ZQ_A', 'T81060201': 'RL_RS_L', 'T81060202': 'RL_RS_P', 'T81060203': 'RL_RS_A', 'T81069901': 'RL_QT_L', 'T81069902': 'RL_QT_P', 'T81069903': 'RL_QT_A', 'T81070101': 'GY_QQ_L', 'T81070102': 'GY_QQ_P', 'T81070103': 'GY_QQ_A', 'T81070201': 'GY_YQ_L', 'T81070202': 'GY_YQ_P', 'T81070203': 'GY_YQ_A', 'T81070301': 'GY_YQ_L', 'T81070302': 'GY_YQ_P', 'T81070303': 'GY_YQ_A', 'T81070401': 'GY_YY_L', 'T81070402': 'GY_YY_P', 'T81070403': 'GY_YY_A', 'T81070501': 'GY_CPY_L', 'T81070502': 'GY_CPY_P', 'T81070503': 'GY_CPY_A', 'T81070601': 'GY_HY_L', 'T81070602': 'GY_HY_P', 'T81070603': 'GY_HY_A', 'T81070701': 'GY_PZ_L', 'T81070702': 'GY_PZ_P', 'T81070703': 'GY_PZ_A', 'T81070801': 'GY_YX_L', 'T81070802': 'GY_YX_P', 'T81070803': 'GY_YX_A', 'T81079901': 'GY_QT_L', 'T81079902': 'GY_QT_P', 'T81079903': 'GY_QT_A', 'T81080101': 'QT_ZHGG_L', 'T81080103': 'QT_ZHGG_A', 'T81080201': 'QT_TSGX_L', 'T81080202': 'QT_TSGX_P', 'T81080203': 'QT_TSGX_A', 'T81080301': 'QT_QSBMGX_L', 'T81080302': 'QT_QSBMGX_P', 'T81080303': 'QT_QSBMGX_A', 'T81090101': 'CSGX_SD_L', 'T81090102': 'CSGX_SD_P', 'T81090103': 'CSGX_SD_A', 'T81090201': 'CSGX_TX_L', 'T81090202': 'CSGX_TX_P', 'T81090203': 'CSGX_TX_A', 'T81090301': 'CSGX_SS_L', 'T81090302': 'CSGX_SS_P', 'T81090303': 'CSGX_SS_A', 'T81090401': 'CSGX_SQ_L', 'T81090402': 'CSGX_SQ_P', 'T81090403': 'CSGX_SQ_A', 'T81090501': 'CSGX_SY_L', 'T81090502': 'CSGX_SY_P', 'T81090503': 'CSGX_SY_A', 'T81099901': 'CSGX_QTCSGX_L', 'T81099902': 'CSGX_QTCSGX_P', 'T81099903': 'CSGX_QTCSGX_A'}
        arcpy.AddMessage("table name match failed, use default table name mapping !!!")
else:
    arcpy.AddMessage("table name match file is not defined, use default table name mapping !!!")
    tabNameMapping = {None: None, 'T81010101': 'DL_GD_L', 'T81010102': 'DL_GD_P', 'T81010103': 'DL_GD_A', 'T81010201': 'DL_LD_L', 'T81010202': 'DL_LD_P', 'T81010203': 'DL_LD_A', 'T81010301': 'DL_DC_L', 'T81010302': 'DL_DC_P', 'T81010303': 'DL_DC_A', 'T81010401': 'DL_JTXHD_L', 'T81010402': 'DL_JTXHD_P', 'T81010403': 'DL_JTXHD_A', 'T81010501': 'DL_GGJGD_L', 'T81010502': 'DL_GGJGD_P', 'T81010503': 'DL_GGJGD_A', 'T81010601': 'DL_ZLZYXL_L', 'T81010602': 'DL_ZLZYXL_P', 'T81010603': 'DL_ZLZYXL_A', 'T81010701': 'DL_DLTX_L', 'T81010702': 'DL_DLTX_P', 'T81010703': 'DL_DLTX_A', 'T81019901': 'DL_QT_L', 'T81019902': 'DL_QT_P', 'T81019903': 'DL_QT_A', 'T81020101': 'TX_DXDL_L', 'T': 'QT_ZHGG_P', 'T81020103': 'TX_DXDL_A', 'T81020201': 'TX_GBDS_L', 'T81020202': 'TX_GBDS_P', 'T81020203': 'TX_GBDS_A', 'T81020301': 'TX_XX_L', 'T81020302': 'TX_XX_P', 'T81020303': 'TX_XX_A', 'T81020401': 'TX_JK_L', 'T81020402': 'TX_JK_P', 'T81020403': 'TX_JK_A', 'T81020501': 'TX_ZX_L', 'T81020502': 'TX_ZX_P', 'T81020503': 'TX_ZX_A', 'T81029901': 'TX_QT_L', 'T81029902': 'TX_QT_P', 'T81029903': 'TX_QT_A', 'T81030101': 'JS_SS_L', 'T81030102': 'JS_SS_P', 'T81030103': 'JS_SS_A', 'T81030201': 'JS_YS_L', 'T81030202': 'JS_YS_P', 'T81030203': 'JS_YS_A', 'T81030301': 'JS_ZS_L', 'T81030302': 'JS_ZS_P', 'T81030303': 'JS_ZS_A', 'T81030401': 'JS_XF_L', 'T81030402': 'JS_XF_P', 'T81030403': 'JS_XF_A', 'T81030501': 'JS_LH_L', 'T81030502': 'JS_LH_P', 'T81030503': 'JS_LH_A', 'T81039901': 'JS_QT_L', 'T81039902': 'JS_QT_P', 'T81039903': 'JS_QT_A', 'T81040101': 'PS_YS_L', 'T81040102': 'PS_YS_P', 'T81040103': 'PS_YS_A', 'T81040201': 'PS_WS_L', 'T81040202': 'PS_WS_P', 'T81040203': 'PS_WS_A', 'T81040301': 'PS_YWHL_L', 'T81040302': 'PS_YWHL_P', 'T81040303': 'PS_YWHL_A', 'T81049901': 'PS_QT_L', 'T81049902': 'PS_QT_P', 'T81049903': 'PS_QT_A', 'T81050101': 'RQ_MQ_L', 'T81050102': 'RQ_MQ_P', 'T81050103': 'RQ_MQ_A', 'T81050201': 'RQ_TRQ_L', 'T81050202': 'RQ_TRQ_P', 'T81050203': 'RQ_TRQ_A', 'T81050301': 'RQ_YHQ_L', 'T81050302': 'RQ_YHQ_P', 'T81050303': 'RQ_YHQ_A', 'T81059901': 'RQ_QT_L', 'T81059902': 'RQ_QT_P', 'T81059903': 'RQ_QT_A', 'T81060101': 'RL_ZQ_L', 'T81060102': 'RL_ZQ_P', 'T81060103': 'RL_ZQ_A', 'T81060201': 'RL_RS_L', 'T81060202': 'RL_RS_P', 'T81060203': 'RL_RS_A', 'T81069901': 'RL_QT_L', 'T81069902': 'RL_QT_P', 'T81069903': 'RL_QT_A', 'T81070101': 'GY_QQ_L', 'T81070102': 'GY_QQ_P', 'T81070103': 'GY_QQ_A', 'T81070201': 'GY_YQ_L', 'T81070202': 'GY_YQ_P', 'T81070203': 'GY_YQ_A', 'T81070301': 'GY_YQ_L', 'T81070302': 'GY_YQ_P', 'T81070303': 'GY_YQ_A', 'T81070401': 'GY_YY_L', 'T81070402': 'GY_YY_P', 'T81070403': 'GY_YY_A', 'T81070501': 'GY_CPY_L', 'T81070502': 'GY_CPY_P', 'T81070503': 'GY_CPY_A', 'T81070601': 'GY_HY_L', 'T81070602': 'GY_HY_P', 'T81070603': 'GY_HY_A', 'T81070701': 'GY_PZ_L', 'T81070702': 'GY_PZ_P', 'T81070703': 'GY_PZ_A', 'T81070801': 'GY_YX_L', 'T81070802': 'GY_YX_P', 'T81070803': 'GY_YX_A', 'T81079901': 'GY_QT_L', 'T81079902': 'GY_QT_P', 'T81079903': 'GY_QT_A', 'T81080101': 'QT_ZHGG_L', 'T81080103': 'QT_ZHGG_A', 'T81080201': 'QT_TSGX_L', 'T81080202': 'QT_TSGX_P', 'T81080203': 'QT_TSGX_A', 'T81080301': 'QT_QSBMGX_L', 'T81080302': 'QT_QSBMGX_P', 'T81080303': 'QT_QSBMGX_A', 'T81090101': 'CSGX_SD_L', 'T81090102': 'CSGX_SD_P', 'T81090103': 'CSGX_SD_A', 'T81090201': 'CSGX_TX_L', 'T81090202': 'CSGX_TX_P', 'T81090203': 'CSGX_TX_A', 'T81090301': 'CSGX_SS_L', 'T81090302': 'CSGX_SS_P', 'T81090303': 'CSGX_SS_A', 'T81090401': 'CSGX_SQ_L', 'T81090402': 'CSGX_SQ_P', 'T81090403': 'CSGX_SQ_A', 'T81090501': 'CSGX_SY_L', 'T81090502': 'CSGX_SY_P', 'T81090503': 'CSGX_SY_A', 'T81099901': 'CSGX_QTCSGX_L', 'T81099902': 'CSGX_QTCSGX_P', 'T81099903': 'CSGX_QTCSGX_A'}

tabSet = DistincTable(gdb)

resGDB = CreateGDB(outPath, outName)

# tab2ply(gdb, tabSet, resGDB, conAttr, fieldX, fieldY, fieldH, spatialReferencePRJ)

# tab2plg(gdb, tabSet, resGDB, conAttr)
tab2plg(gdb, tabSet, resGDB, fieldSerialNumber, spatialReferencePRJ, tabNameMapping)

arcpy.CheckInExtension("3D")
arcpy.CheckInExtension("spatial")