import openpyxl
import os
import json


def xlsxToJson(xlsx, outJson):
    wb = openpyxl.load_workbook(xlsx)
    sht = wb.active

    # start from 1
    maxCol = sht.max_column

    keyList = []
    resJson = {"ATTR": []}
    for i, eachRow in enumerate(sht.rows):
        # convert excel header to key
        if i == 0:
            print(eachRow)
            for colNum in range(maxCol):
                keyList.append(eachRow[colNum].value)
        else:
            attrJson = {}
            for colNum in range(maxCol):
                attrJson[keyList[colNum]] = eachRow[colNum].value
            resJson["ATTR"].append(attrJson)

    print(keyList)
    print(resJson)

    with open(outJson, "w", encoding="utf-8") as f:
        json.dump(resJson, f, ensure_ascii=False, indent=4)
        # json.dump(resJson, f, ensure_ascii=False)



xlsx = r"F:\工作项目\项目_温州超图\任务_分层分户\数据进超图\excel\floor_split_white.xlsx"
outJson = r"F:\工作项目\项目_温州超图\任务_分层分户\数据进超图\json\floor_split_formatted.json"
xlsxToJson(xlsx, outJson)