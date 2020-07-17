# -*- coding: utf-8 -*-

import arcpy, os, urllib, httplib, json, multiprocessing, getpass, sys, time
from datetime import datetime
import xml.dom.minidom as DOM
from PK_YZT_SupportPackage import *

try:
    windowsUserName = getpass.getuser()
except:
    pass
try:
    cpuCount = multiprocessing.cpu_count()
except:
    pass

arcpy.env.overwriteOutput = True


# 创建运行日志文件夹
def RunLogDirs(outputPath):
    newdir = os.path.join(outputPath, "RunLogDir")
    if os.path.exists(newdir):
        pass
    else:
        try:
            os.makedirs(newdir)
            return "Directory created successful"
        except:
            return "RunError, outPutPath is not exists"


# 写入运行日志模块
def RunLogWrite(logPath, logName, messages):
    # 判断数据类型，以免出现无法写入或者乱码的错误
    if isinstance(messages, unicode):
        messages.encode("utf-8")
    elif isinstance(messages, str):
        messages = messages
    else:
        messages = str(messages).replace("[", "").replace("]", "")
    # 创建运行日志并写入消息内容
    logName = os.path.join(logPath, logName)
    try:
        os.makedirs(logPath)
    except:
        pass
    finally:
        with open(logName + ".txt", "w") as log:
            log.writelines("Script start at " + str(datetime.now()) + "\n")
            log.writelines("Run Log Writing... \n")
            log.writelines(messages)


# 获取登录令牌
def getToken(username, password, serverName, serverPort, outputPath):
    tokenURL = "/arcgis/admin/generateToken"
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        message = "URL connect status is not 200."
        RunLogWrite(outputPath, "TokenRunLog", message)
        return
    else:
        data = response.read()
        httpConn.close()
        # 检查JSON获取是否正常
        if not assertJsonSuccess(data):
            message = "URL Connect Successful, But JSON is not useful."
            RunLogWrite(outputPath, "TokenRunLog", message)
            return
        token = json.loads(data)
        message = "Token get successful"
        RunLogWrite(outputPath, "TokenRunLog", message)
        return token['token']


#  判断JSON返回是否正常
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        message = "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True


# 1、由featureClass创建Layer,用于加载到mxd的df当中去----------
def MakeLayers(inFea, outputPath):
    try:
        # 用于创建"LyrTemp"文件夹
        LyrTempDir = os.path.join(outputPath, "LyrTemp")
        # 用于记录运行情况
        runLog = os.path.join(os.path.join(outputPath, "RunLogDir"), "MakeLayersLog.txt")
        try:
            os.makedirs(LyrTempDir)
        except:
            pass
        lyrList = []
        # 创建用于发布的临时图层
        for each in inFea:
            # 1、定义templyr
            each = YZT_CodingJudge(each)
            lyrname = os.path.splitext(os.path.split(each)[1])
            lyrNameInMxd = lyrname[0]
            templyr = os.path.join(LyrTempDir, lyrname[0] + ".lyr")

            # 2、有fea创建并另存图层文件
            lyr = arcpy.MakeFeatureLayer_management(each, lyrNameInMxd)
            arcpy.SaveToLayerFile_management(lyr, templyr)
            lyrs = arcpy.mapping.Layer(templyr)
            lyrList.append(lyrs)
        return lyrList
    except BaseException as e:
        with open(runLog, "w") as f:
            f.writelines("Run time is {} \n".format(datetime.now()))
            f.writelines("Log: \n")
            f.writelines(str(e))
        return False


# 这里需要一个已经创建好的mxd用于存放数据并发布服务
# inLayer传入一个图层对象的列表，同类型（点、线、面）的越靠前越在上。用于将Layer类型文件传入MXD并发布。
# tempMxd用于临时承载数据及计算过程，数据入口暂时保留
def MakeMxd(inLayer, tempMxd, outputPath, outputName):
    try:
        try:
            RunLogDirs(outputPath)
        except:
            pass
        logDir = os.path.join(outputPath, "RunLogDir")
        tempMxdDir = os.path.join(outputPath, "mxdTemp")
        tempMxds = os.path.join(tempMxdDir, outputName + ".mxd")
        try:
            os.makedirs(tempMxdDir)
        except:
            pass

        # 创建mxd并且激活第一个df
        mxd = arcpy.mapping.MapDocument(tempMxd)
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        for each in inLayer:
            each = YZT_CodingJudge(each)
            descLyr = arcpy.Describe(each)
            feaInlyr = descLyr.featureClass
            # 通过featureClass创建图层，再保存为图层文件，再通过Layer调用才可以加载到mxd的df中
            if feaInlyr.shapeType == "Point" or feaInlyr.shapeType == "Multipoint":
                arcpy.mapping.AddLayer(df, each, "TOP")
            elif feaInlyr.shapeType == "Polyline":
                arcpy.mapping.AddLayer(df, each)
            else:
                arcpy.mapping.AddLayer(df, each, "BOTTOM")

        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()
        mxd.saveACopy(tempMxds, "10.0")
        del mxd
        return tempMxds

    except BaseException as e:
        logDir = os.path.join(outputPath, "RunLogDir")
        errlog = os.path.join(logDir, "CreateMxdLog.txt")
        with open(errlog, "w") as f:
            f.writelines("The Module 'MakeMxd' ran at {} \n".format(datetime.now()))
            f.writelines("Module Field, Log: \n")
            f.writelines(str(e))


