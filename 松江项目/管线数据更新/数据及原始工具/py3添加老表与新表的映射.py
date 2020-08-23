import re, sys
data = "D:/tablename.txt"
resDic = {}
with open(data, "r", encoding="utf-8") as f:
    lines = f.readlines()
#     print(lines)
    i = 0
    for each in lines:
        reTabName = None
        reTabNameNew = None
#         print(each)
        # 匹配老表名
        reTabNameCom = re.compile(r"T\d*")
        reTabNameMo = reTabNameCom.search(each)
        if reTabNameMo:
            reTabName = reTabNameMo.group()
            
        # 匹配新表明
#         reTabNameNewCom = re.compile(r"[A-Z]*_[A-Z]*_[A-Z]")
        reTabNameNewCom = re.compile(r"\w*_\w*_\w")
        reTabNameNewMo = reTabNameNewCom.search(each)
        if reTabNameMo:
            reTabNameNew = reTabNameNewMo.group()
            
            
#         print("原表名是：", reTabName)
#         print("新表名是：", reTabNameNew)
        resDic[reTabName] = reTabNameNew
        i += 1
print(resDic)
with open("D:/tableNameMapping.txt", "w") as f:
    f.write(str(resDic))
    