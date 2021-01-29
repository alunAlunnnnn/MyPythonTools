from PIL import Image
import os


def getRasterData(inputPath, extensionName):
    # get all raster datas
    rasList = [each for each in os.listdir(inputPath) if each[-4:] == extensionName]

    rasDict = {}
    for each in rasList:
        if "up" in each.lower():
            rasDict["up"] = each
        elif "dn" in each.lower():
            rasDict["down"] = each
        elif "fr" in each.lower():
            rasDict["front"] = each
        elif "bk" in each.lower():
            rasDict["back"] = each
        elif "lf" in each.lower():
            rasDict["left"] = each
        elif "rt" in each.lower():
            rasDict["right"] = each

    return rasDict


def rotateRaster(inputPath, rasDict, rotateDegree):
    # create output directory
    outputPath = os.path.join(inputPath, "result")
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    #
    for eachDir, eachData in rasDict.items():
        rotDeg = rotateDegree[eachDir]
        ras = os.path.join(inputPath, eachData)
        img = Image.open(ras)
        img.rotate(rotDeg).save(os.path.join(outputPath, eachData))



inputPath = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\温州超图\图片转天空盒\data\process"
extensionName = ".jpg"
rotateDegree = {
    "up": 0,  # 不变
    "down": 0,  # 不变
    "front": 0,  # 不变
    "back": 180,  # 旋转180度
    "left": 270,  # 顺时针旋转90度
    "right": 90,  # 逆时针旋转90度
}

rasDict = getRasterData(inputPath, extensionName)
print(rasDict)

rotateRaster(inputPath, rasDict, rotateDegree)