def PublishMxdToServer(inmxd, outputPath, outputName, serviceName, copy_data_to_server, folder_name, summary, tags,
                       serverHost="localhost", serverPort="6080", username="siteadmin", password="siteadmin",
                       registerDataSource=True):
    pubDir = os.path.join(outputPath, "PublishTemp")
    try:
        os.makedirs(pubDir)
    except:
        pass
    env = pubDir
    mxdDoc = inmxd
    serverConnName = outputName + ".ags"
    arcpy.mapping.CreateGISServerConnectionFile("ADMINISTER_GIS_SERVICES", env, serverConnName,
                                                "http://{}:{}/arcgis/admin".format(serverHost, serverPort),
                                                "ARCGIS_SERVER", "", "", username, password, "SAVE_USERNAME")
    # 创建服务连接
    con = os.path.join(env, serverConnName)

    if registerDataSource == True:
        RegisterDataSource(mxdDoc, con)
    else:
        copy_data_to_server = True

    # 创建.sddraft文件
    sddraft = os.path.join(env, serviceName + ".sddraft")
    analyst = arcpy.mapping.CreateMapSDDraft(mxdDoc, sddraft, serviceName, 'ARCGIS_SERVER', con, copy_data_to_server,
                                             folder_name, summary, tags)
    sd = os.path.join(env, serviceName + ".sd")
    # 检测mxd文档中的错误并输出日志
    with open(os.path.join(env, "SDAnalystLog.txt"), "w") as f:
        # for each in analyst:
        #     f.writelines(each + ": ")
        #     f.writelines(str(analyst[each]) + "\n")
        for key in ('messages', 'warnings', 'errors'):
            mes1 = "======" + key.upper() + "======"
            f.writelines("\n" + str(datetime.now()) + "\n")
            f.writelines("\n" + mes1 + "\n")
            vars = analyst[key]
            for ((message, code), layerlist) in vars.iteritems():
                mes2 = "     " + message.encode("utf-8") + "(errcode  %i )" % code + "\n"
                f.writelines("\n")
                f.writelines(mes2)
                mes3 = "     layer: "
                f.writelines(mes3)
                for layer in layerlist:
                    f.writelines(layer.name.encode("utf-8") + "\n")
                    f.writelines("\n")
            f.writelines("\n")
        if analyst["errors"] == {}:
            arcpy.StageService_server(sddraft, sd)
            arcpy.UploadServiceDefinition_server(sd, con)
        else:
            mes4 = analyst["errors"]
            f.writelines(mes4)


# 注册文件夹
def RegisterDataSource(mxdDoc, connFileAgs):
    mxd = arcpy.mapping.MapDocument(mxdDoc)
    dfs = arcpy.mapping.ListDataFrames(mxd)[0]
    lyrs = arcpy.mapping.ListLayers(mxdDoc, "", dfs)
    n = 0
    for each in lyrs:
        paths = arcpy.Describe(each).path
        if paths not in [i[2] for i in arcpy.ListDataStoreItems(connFileAgs, 'FOLDER')]:
            try:
                paths2 = os.path.split(paths)[1].encode('utf-8')
                arcpy.AddDataStoreItem(connFileAgs, "FOLDER", "{}_{}".format(paths2, n), paths, paths)
            except:
                pass
        n += 1
    del mxd


