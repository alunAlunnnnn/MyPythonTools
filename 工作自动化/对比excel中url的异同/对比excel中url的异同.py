import pandas as pd
import openpyxl


class valueMatchError(Exception):
    pass


def _getDataFromXLSX(inXlsxFile: str, sheetName: str) -> dict:
    wb = openpyxl.load_workbook(inXlsxFile)
    sht = wb[sheetName]
    cols = [eachCol for eachCol in sht.columns if
            eachCol[0].value == "服务名" or eachCol[0].value == "服务类型" or eachCol[0].value == "url"]

    tempList = []
    for i, eachCol in enumerate(cols):
        data = [eachData.value for j, eachData in enumerate(eachCol) if j > 0]
        serviceName = []
        # 第一列 —— 服务名，去除因为合并单元格后出现的None值
        if i == 0:
            # 第一列的每一行，搜寻 None 值
            for k, each in enumerate(data):
                # 找到 None 值，并且保证不是在开头
                if each is None and k != 0:
                    newSerName = None
                    # 获取从 k 开始往前的 第一个非空值，作为服务名
                    for l in range(k - 1, -1, -1):
                        if data[l] is not None:
                            newSerName = data[l]
                            break
                else:
                    newSerName = each

                serviceName.append(newSerName)
        else:
            serviceName = data

        tempList.append(serviceName)

    resList = list(zip(*tempList))
    print(resList)
    resDict = {}
    for i, eachKey in enumerate(tempList[0]):
        tmpDict = {}
        resDict.setdefault(eachKey, {})
        tmpDict[resList[i][1]] = resList[i][2]
        resDict[eachKey].update(tmpDict)
    return resDict


def _compareData(dataOri: dict, dataTar: dict):
    for eachSer, eachValue in dataOri.items():
        tarDict = dataTar.get(eachSer, None)

        # 可能存在新服务在原来表中未统计的情况
        if tarDict is not None:
            # 新服务表中，某服务的各种类型服务
            for i, (oriType, oriUrl) in enumerate(eachValue.items()):
                tarUrl = tarDict.get(oriType, None)

                # 确保服务类型在老表中存在
                if tarUrl is not None:
                    comTarUrl = tarUrl[20:]
                    comOriUrl = oriUrl[21:]
                    print("tar:", comTarUrl)
                    print("ori:", comOriUrl)


inXlsxFileOri = r"./data/松江客户发布服务url(1).xlsx"
inXlsxFileTar = r"./data/松江管廊服务url及对应关系_20201113.xlsx"
sheetName = "二维服务"
resOri = _getDataFromXLSX(inXlsxFileOri, sheetName)
resTar = _getDataFromXLSX(inXlsxFileTar, sheetName)

print(resOri)
print(resTar)


_compareData(resOri, resTar)