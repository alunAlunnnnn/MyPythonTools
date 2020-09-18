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
            reTabNameCom = re.compile(r"T\d*")
            reTabNameMo = reTabNameCom.search(each)
            if reTabNameMo:
                reTabName = reTabNameMo.group()

            # match NewTableName
            reTabNameNewCom = re.compile(r"\w*_\w*_\w")
            reTabNameNewMo = reTabNameNewCom.search(each)
            if reTabNameMo:
                reTabNameNew = reTabNameNewMo.group()

            resDic[reTabName] = reTabNameNew
            i += 1
    return resDic

tabNameTxt = r"D:\gxce\tablename.txt"
res = GetNewTableName(tabNameTxt)
print(res)