def ModifyService(inmxd, logPath, serviceFolder="test1008", serviceName="newb", serviceType="MapServer",
                  serverName="localhost", serverPort="6080", username="siteadmin", password="siteadmin"):
    serverPort = eval(serverPort)
    outputPath = logPath
    # service = "Scale/test.MapServer"
    service = serviceFolder + "/" + serviceName + "." + serviceType
    logName = "ModifyServicesLog"
    # 初始化实例数范围
    minInstances = "1"
    if cpuCount:
        maxInstances = "{}".format(cpuCount)
    else:
        maxInstances = "4"

    # 防止实例数输入非整型
    try:
        minInstancesNum = int(minInstances)
        maxInstancesNum = int(maxInstances)
    except ValueError:
        messages = "Numerical value not entered for minimum, maximum, or both."
        RunLogWrite(logPath, logName, messages)
        return

    # 防止最小实例数大于最大实例数
    if minInstancesNum > maxInstancesNum:
        messages = "Maximum number of instances must be greater or equal to minimum number."
        RunLogWrite(logPath, logName, messages)
        return

    # 获取登陆口令
    token = getToken(username, password, serverName, serverPort, logPath)
    if token == "":
        messages = "Could not generate a token with the username and password provided."
        RunLogWrite(logPath, logName, messages)
        return

    serviceURL = "/arcgis/admin/services/" + service
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", serviceURL, params, headers)

    # 读取响应
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        messages = "Connect Status is not 200, Could not read service information."
        RunLogWrite(logPath, logName, messages)
        return
    else:
        data = response.read()

        if not assertJsonSuccess(data):
            messages = "Error when reading service information. " + str(data)
            RunLogWrite(logPath, logName, messages)
        else:
            messages = "Service information read successfully. Now changing properties..."
            RunLogWrite(logPath, logName, messages)
        # 读取JSON主体
        dataObj = json.loads(data)
        httpConn.close()
        # 修改服务内容
        dataObj["minInstancesPerNode"] = minInstancesNum
        dataObj["maxInstancesPerNode"] = maxInstancesNum
        # 最大返回记录数
        maxRecordCount = MaxRecordCount(inmxd)
        if maxRecordCount >= 5000 and maxRecordCount <= 200000:
            dataObj["properties"]["maxRecordCount"] = maxRecordCount
        elif maxRecordCount <= 5000:
            dataObj["properties"]["maxRecordCount"] = 5000
        else:
            dataObj["properties"]["maxRecordCount"] = 200000

        # 创建动态工作空间
        if os.path.exists(os.path.join(outputPath, "DynamicDataWorkspaces")):
            if os.path.exists(os.path.join(outputPath, "DynamicDataWorkspaces" + "\\" + "shp")):
                pass
            else:
                try:
                    os.makedirs(os.path.join(outputPath, "DynamicDataWorkspaces" + "\\" + "shp"))
                except:
                    pass

            if os.path.exists(os.path.join(outputPath, "DynamicDataWorkspaces" + "\\" + "raster")):
                pass
            else:
                try:
                    os.makedirs(os.path.join(outputPath, "DynamicDataWorkspaces" + "\\" + "raster"))
                except:
                    pass

        else:
            try:
                os.makedirs(os.path.join(outputPath, "DynamicDataWorkspaces"))
            except:
                pass

            try:
                os.makedirs(os.path.join(outputPath, "DynamicDataWorkspaces" + "\\" + "shp"))
            except:
                pass

            try:
                os.makedirs(os.path.join(outputPath, "DynamicDataWorkspaces" + "\\" + "raster"))
            except:
                pass
        # 若要修改动态工作空间，则仅修改outputPath = logPath即可
        dynamicWP = os.path.join(outputPath, "DynamicDataWorkspaces\\raster")
        dynamicWP1 = os.path.join(outputPath, "DynamicDataWorkspaces\\shp")
        dynamicWP = dynamicWP.replace("\\", "\\\\")
        dynamicWP1 = dynamicWP1.replace("\\", "\\\\")

        # 服务---功能---允许每次请求修改图层顺序和符号
        dataObj["properties"]["enableDynamicLayers"] = "true"
        dataObj["properties"][
            "dynamicDataWorkspaces"] = "[{\"id\":\"DynamicRaster\",\"workspaceFactory\":\"raster\",\"workspaceConnection\":\"DATABASE=%s\"},{\"id\":\"DynamicSHP\",\"workspaceFactory\":\"Shapefile\",\"workspaceConnection\":\"DATABASE=%s\"}]" % (
        dynamicWP, dynamicWP1)

        # 添加工作空间
        # AllFeaturePath(inmxd, dataObj)

        # 修改服务
        updatedSvcJson = json.dumps(dataObj)

        editSvcURL = "/arcgis/admin/services/" + service + "/edit"
        params = urllib.urlencode({'token': token, 'f': 'json', 'service': updatedSvcJson})
        httpConn.request("POST", editSvcURL, params, headers)

        # 查看服务器连接状态
        editResponse = httpConn.getresponse()
        if (editResponse.status != 200):
            httpConn.close()
            return
        else:
            editData = editResponse.read()

            if not assertJsonSuccess(editData):
                pass
            else:
                pass

        httpConn.close()

        return


# 获取mxd文档所有数据框中图层的最大要素数
def MaxRecordCount(inmxd):
    inmxd = arcpy.mapping.MapDocument(inmxd)
    layers = arcpy.mapping.ListLayers(inmxd)
    feaCount = 0
    for each in layers:
        fea = arcpy.Describe(each).featureClass
        fea = fea.catalogPath
        feaCount_temp = arcpy.GetCount_management(fea)
        if feaCount_temp.getOutput(0) >= feaCount:
            feaCount = feaCount_temp.getOutput(0)
        else:
            pass
    del inmxd
    return int(feaCount)


# 获取mxd文档所有数据框中图层的路径（不可以，具体格式要看 新的文件）

# 暂时放弃
def AllFeaturePath(inmxd, dataObj):
    inmxd = arcpy.mapping.MapDocument(inmxd)
    layers = arcpy.mapping.ListLayers(inmxd)
    for each in layers:
        fea = arcpy.Describe(each).featureClass
        fea = fea.catalogPath
        feaPath = os.path.split(fea)[0]
        dataObj["properties"]["dynamicDataWorkspaces"] = feaPath.encode("utf-8") + str(datetime.now())
    del inmxd


# 连接数据库---Oracle
# oracleServer---Oracle Easy Connection( 如 "192.168.31.203/orcl203")
# username,password---Oracle的实例账号密码
def ConnectDataBase(oracleServer, username, password, schema, outputPath):
    outputName = 'oracle.sde'
    DB = 'ORACLE'
    try:
        os.makedirs(outputPath)
    except:
        pass
    finally:
        arcpy.CreateDatabaseConnection_management(outputPath, outputName, DB, oracleServer, "", username, password, "",
                                                  "", schema)


