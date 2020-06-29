import os

dir = r'E:\slpk\max\nodes'
dirList = os.listdir(dir)
for each in dirList:
    try:
        nodeDir = os.path.join(dir, each, '3dNodeIndexDocument.json')
        os.remove(nodeDir)
    except:
        pass

