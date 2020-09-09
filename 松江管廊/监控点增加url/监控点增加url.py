import json
import os
data = r"E:\松江管廊\新数据0805\监控点\JSON\设备json"


os.chdir(data)
print(os.getcwd())

for eachData in os.listdir(data):
    with open(eachData, encoding="utf-8") as f:
        data = f.read()
        dataList = json.loads(data)["data"]
        for i, eachJson in enumerate(dataList):
            codes = eachJson["code"]
            url = eachJson["images"]
            print(eachData, codes, url)
            # if codes == None:
            #     print(eachData, i, url)