# 开启、停止Server站点中某文件夹的所有服务
def StartorStopAllServices(logPath, logName, folder="Scale", stopOrStart="STart", username="siteadmin",
                           password="siteadmin", serverName="localhost", serverPort="6080", waitTime="5"):
    '''
    注：本脚本不会等待所有服务均开启或关闭后才结束，程序会将命令发送至站点后即结束，服务的开启与关闭由站点自行排序进行。
    具体运行时间受服务数量、正在调用情况及服务器性能影响较大
    受限于GIS站点的稳定性，频繁使用此功能可能会导致难以解决的问题发生
    '''
    waitTime = eval(waitTime)
    serverPort = eval(serverPort)
    if stopOrStart.lower() == "stop":
        stopOrStart = "STOP"
    elif stopOrStart.lower() == "start":
        stopOrStart = "START"
    else:
        messages = "The parameter 'stopOrStart' enterd is not a number of 'START/STOP'"
        RunLogWrite(logPath, logName, messages)
        return

    token = getToken(username, password, serverName, serverPort, logPath)
    if token == "":
        messages = "Could not generate a token with the username and password provided."
        RunLogWrite(logPath, logName, messages)
        return

    if str.upper(folder) == "ROOT":
        folder = ""
        run = "all"
    else:
        folder += "/"
        run = "no"

    folderURL = "/arcgis/admin/services/" + folder
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort, timeout=600)
    httpConn.request("POST", folderURL, params, headers)

    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        messages = "Could not read folder information."
        RunLogWrite(logPath, logName, messages)
        return
    else:
        data = response.read()

        if not assertJsonSuccess(data):
            messages = "Error when reading folder information. " + str(data)
            RunLogWrite(logPath, logName, messages)
        else:
            messages = "Processed folder information successfully. Now processing services..."
            RunLogWrite(logPath, logName, messages)

        dataObj = json.loads(data)
        httpConn.close()

        # 停止根目录下所有服务（不包括子文件夹）
        for item in dataObj['services']:
            fullSvcName = item['serviceName'] + "." + item['type']
            stopOrStartURL = "/arcgis/admin/services/" + folder + fullSvcName + "/" + stopOrStart
            httpConn.request("POST", stopOrStartURL, params, headers)
            stopStartResponse = httpConn.getresponse()

            if (stopStartResponse.status != 200):
                httpConn.close()
                messages = "Error while executing stop or start. Please check the URL and try again."
                RunLogWrite(logPath, logName, messages)
                return
            else:
                stopStartData = stopStartResponse.read()
                if not assertJsonSuccess(stopStartData):
                    if str.upper(stopOrStart) == "START":
                        messages = "Error returned when starting service " + fullSvcName + "."
                        RunLogWrite(logPath, logName, messages)
                    else:
                        messages = "Error returned when stopping service " + fullSvcName + "."
                        RunLogWrite(logPath, logName, messages)

                else:
                    messages = "Service " + fullSvcName + " processed successfully."
                    RunLogWrite(logPath, logName, messages)
            time.sleep(waitTime)
            httpConn.close()

    # 对所有文件夹中的服务进行遍历关闭
    if run == "all":
        for each in dataObj["folders"]:
            if each in ["System", "Utilities"]:
                pass
            else:
                # 停止所有子文件夹中的服务
                # 发送request，获取子文件夹中的服务
                folderURL = "/arcgis/admin/services/" + each
                httpConn.request("POST", folderURL, params, headers)
                response = httpConn.getresponse()
                data = response.read()
                dataObj = json.loads(data)
                httpConn.close()
                # 关闭服务
                for item in dataObj['services']:
                    fullSvcName = item['serviceName'] + "." + item['type']
                    stopOrStartURL = "/arcgis/admin/services/" + each + "/" + fullSvcName + "/" + stopOrStart
                    httpConn.request("POST", stopOrStartURL, params, headers)
                    httpConn.close()
                    time.sleep(waitTime)
    else:
        pass


# 开启或关闭某一个服务
def StartorStopOneServices(logPath, logName, folder, serviceName, stopOrStart="STart", username="siteadmin",
                           password="siteadmin", serverName="localhost", serverPort="6080"):
    serverPort = eval(serverPort)
    # 检测用户输入的是否为"STOP"或"START"
    if stopOrStart.lower() == "stop":
        stopOrStart = "STOP"
    elif stopOrStart.lower() == "start":
        stopOrStart = "START"
    else:
        messages = "The parameter 'stopOrStart' enterd is not START/STOP"
        RunLogWrite(logPath, logName, messages)
        return
    # 检测是否可以正常获取令牌（若失败一般是账户或者密码错误）
    token = getToken(username, password, serverName, serverPort, logPath)
    if token == "":
        messages = "Could not generate a token with the username and password provided."
        RunLogWrite(logPath, logName, messages)
        return
    folderURL = "/arcgis/admin/services/" + folder
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        messages = "Could not read folder information."
        RunLogWrite(logPath, logName, messages)
        return
    else:
        data = response.read()

        if not assertJsonSuccess(data):
            messages = "Error when reading folder information. " + str(data)
            RunLogWrite(logPath, logName, messages)
        else:
            messages = "Processed folder information successfully. Now processing services..."
            RunLogWrite(logPath, logName, messages)
        dataObj = json.loads(data)
        httpConn.close()
        # 开启或者停止某个服务
        stopOrStartURL = "/arcgis/admin/services/" + folder + "/" + serviceName + "/" + stopOrStart
        httpConn.request("POST", stopOrStartURL, params, headers)
        # 获取连接状态
        stopStartResponse = httpConn.getresponse()
        if (stopStartResponse.status != 200):
            httpConn.close()
            messages = "Error while executing stop or start. Please check the URL and try again."
            RunLogWrite(logPath, logName, messages)
            return
        else:
            stopStartData = stopStartResponse.read()

            # 检测返回的数据是否有效
            if not assertJsonSuccess(stopStartData):
                if str.upper(stopOrStart) == "START":
                    messages = "Error returned when starting service " + serviceName + "."
                    RunLogWrite(logPath, logName, messages)
                else:
                    messages = "Error returned when stopping service " + serviceName + "."
                    RunLogWrite(logPath, logName, messages)
            else:
                messages = "Service " + serviceName + " '" + stopOrStart + "'" + " successfully."
                RunLogWrite(logPath, logName, messages)
        httpConn.close()
        return


