import os, gzip, json
from PIL import Image


# 3dNodeIndexDocument.json
def uncompressGzData(baseDir):
    subDirList = os.listdir(baseDir)
    for i, each in enumerate(subDirList):
        if i % 50 == 0:
            print(i)

        indexDocDir = os.path.join(baseDir, each)
        indexDoc = [ eachData for eachData in os.listdir(indexDocDir) if '3dNodeIndexDocument.json' in eachData][0]
        docData = os.path.join(indexDocDir, indexDoc)
        savData = os.path.join(indexDocDir, indexDoc[:-3])
        with gzip.open(docData, 'rb') as f:
            data = f.read()
        with open(savData, 'wb') as f:
            f.write(data)


def compressJPG(baseDir, nodesId, jpgFile):
    pass


def getResourceFromNodePagesIndex(nodePagesDir, targetLevel):
    targetLevel = int(targetLevel)
    if targetLevel == 1:
        minIndex = 1
        maxIndex = 4
    else:
        minIndex = 1 + 4 ** (targetLevel - 1)
        maxIndex = 4 + 4 ** (targetLevel - 1)

    # if maxIndex




def getNodesListFromNodesLevel(baseDir):
    levelDict = {}
    nodesList = os.listdir(baseDir)
    for i, eachNode in enumerate(nodesList):
        nodeDir = os.path.join(baseDir, eachNode)

        # unconpress gzip data
        gzIndexDocument = os.path.join(nodeDir, '3dNodeIndexDocument.json.gz')
        indexDocument = os.path.join(nodeDir, '3dNodeIndexDocument.json')
        with gzip.open(gzIndexDocument, 'rb') as g:
            data = g.read()

        with open(indexDocument, 'wb') as f:
            f.write(data)

        with open(indexDocument, 'r', encoding='utf-8') as f:
            strData = f.read()
            dicData = json.loads(strData)

        level = dicData['level']
        nodeId = dicData['id']

        if level not in levelDict:
            levelDict[level] = []

        levelDict[level].append(nodeId)

        os.remove(indexDocument)
    return levelDict


nodesDir = r'E:\slpk\max\nodes'
nodeDictWithLevel = getNodesListFromNodesLevel(nodesDir)
repJPGDir = r'E:\slpk\Desktop\16张不同的'
textureDir = 'textures'
#
for eachKey, eachValue in nodeDictWithLevel.items():
    compressLevelNodes = eachValue
    for each in compressLevelNodes:
        if os.path.exists(os.path.join(nodesDir, str(each), textureDir)):
            targetDir = os.path.join(nodesDir, str(each), textureDir)
            try:
                os.remove(os.path.join(targetDir, '0_0_1.bin.dds.gz'))
            except:
                pass

            try:
                os.remove(os.path.join(targetDir, '0.jpg'))
            except:
                pass

            # copy a .jpg file to target dir
            repImg = Image.open(os.path.join(repJPGDir, str(eachKey) + '.jpg'))
            repImg.save(os.path.join(targetDir, '0.jpg'))
            del repImg

            # compress jpg image
            img = Image.open(os.path.join(targetDir, '0.jpg'))
            img.save(os.path.join(targetDir, '0_com.jpg'), quality=1)
            del img

            newImg = Image.open(os.path.join(targetDir, '0_com.jpg'))
            os.system('D:/softs/soft/ddsInstall/nvdxt.exe -file %s -output %s -dxt1a -nomipmap' % (os.path.join(targetDir, '0_com.jpg'), os.path.join(targetDir, '0_0_1.bin.dds')))

            del newImg

            try:
                os.remove(os.path.join(targetDir, '0_com.jpg'))
            except:
                pass

            # write to gz
            with open(os.path.join(targetDir, '0_0_1.bin.dds'), 'rb') as f:
                data = f.read()
            with gzip.open(os.path.join(targetDir, '0_0_1.bin.dds.gz'), 'wb') as g:
                g.write(data)

            try:
                os.remove(os.path.join(targetDir, '0_0_1.bin.dds'))
            except:
                pass






