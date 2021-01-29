import psycopg2
import json


def selectJMLable(host, port, username, password, dbname, tableName):
    conn = psycopg2.connect(host=host, port=port, user=username, password=password, dbname=dbname)
    cur = conn.cursor()

    cur.execute(f"select * from {tableName};")
    data = cur.fetchall()

    conn.commit()
    conn.close()

    return data


def data2json(data, outputFile):
    print(data)
    totalList = []
    for eachRow in data:
        eachDict = {}

        eachDict["coordinates"] = [float(eachRow[7]), float(eachRow[8])]
        eachDict["id"] = eachRow[13]
        eachDict["SCALE"] = eachRow[10]
        eachDict["HEIGHT"] = float(eachRow[9])
        eachDict["TYPE"] = ""
        eachDict["NAME"] = eachRow[12]
        eachDict["XZQ_SQ"] = eachRow[2]
        eachDict["XZQ_QX"] = eachRow[3]
        eachDict["XZQ_JD"] = eachRow[4]

        totalList.append(eachDict)

    print(totalList)

    with open(outputFile, "w", encoding="utf-8") as f:
        json.dump(totalList, f, ensure_ascii=False, indent=4)


def main(host, port, username, password, dbname, tableName, outputFile):
    data = selectJMLable(host, port, username, password, dbname, tableName)

    data2json(data, outputFile)


host = "192.168.31.128"
port = "5432"
username = "postgres"
password = "0403"
dbname = "ZGJDB"
tableName = "jmlabel"
outputFile = r"F:\工作项目\项目_温州超图\sql_建表建库\数据_重点建筑pg转json\jmlabel.json"

main(host, port, username, password, dbname, tableName, outputFile)