# =============================发布要素服务从这里开始=============================
def PublishFeatureService(inMxd, outputPath, outputName, con, folderName, serverName, registerDataSource,
                          copy_data_to_server, summary, tags):
    if registerDataSource == True:
        RegisterDataSourceSDE(inMxd, con)
    else:
        copy_data_to_server = True

    try:
        FeatureRegister(inMxd)
    except:
        pass

    # 尝试创建输出目录
    try:
        os.makedirs(outputPath)
    except:
        pass

    # 创建outputPath中的运行日志目录
    logDir = RunLogDirs(outputPath)

    # 判断outputPath是否存在可用
    if os.path.exists(outputPath):
        pass
    else:
        messages = "The directory of output is not exists"
        RunLogWrite(logDir, outputName, messages)
        return

    # 到这了
    sdDraft = os.path.join(outputPath, outputName + ".sddraft")
    newSDdraft = 'updatedDraft.sddraft'
    SD = os.path.join(outputPath, outputName + ".sd")

    try:
        # 创建服务定义文件
        analysis = arcpy.mapping.CreateMapSDDraft(inMxd, sdDraft, serverName, 'ARCGIS_SERVER', con, copy_data_to_server,
                                                  folderName, summary, tags)
        # 读取sddraft文件
        doc = DOM.parse(sdDraft)

        # 修改xml的文档
        typeNames = doc.getElementsByTagName('TypeName')
        for typeName in typeNames:
            if typeName.firstChild.data == 'FeatureServer':
                typeName.parentNode.getElementsByTagName('Enabled')[0].firstChild.data = 'true'

        f = open(newSDdraft, 'w')
        doc.writexml(f)
        f.close()
        analysis = arcpy.mapping.AnalyzeForSD(newSDdraft)
        for key in ('messages', 'warnings', 'errors'):
            vars = analysis[key]
            for ((message, code), layerlist) in vars.iteritems():
                pass
                for layer in layerlist:
                    pass
                pass

        if analysis['errors'] == {}:
            arcpy.StageService_server(newSDdraft, SD)
            arcpy.UploadServiceDefinition_server(SD, con)
            txtFile = open(outputPath + '/{}-log.txt'.format(outputName), "a")
            txtFile.write(str(datetime.now()) + " | " + "Uploaded and publish service" + "\n")
            txtFile.close()

        else:
            txtFile = open(outputPath + '/{}-log.txt'.format(outputName), "a")
            txtFile.write(str(datetime.now()) + " | " + analysis['errors'] + "\n")
            txtFile.close()

    except:
        # Write messages to a Text File
        txtFile = open(outputPath + '/{}-log.txt'.format(outputName), "a")
        txtFile.write(str(datetime.now()) + " | Last Chance Message:" + arcpy.GetMessages() + "\n")
        txtFile.close()


# 创建服务连接(ags)
def CreateServerConnect(outputPath, outputName, serverHost="localhost", serverPort="6080", username="siteadmin",
                        password="siteadmin"):
    pubDir = os.path.join(outputPath, "GISServerConnect")
    try:
        os.makedirs(pubDir)
    except:
        pass
    serverConnName = outputName + ".ags"
    arcpy.mapping.CreateGISServerConnectionFile("ADMINISTER_GIS_SERVICES", pubDir, serverConnName,
                                                "http://{}:{}/arcgis/admin".format(serverHost, serverPort),
                                                "ARCGIS_SERVER", "", "", username, password, "SAVE_USERNAME")

    # 创建服务连接
    con = os.path.join(pubDir, serverConnName)
    return con


# 注册sde
def RegisterDataSourceSDE(mxdDoc, connFileAgs):
    mxd = arcpy.mapping.MapDocument(mxdDoc)
    dfs = arcpy.mapping.ListDataFrames(mxd)[0]
    lyrs = arcpy.mapping.ListLayers(mxdDoc, "", dfs)
    n = 0
    for each in lyrs:
        paths = arcpy.Describe(each).path
        if paths not in [i[2] for i in arcpy.ListDataStoreItems(connFileAgs, 'DATABASE')]:
            try:
                paths2 = os.path.split(paths)[1].encode('utf-8')
            except:
                pass

            try:
                arcpy.AddDataStoreItem(connFileAgs, "DATABASE", "{}_{}".format(paths2, datetime.now()), paths, paths)
            except:
                pass
        n += 1
    del mxd


# 注册要素版本
def FeatureRegister(inmxd):
    mxd = arcpy.mapping.MapDocument(inmxd)
    dfs = arcpy.mapping.ListDataFrames(mxd)
    for df in dfs:
        dataList = arcpy.mapping.ListLayers(df)
        for each in dataList:
            arcpy.RegisterAsVersioned_management(each, "EDITS_TO_BASE")


# 删除服务
def DeleteService(logPath, logName, folder, servicecName, serviceType, username="siteadmin", password="siteadmin",
                  serverName="localhost", serverPort="6080"):
    serverPort = eval(serverPort)

    token = getToken(username, password, serverName, serverPort, logPath)
    if token == "":
        messages = "Could not generate a token with the username and password provided."
        RunLogWrite(logPath, logName, messages)
        return

    # 创建连接
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"

    folderURL = "/arcgis/admin/services/" + folder + "/" + servicecName + "." + serviceType
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)

    # 读取reponse,查看服务状态是否正常
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        messages = "Delete service field, connect to ArcGIS Server site field, status code is not 200."
        RunLogWrite(logPath, logName, messages)
        return
    else:
        data = response.read()
        # 确认返回数据有效
        if not assertJsonSuccess(data):
            messages = "Error when reading folder information. " + str(data)
            RunLogWrite(logPath, logName, messages)
        else:
            messages = "Processed folder information successfully. Now processing services..."
            RunLogWrite(logPath, logName, messages)

        httpConn.close()
        delService = folderURL + "/" + "delete"
        httpConn.request("POST", delService, params, headers)
        httpConn.close()
    return


