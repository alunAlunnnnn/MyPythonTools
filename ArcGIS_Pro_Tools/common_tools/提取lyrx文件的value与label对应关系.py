import os
import datetime
import functools
import json


# import arcpy


def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        print(f"Method {func.__name__} start running ! ")
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        end = datetime.datetime.now()
        cost = end - start
        print("*" * 30)
        print(f"Method {func.__name__} start at {start}")
        print(f"Method {func.__name__} finish at {start}")
        print(f"Method {func.__name__} total cost {cost}")
        print("*" * 30)
        return res

    return _wrapper


@getRunTime
def copyLyrx2Txt(lyrx):
    if "\\" in lyrx:
        print(1)
        dirName = os.path.dirname(lyrx)
        baseName = os.path.basename(lyrx)
        tarFileName = baseName.split(".lyrx")[0]
    else:
        print(2)
        dirName = ""
        tarFileName = lyrx.split(".lyrx")[0]

    decFile = os.path.join(dirName, tarFileName + ".json")
    os.system(f"copy {lyrx} {decFile}")
    return decFile


@getRunTime
def getValueAndLabelMapping(dataJson, outputJson):
    with open(dataJson, "r", encoding="utf-8") as f:
        data = f.read()

    dataToJson = json.loads(data)
    symClass = dataToJson["layerDefinitions"][0]["renderer"]["groups"][0]["classes"]
    resJson = {}
    for eachSym in symClass:
        label = eachSym["label"]
        value = eachSym["values"][0]["fieldValues"][0]
        resJson[value] = label
    with open(outputJson, "w", encoding="utf-8") as f:
        json.dump(resJson, f, ensure_ascii=False)

    return outputJson


@getRunTime
def main_single(lyrx, outputJson):
    global resJson
    resJson = copyLyrx2Txt(lyrx)
    getValueAndLabelMapping(resJson, outputJson)


def mergeJson(jsonDir):
    resDir = os.path.join(jsonDir, "res")
    # resJson = os.path.join(resDir, "res.json")
    res = {}
    if not os.path.exists(resDir):
        os.makedirs(resDir)

    jsonFile = os.listdir(jsonDir)
    for each in jsonFile:
        if each[-5:] == ".json":
            with open(os.path.join(jsonDir, each), "r", encoding="utf-8") as f:
                data_str = f.read()
                data_json = json.loads(data_str)
                for eachKey, eachValue in data_json.items():
                    # key not in res json, add it into res json
                    if not eachKey in res:
                        res[eachKey] = eachValue
                    # key in res json
                    else:
                        # same key without same value
                        n = 0
                        newKey = str(eachKey) + "_" + str(n)
                        while newKey in res:
                            n += 1
                            newKey = str(eachKey) + "_" + str(n)
                        res[eachKey] = eachValue

    with open(os.path.join(resDir, "res.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)


resJson = None
data = r"E:\公司GIS共用\通信管点信息特征.lyrx"
outputJson = r"E:\公司GIS共用\res.json"
lyrxDir = r"E:\公司GIS共用\DXGX\lyrx"
outJsonDir = r"E:\公司GIS共用\DXGX\json"
# aprxFile = r"E:\公司GIS共用\自动应用符号系统\自动应用符号系统\自动应用符号系统.aprx"
# mxdDir = r"E:\公司GIS共用\DXGX"

if __name__ == "__main__":
    lyrxList = os.listdir(lyrxDir)
    for lyrx in lyrxList:
        print(lyrx)
        lyrx = os.path.join(lyrxDir, lyrx)
        outJson = os.path.join(outJsonDir, os.path.basename(lyrx).split(".lyrx")[0] + ".json")
        try:
            main_single(lyrx, outJson)
            os.remove(resJson)
        except:
            os.remove(resJson)

    mergeJson(outJsonDir)






# aprx = arcpy.mp.ArcGISProject("CURRENT")
# maps = aprx.listMaps("*Layers*")
# for mapObj in maps:
#     print(mapObj.name)
#
# lyrs = maps[8].listLayers()
# for i, lyr in enumerate(lyrs):
#     if lyr.isFeatureLayer:
#         arcpy.management.SaveToLayerFile(lyr, fr"E:\公司GIS共用\DXGX\lyrx\CSGX_{i}.lyrx")
