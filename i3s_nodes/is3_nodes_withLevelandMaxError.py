import gzip, os, json


resDic = {}


class NoRootNodes(Exception):
    pass


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


def getRootNode(baseDir):
    for i, each in enumerate(os.listdir(baseDir)):
        if i % 50 == 0:
            print(i)

        if each == 'root':
            subDir = os.path.join(baseDir, each)
            jsonFile = [eachSub for eachSub in os.listdir(subDir) if eachSub == '3dNodeIndexDocument.json'][0]
            # print(subDir)
            # print(jsonFile)
            jsonFile = os.path.join(subDir, jsonFile)

            # read root json data —— 3dNodeIndexDocument.json
            with open(jsonFile, 'r', encoding='utf-8') as f:
                rootJson = f.read()

            rootDic = json.loads(rootJson)
            # print(rootDic)
    return rootDic


def buildTree(baseDir, parentNodeDict, parentNode='root'):
    level = parentNodeDict['level']
    parentNode = parentNode + '(' + str(level) + ')'

    for i, each in enumerate(parentNodeDict['children']):
        subNodeID = each['id']
        nodeTree = parentNode + '.' + subNodeID
        subDir = os.path.join(baseDir, subNodeID)
        subNodeJson = [eachFIle for eachFIle in os.listdir(subDir) if eachFIle == '3dNodeIndexDocument.json'][0]
        with open(os.path.join(subDir, subNodeJson), 'r', encoding='utf-8') as f:
            subData = f.read()
            subJsonData = json.loads(subData)
        if subJsonData.get('children', None):
            buildTree(baseDir, subJsonData, nodeTree)
        else:
            leafLevel = getLeafNodesLevel(baseDir, subNodeID)
            nodeTree += leafLevel
            resDic[nodeTree[:]] = int(nodeTree.count('.')) + 1



def fn(src, key='', dct={}):  # src = {'a':{'b':1,'c':2},'d':{'e':3,'f':{'g':4}}}
    for k, v in src.items():
        newkey = key + k + '.'
        if isinstance(v, int):
            newkey = newkey.strip('.')
            dct[newkey] = v
        else:
            fn(v, newkey)
    return dct

# src = {'a':{'b':1,'c':2},'d':{'e':3,'f':{'g':4}}}
# dst = fn(src)
# print(dst)


def getLeafNodesLevel(baseDir, subNodeID):
    leafDir = os.path.join(baseDir, subNodeID)
    with open(os.path.join(leafDir, '3dNodeIndexDocument.json'), 'r', encoding='utf-8') as f:
        subData = f.read()
        subJsonData = json.loads(subData)
    level = subJsonData['level']
    return '(' + str(level) + ')'



print('start')
# baseDir = r'E:\slpk\Rancho_Mesh_v17\nodes'
# baseDir = r'E:\slpk\small_自适应树\nodes'
baseDir = r'E:\CCProject\Projects\newSmall\Productions\aa_glb\nodes'
# uncompressGzData(baseDir)
rootDict = getRootNode(baseDir)
# print(rootDict)
buildTree(baseDir, rootDict)
print('finish')
res = json.dumps(resDic)
with open('D:/a/res/small_old_withRootAndLevel.json', 'w', encoding='utf-8') as f:
    f.write(res)