'''
预设运行模式：
0 —— 从shp、要素类发布MapServer
1 —— 从mxd发布MapServer
2 —— 发布FeatureServer
3 —— 修改服务
4 —— 删除服务
5 —— 启动、停止所有服务
6 —— 启动、停止某个服务
'''
runmode = "5"

# # ============================= 由 Shp 发布 MapServer 服务调用区域 ==========================================
if runmode == "0":
    '''
    inFea = [r"F:\alun\一张图\服务自动发布\plg.shp", r"F:\alun\一张图\服务自动发布\pnt.shp", r"F:\alun\一张图\服务自动发布\ply.shp"]                                                    # inFea --- 传入全路径数据列表,只有一个也传列表
    outputPath = r"F:\alun\一张图\服务自动发布\运行模式0"            # outputPath --- 临时Layer输出路径
    tempMxd = r"F:\alun\一张图\服务自动发布\运行模式0\temp.mxd"
    outputName = "创建mxd"
    ## 3、由创建的mxd发布Server
    serviceName = "AutoPublish_MapServer_555"                       # serviceName --- 发布出去的服务的名称
    copy_data_to_server = "True"                                    # copy_data_to_server --- 是否将数据复制包服务器
    folder_name = "AutoMapServer"                                   # folder_name --- 发布出去的服务的文件夹
    ### summary/tags --- 服务的简介及标签
    summary = ''
    serverHost = "192.168.80.186"                                   # serverHost --- Server服务器的主机名称或者ip地址
    serverPort = "6080"                                             # serverPort --- Server服务器的端口
    username = "siteadmin"                                          # username/password --- Server站点的账户及密码
    password = "siteadmin"
    registerDataSource = "False"                                    # registerDataSource --- 是否将数据源注册到服务器
    serviceType = "MapServer"                                       # serviceType --- 服务类型，用于ModifyService
    '''
    inFea = sys.argv[1]
    tempMxd = sys.argv[2]
    folder_name = sys.argv[3]
    serviceName = sys.argv[4]
    serviceType = sys.argv[5]
    summary = sys.argv[6]
    serverHost = sys.argv[7]
    serverPort = sys.argv[8]
    username = sys.argv[9]
    password = sys.argv[10]
    outputPath = sys.argv[11]
    outputName = sys.argv[12]

    tags = ""
    copy_data_to_server = "True"
    registerDataSource = "False"
    copy_data_to_server = eval(copy_data_to_server)
    ## *数据编码
    outputPath = YZT_CodingJudge(outputPath)
    ### 函数调用
    inLayer = MakeLayers(inFea, outputPath)
    tempMxd = YZT_CodingJudge(tempMxd)  # *数据编码
    outputName = YZT_CodingJudge(outputName)
    ### 调用
    inmxd = MakeMxd(inLayer, tempMxd, outputPath, outputName)
    ### 内部修改
    registerDataSource = eval(registerDataSource)
    inmxd = YZT_CodingJudge(inmxd)
    outputPath = YZT_CodingJudge(outputPath)
    outputName = YZT_CodingJudge(outputName)
    # 函数调用
    PublishMxdToServer(inmxd, outputPath, outputName, serviceName, copy_data_to_server, folder_name, summary, tags,
                       serverHost, serverPort, username, password, registerDataSource)

    ## 4、修改服务参数 --- 最大实例数（根据CPU核数，支持超线程则为线程数）
    ModifyService(inmxd, outputPath, folder_name, serviceName, serviceType, serverHost, serverPort, username, password)
# # ============================= 由 Shp 发布 MapServer 服务调用区域 ==========================================


# # ============================= 由 Mxd 发布 MapServer 服务调用区域 ==========================================
if runmode == "1":
    '''
    ## 由创建的mxd发布Server
	### inmxd --- 输入的Mxd文件
    inmxd = r"F:\alun\一张图\服务自动发布\mxdDemo_100.mxd"
    ### folder_name --- 发布出去的服务的文件夹
    folder_name = "AutoMapServer"
    ### serviceName --- 发布出去的服务的名称
    serviceName = "AutoPublish_MapServer_1"
    ### serviceType --- 服务类型，用于ModifyService
    serviceType = "MapServer"
    ### summary/tags --- 服务的简介及标签
    summary = ''
    tags = "arcpy; ArcGIS Server; AutPublish"
    ### serverHost --- Server服务器的主机名称或者ip地址
    serverHost = "localhost"
    ### serverPort --- Server服务器的端口
    serverPort = "6080"
    ### username/password --- Server站点的账户及密码
    username = "siteadmin"
    password = "siteadmin"
    ### outputPath/outputName =
    outputPath = r"F:\alun\一张图\服务自动发布"
    outputName = r"Mxd发布服务"
    ### copy_data_to_server --- 是否将数据复制包服务器
    copy_data_to_server = "True"
    ### registerDataSource --- 是否将数据源注册到服务器
    registerDataSource = "False"
    '''
    inmxd = sys.argv[1]
    folder_name = sys.argv[2]
    serviceName = sys.argv[3]
    serviceType = sys.argv[4]
    summary = sys.argv[5]
    serverHost = sys.argv[6]
    serverPort = sys.argv[7]
    username = sys.argv[8]
    password = sys.argv[9]
    outputPath = sys.argv[10]
    outputName = sys.argv[11]

    ### 内部修改
    copy_data_to_server = "True"
    registerDataSource = "False"
    tags = "arcpy; ArcGIS Server; AutPublish"
    copy_data_to_server = eval(copy_data_to_server)
    registerDataSource = eval(registerDataSource)
    inmxd = YZT_CodingJudge(inmxd)
    outputPath = YZT_CodingJudge(outputPath)
    outputName = YZT_CodingJudge(outputName)
    # 函数调用
    PublishMxdToServer(inmxd, outputPath, outputName, serviceName, copy_data_to_server, folder_name, summary, tags,
                       serverHost, serverPort, username, password, registerDataSource)

    ## 修改服务参数 --- 最大实例数（根据CPU核数，支持超线程则为线程数）
    ModifyService(inmxd, outputPath, folder_name, serviceName, serviceType, serverHost, serverPort, username, password)

