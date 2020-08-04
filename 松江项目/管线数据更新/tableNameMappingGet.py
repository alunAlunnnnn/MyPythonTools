import re


def GetNewTableName(data):
    resDic = {}
    with open(data, "r", encoding="utf-8") as f:
        lines = f.readlines()
        i = 0
        for each in lines:
            reTabName = None
            reTabNameNew = None

            # match OldTableName
            reTabNameCom = re.compile(r"T\d+")
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


data = r'D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\松江项目\管线数据更新\20200330工具提交升级\20200330工具提交\data\tablename.txt'
print(GetNewTableName(data))