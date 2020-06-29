import os

dir = r'E:\slpk\Rancho_Mesh_v17_2\nodes'
dirList = os.listdir(dir)
for each in dirList:
    nodeDir = os.path.join(dir, each, '3dNodeIndexDocument.json')
    os.remove(nodeDir)