# # ============================= 由 Mxd 发布 MapServer 服务调用区域 ==========================================


# # ============================= 发布要素服务调用区域 ==========================================
# elif runMode == "3":
#     # 创建server连接
#     con = CreateServerConnect("D:/4/newAGS", "feaServer")
#     # 打开mxd文件
#     outputPath = 'D:/4/feaTest'
#     inMxd = "D:/4/mxd2.mxd"
#
#     # 输入其他参数
#     folderName = "FeaTest1009"
#     outputName = 'KYEM'
#     serverName = "Feafea"
#
#     summary = 'fire point by County'
#     tags = 'county, counties, population, density, census'
#
#     registerDataSource = True
#     copy_data_to_server = False
#
#     PublishFeatureService(inMxd, outputPath, outputName, con, folderName, serverName, registerDataSource,
#                           copy_data_to_server)
#
# # ============================= 发布要素服务调用区域 =============================


# # ============================= 删除服务调用区域 ==========================================
if runmode == "4":
    logPath = r"D:\logpath"
    logName = "删除服务的运行日志"
    '''
    folder = "YZT_Test"
    servicecName = "YZT_Intersect"
    serviceType = "MapServer"
    username = "siteadmin"
    password = "siteadmin"
    serverName = "192.168.80.186"
    serverPort = "6080"
    '''
    folder = sys.argv[1]
    servicecName = sys.argv[2]
    serviceType = sys.argv[3]
    username = sys.argv[4]
    password = sys.argv[5]
    serverName = sys.argv[6]
    serverPort = sys.argv[7]

    logPath = YZT_CodingJudge(logPath)
    logName = YZT_CodingJudge(logName)
    DeleteService(logPath, logName, folder, servicecName, serviceType, username, password, serverName, serverPort)
# # ============================= 删除服务调用区域 ==========================================


# # ============================= 开启或停止所有服务调用区域 ==========================================
# 开启或停止Server站点中某文件夹的所有服务/ 若文件夹设置为root，则关闭除了system及utilities外的其他所有服务
if runmode == "5":
    logPath = r"D:\logpath"  # 运行日志存放目录
    outputName = "RunTest20190929"  # 输出日志的名称
    folder = "modifytest"  # 服务文件夹名
    # folder = "root"                     # 服务文件夹名
    stopOrStart = "start"  # 开启或关闭，"start" "stop"
    username = "siteadmin"  # server站点账户
    password = "siteadmin"  # server站点密码
    serverHost = "192.168.31.101"  # 站点ip
    serverPort = "6080"  # 站点端口
    waitTime = "5"  # 单位秒，开启或关闭每个服务的等待时间，此值设置小于5可能会造成大量服务操作失败

    '''
    logPath = sys.argv[1] 
    outputName = sys.argv[2] 
    folder = sys.argv[3] 
    stopOrStart = sys.argv[4] 
    username = sys.argv[5]
    password = sys.argv[6]
    serverHost = sys.argv[7] 
    serverPort = sys.argv[8]
    waitTime = sys.argv[9]
    '''

    logPath = YZT_CodingJudge(logPath)
    # 检测运行日志是否存在，若不存在则创建
    runLogDir = RunLogDirs(logPath)
    StartorStopAllServices(logPath, outputName, folder, stopOrStart, username, password, serverHost, serverPort,
                           waitTime)
# # ============================= 开启或停止所有服务调用区域 ==========================================


# # ============================= 开启或停止单个服务调用区域 ==========================================
# 开启或停止Server站点中某文件夹的所有服务/ 若文件夹设置为root，则关闭除了system及utilities外的其他所有服务
if runmode == "6":
    '''
    logPath = r"D:\logpath"             # 运行日志存放目录
    outputName = "RunTest20190929"      # 输出日志的名称
    # folder = "AutoMapServer"          # 服务文件夹名
    folder = "test"                     # 服务文件夹名
    serviceName = "qqq"                 # 服务文件夹名
    serviceType = "MapServer"           # 服务文件夹名
    stopOrStart = "start"               # 开启或关闭，"start" "stop"
    username = "siteadmin"              # server站点账户
    password = "siteadmin"              # server站点密码
    serverHost = "192.168.31.101"       # 站点ip
    serverPort = "6080"                 # 站点端口

    '''
    logPath = sys.argv[1]
    outputName = sys.argv[2]
    folder = sys.argv[3]
    serviceName = sys.argv[4]
    serviceType = sys.argv[5]
    stopOrStart = sys.argv[6]
    username = sys.argv[7]
    password = sys.argv[8]
    serverHost = sys.argv[9]
    serverPort = sys.argv[10]

    logPath = YZT_CodingJudge(logPath)
    # 检测运行日志是否存在，若不存在则创建
    runLogDir = RunLogDirs(logPath)
    # 开启或停止Server站点中某个服务
    # serviceName必须为字符串形式的 "服务名.服务类型"，必须有.服务类型
    serviceName = serviceName + "." + serviceType
    StartorStopOneServices(logPath, outputName, folder, serviceName, stopOrStart, username, password, serverHost,
                           serverPort)
