import re
import json

outHtml = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\爬虫\超图_iServer服务信息爬取\数据\iServer_Manager\3D-local3DCache-RoughModelHighv3RoughModelv3.html"
outHtml = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\爬虫\超图_iServer服务信息爬取\数据\iServer_Manager\3D-local3DCache-RoughModelLowv3RoughModelv3.html"

with open(outHtml, "r", encoding="utf-8") as f:
    data = f.read()

def parseHtml(data):
    # reObj = re.search(r"setting = \{\"[\w \"-/:\[{\],\}\\]*?;", data)
    reObj = re.search(r"setting = {\"isStreamingService\".*", data)
    # reObj = re.search(r"setting = \{[\w \"]*;", data)
    # reObj = re.search(r"setting = \{[\w \"-/:[{\],\}\\]*\]\};", data)
    data = reObj.group(0)[10:-1]

    dataDict = json.loads(data)

    serviceProvider = dataDict["providers"]
    print(serviceProvider)
    for eachProvider in serviceProvider:
        providerName = eachProvider["spSetting"]["name"]
        try:
            prividerPath = eachProvider["spSetting"]["config"]["workspacePath"]
        except:
            prividerPath = eachProvider["spSetting"]["config"]["configFile"]
        print(providerName, prividerPath)

parseHtml(data)