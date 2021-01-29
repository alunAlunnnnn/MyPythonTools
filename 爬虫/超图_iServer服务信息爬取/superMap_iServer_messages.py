import requests
import os
import re
from bs4 import BeautifulSoup
import json


def parseHtml(data, singleDict):
    global resList, resDict
    # reObj = re.search(r"setting = \{[\w \"-/:[{\],\}\\]*;", data)
    reObj = re.search(r"setting = {\"isStreamingService\".*", data)
    try:
        data = reObj.group(0)[10:-2]
        # data = reObj.group(0)
        print(data)
        dataDict = json.loads(data)
        serviceProvider = dataDict["providers"]

        for eachProvider in serviceProvider:
            try:
                providerName = eachProvider["spSetting"]["name"]
                try:
                    prividerPath = eachProvider["spSetting"]["config"]["workspacePath"]
                except:
                    prividerPath = eachProvider["spSetting"]["config"]["configFile"]
                print(providerName, prividerPath)
                singleDict["name"] = providerName
                singleDict["data_path"] = prividerPath
                resList.append(singleDict)
            except:
                pass

        resDict["datas"] = resList
        print(resDict)
    except:
        pass


def getHtml(url, cookie, outputPath, outputName):
    header = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": cookie
    }

    res = requests.get(url, headers=header)
    if res.status_code == 200:
        htmlText = res.text
    else:
        htmlText = "None"

    with open(os.path.join(outputPath, outputName), "w", encoding="utf-8") as f:
        f.write(htmlText)

    return htmlText, os.path.join(outputPath, outputName)


def getServicesUrl(restUrl, cookie, outputPath, outputName):
    data, _ = getHtml(restUrl, cookie, outputPath, outputName)
    soup = BeautifulSoup(data, "lxml")
    urlList = []
    for each in soup.find_all('a'):
        try:
            href = each["href"]
            # print(href)
            if "/rest" in href:
                # print(href)
                urlList.append(href)
        except:
            pass

    return urlList


def requestAllUrl(urlList, outputPath, cookie):
    for eachUrl in urlList:
        singleDict = {}
        # print(eachUrl)
        list1 = eachUrl.split("/")[:-1]
        list1.insert(4, "manager")
        url = "/".join(list1)
        print(url)

        outputName = eachUrl.split("/")[-2] + ".html"
        print(outputName)

        singleDict["url"] = url

        data, _ = getHtml(url, cookie, outputPath, outputName)

        # try:
        #     parseHtml(data)
        # except:
        #     pass

        parseHtml(data, singleDict)


def main(restUrl, cookie, outputPath, outputName):
    urlList = getServicesUrl(restUrl, cookie, outputPath, outputName)
    print(urlList)
    requestAllUrl(urlList, outputPath, cookie)


# url = r"http://192.168.10.244:8090/iserver/manager/services/3D-BinJiangJieDao"
url = r"http://192.168.10.244:8090/iserver/services"
outputPath = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\爬虫\超图_iServer服务信息爬取\数据\iServer_Manager"
outputName = r"test.html"
cookie = "JSESSIONID=88CDC19684CA5BFCDCA26D84F83AD154; rememberMe=r4lPv14Myti3XCEe+Xxkotxsbpb4IbNAkvCHfdlEJqIaZlYRXGS85j0Qd0aCkWtJrL29TLhhZjQXkM+/fb1QVSaej66l9AxbFnqnVQ2sJImhJslgCeyx2eiyXnh5kIey37oSilLNgSUcqae4WlOerNEhayXLzFL2JrpJizP9Qsge8ROuI4bFC1sG8FDm6w/tLyUfSdWzRu4+2w6o+Ti+4Cq1GmzRSci29jqAsfJRD60nMlG+G9SYUK4BfNBlitUe/iK5xN5JJhC6wsV/1IDlK1TqZs5w3AIFAJAhYJXc8vOHUFWNJpXb0bBWf9JS8wJBYeuLJnqYvrkU/EaIy4qYg5nnjI7VNWk9ORPoLMgw/vn2mN57kvxu0n1EA7EKGvFZsN91PIJGwgqEzvsli4SPmrwxupC6V4sFCFvZybRQUmsA99PhEAlF3Mc0gvI8ToA3w1UznVV0bb2slIxjRv+ouv27JQqemq19Tick1GXrUmU3iJvqXfvfaRB++XucnuLM8TqVEZYb2amxPmY7GqA="
resDict = {}
resList = []

main(url, cookie, outputPath, outputName)

print(resDict)