# # ============================= 开启或停止单个服务调用区域 ==========================================


# #
# # # RunTestArea       =================================================================================
# # 创建工作目录      ParatersArea 1
# logPath = r"D:\2\mxd"
# runLogDir = RunLogDirs(logPath)
# # 由矢量数据创建图层文件，会自动创建一个LyrTemp文件夹用于存放lyr文件
# # inFea = [r"D:\2\data\tempPolygon.shp", r"D:\2\data\tempPolyline.shp", r"D:\2\data\tempPoints.shp", r"D:\2\data\tempMPoints.shp"]
# inFea = [r"D:\2\data\Polygon_Small.shp", r"D:\2\data\Points.shp", r"D:\2\data\Polyline.shp", r"D:\2\data\Polygon_Huge.shp"]
# outputPath = runLogDir
#
# tempMxd = r"D:\2\data\temp_102.mxd"
# outputName = "RunTest20190929"
#
# # 由函数MakeMxd()，创建的mxdTemp文件夹中有另存出来的mxd文件
# tempMxdDir = os.path.join(outputPath, "mxdTemp")
# tempMxds = os.path.join(tempMxdDir, outputName + ".mxd")
#
# # 发布服务参数区   ParametersArea 3
#
# # 输入mxd文件路径     use in 3、4、5
# inmxd = tempMxds
#
# # 创建的服务的名称
# serviceName = "AutoPublish_test"
#
# # 是否将mxd中的数据复制到服务器中 True/False
# copy_data_to_server = False
#
# # 设置要发布到的文件夹，若不存在则创建
# folder_name = "CeShiYiXIa22"
#
# # 服务的摘要
# # summary = '''
# #  这个服务是用脚本自动创建的
# #  创建时间是{}
# #  '''.format(datetime.datetime.now())
# summary = '''
#  这个服务是用脚本自动创建的
#  创建时间是{}
#  '''.format(datetime.now())
#
# # 服务的标签
# tags = "arcpy; ArcGIS Server; AutPublish"
# serverHost = "localhost"
# serverPort = "6080"
# username = "siteadmin"
# password = "siteadmin"
# registerDataSource = True
#
# # 服务类型，用于ModifyService
# serviceType="MapServer"
#
# # 开启或关闭服务，用于StartorStopAllServices/StartorStopOneServices
# stopOrStart="STart"
#
# # 创建数据库连接
# # oracleServer = '192.168.31.203/orcl203'
# # username = 'sdexh'
# # password = 'sdexh'
# # schema = 'SDEXH'
#
#
# # 预设的程序运行模式 runMode
# # "0" ---由shp创建mxd并进行发布
# # "1" ---直接使用制作完成的mxd进行发布
# # "2" ---检测所有目录中是否有服务处于停止状态
# # "3" ---
# # "4" ---启动或停止Server站点中某个文件夹中的所有服务
# # "5" ---启动或停止Server站点中某个服务
#
# runMode = "1"
#
# # 最终执行区     'RunArea'
#
#
# # 通过shp文件制作mxd并进行发布
# if runMode == "0":
#     inLayer = MakeLayers(inFea, outputPath)
#     MakeMxd(inLayer, tempMxd, outputPath, outputName)
#     PublishMxdToServer(inmxd, outputPath, outputName, serviceName, copy_data_to_server, folder_name, summary, tags, serverHost, serverPort, username, password, registerDataSource)
#
#
# # 直接传入制作好的mxd文件，将mxd发布为服务
# if runMode == "1":
#     PublishMxdToServer(inmxd, outputPath, outputName, serviceName, copy_data_to_server, folder_name, summary, tags, serverHost, serverPort, username, password, registerDataSource)
#     runMode = "2"
#
#
# # 修改服务属性--- 最大实例数（根据CPU核数，支持超线程则为线程数）、
# if runMode == "2":
#     ModifyService(inmxd, logPath, serverHost, serverPort, username, password, folder_name, serviceName, serviceType)
#
#
# # 开启或停止Server站点中某文件夹的所有服务
# if runMode == "4":
#     StartorStopAllServices(logPath, outputName, folder_name, stopOrStart, username, password, serverHost, serverPort)
#
#
# # 开启或停止Server站点中某个服务
# # serviceName必须为字符串形式的 "服务名.服务类型"，必须有.服务类型
# if runMode == "5":
#     serviceName = serviceName + "." + serviceType
#     StartorStopOneServices(outputPath, outputName, folder_name, serviceName, stopOrStart, username, password, serverHost, serverPort, summary, tags)

# '''
# 程序特点：
# 1、若发布的服务所在文件夹及服务名称均相同则后发服务会覆盖之前发布过的服务；
# 2、服务修改会默认将最小实例数设置为1，最大实例数设置为CPU核数（若CPU支持超线程技术则为线程数，如4核8线程则为8）；
# 3、
# '''

# # 将  发布要素服务new---检测服务状态并入即可






