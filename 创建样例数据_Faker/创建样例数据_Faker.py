from faker import Faker
import numpy as np
import pandas as pd
import random

f = Faker(locale="zh_CN")

nId = np.arange(10)
print(nId)

sId = pd.Series(nId)
nIdTup = nId.tolist()

nameList = []
ageList = []
addressList = []
jobList = []
salList = []
bonusList = []
salNumList = []
for i in range(10):
    nameList.append(f.name())
    ageList.append(random.randint(15, 45))
    addressList.append(f.address())
    jobList.append(f.job())
    salList.append(random.randint(35, 125) * 100)
    bonusList.append(random.randint(15, 70) * 40)
    salNumList.append(random.randint(10, 16))
dataList = [nId, nameList, ageList, addressList, jobList, salList, bonusList, salNumList]

columns = ["姓名", "年龄", "地址", "工作", "薪水", "奖金", "薪水月数"]
col = [nameList, ageList, addressList, jobList, salList, bonusList, salNumList]
datas = list(zip(nameList, ageList, addressList, jobList, salList, bonusList, salNumList))
print(datas)
dataDict = {columns[i]: col[i] for i, each in enumerate(columns)}
dataArray = np.array(dataList)
print(dataDict)
df = pd.DataFrame(dataDict)
df.columns = ["姓名", "年龄", "地址", "工作", "薪水", "奖金", "薪水月数"]
print(df)
df.to_excel("./data/data.xlsx", index=False)
