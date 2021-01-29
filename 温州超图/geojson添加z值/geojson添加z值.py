import json
import sys


# geojson = r"F:\github\cesium_study\data\oriJson.json"
# newGeojson = r"F:\github\cesium_study\data\road_all_jm.json"
# move_x = 0
# move_y = 0
# move_z = 2


geojson = sys.argv[1]
newGeojson = sys.argv[2]
move_x = float(sys.argv[3])
move_y = float(sys.argv[4])
move_z = float(sys.argv[5])


with open(geojson, "r", encoding="utf-8") as f:
    data = f.read()

dataDict = json.loads(data)
newDict = {}

# feature class properity
for eachKey, eachValue in dataDict.items():
    if eachKey == "type":
        newDict["type"] = eachValue
    elif eachKey == "features":
        FClist = []
        # each single feature
        for eachFC in eachValue:
            singleFC = {}
            # save the data of each feature
            for eachFCKey, eachFCValue in eachFC.items():
                if eachFCKey != "geometry":
                    singleFC[eachFCKey] = eachFCValue
                else:
                    # save the properity in each feature
                    geoObj = {}
                    for eachFkey, eachFValue in eachFCValue.items():
                        if eachFkey != "coordinates":
                            geoObj[eachFkey] = eachFValue
                        else:
                            coordListTotal = []
                            # modify the coord value
                            for eachCoordList in eachFValue:
                                # assert len(eachCoordList) == 3, "the length of coord is not 3"

                                newCoordList = [float(eachCoordList[0]) + move_x, float(eachCoordList[1]) + move_y,
                                                float(eachCoordList[2]) + move_z]

                                coordListTotal.append(newCoordList)
                            geoObj[eachFkey] = coordListTotal
                        print("aaa", geoObj)
                    singleFC["geometry"] = geoObj
            FClist.append(singleFC)
        newDict["features"] = FClist
print(newDict)
resData = json.dumps(newDict, ensure_ascii=False)

with open(newGeojson, "w", encoding="utf-8") as f:
    f.write(resData)
