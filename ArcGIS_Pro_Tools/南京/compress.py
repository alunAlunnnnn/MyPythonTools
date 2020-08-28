# # powered by esri xupf
# # time:20200311
# import os, gzip, zipfile, json, sys, time
# from PIL import Image
# from io import BytesIO
#
# if __name__ == "__main__":
#     print("powered by esri hacter\nrun...")
#
#     path = r'E:\南京工具\test_date.slpk'
#     slpk = r'E:\南京工具\res\GL_BUILDING.slpk'
#
#     # 读取与存储方式依旧为仅存储
#     z = zipfile.ZipFile(path, 'r', zipfile.ZIP_STORED, True)
#     w = zipfile.ZipFile(slpk, "w", zipfile.ZIP_STORED, True)
#
#
#     inners = z.namelist()
#     print(inners)
#     # sys.exit()
#     # modify scenelayer
#     gzc = z.read("3dSceneLayer.json.gz")
#     featureJson = json.loads(gzip.decompress(gzc))
#     featureJson1 = json.loads(gzip.decompress(gzc))
#     if featureJson["store"]["version"] != "1.7":
#         print("unsupport version 1.6 slpk")
#         exit()
#
#     # 获取贴图格式
#     texure_num = featureJson["textureSetDefinitions"].__len__()
#     textureSetDefinitions = featureJson["textureSetDefinitions"]
#     textureSetDefinitions1 = featureJson1["textureSetDefinitions"]
#     newtextureSetDefinitions1 = []
#     newtextureSetDefinitions2 = []
#     for tex in textureSetDefinitions:
#         newtextureSetDefinitions1.append(tex)
#     for tex in textureSetDefinitions1:
#         newtextureSetDefinitions2.append(tex)
#     for i in range(0, texure_num):
#         newtextureSetDefinitions1[i]["formats"] = [{
#             "name": "0",
#             "format": "jpg"
#         }]
#     for i in range(0, texure_num):
#         newtextureSetDefinitions2[i]["formats"] = [{
#             "name": "0",
#             "format": "png"
#         }]
#
#
#     for mat in featureJson["materialDefinitions"]:
#         if "alphaMode" in mat.keys():
#             mat["pbrMetallicRoughness"]["baseColorTexture"]["textureSetDefinitionId"] += texure_num
#
#
#     featureJson["textureSetDefinitions"] = newtextureSetDefinitions1 + newtextureSetDefinitions2
#     materialDefinitions = featureJson["materialDefinitions"]
#     featureJson["store"]["textureEncoding"] = [
#         "image/jpeg",
#         "image/png"
#     ]
#
#     # save scene layer
#     saveJson = json.dumps(featureJson).encode('utf-8')
#     gzjson = gzip.compress(saveJson)
#     w.writestr("3dSceneLayer.json.gz", gzjson, zipfile.ZIP_STORED)
#
#     # 从slpk数据列表中删除 "3dSceneLayer.json.gz"
#     index = inners.index("3dSceneLayer.json.gz")
#     del inners[index]
#
#
#     if "@specialIndexFileHASH128@" in inners:
#         index = inners.index("@specialIndexFileHASH128@")
#         del inners[index]
#
#
#     temp = z.read("metadata.json")
#     w.writestr("metadata.json", temp, zipfile.ZIP_STORED)
#     index = inners.index("metadata.json")
#     del inners[index]
#     #
#     for cursor in inners:
#         if cursor[-1] != '/':
#             flag = cursor.split("/")
#             if cursor[:5] == "nodep":
#                 gzc = z.read(cursor)
#                 w.writestr(cursor, gzc, zipfile.ZIP_STORED)
#                 featureJson = json.loads(gzip.decompress(gzc))
#                 nodes = featureJson["nodes"]
#                 for node in nodes:
#                     if "mesh" in node.keys():
#                         nodeid = str(node["mesh"]["material"]["resource"])
#                         definition = node["mesh"]["material"]["definition"]
#                         if "alphaMode" in materialDefinitions[definition].keys():
#                             # op dds
#                             ddspath = "nodes/%s/textures/0_0_1.bin.dds.gz" % nodeid
#                             pngpath = "nodes/%s/textures/0.png" % nodeid
#                             ddsgz = z.read(ddspath)
#                             dds = gzip.decompress(ddsgz)
#                             im = Image.open(BytesIO(dds))
#                             # PIL complains if you don't load explicitly
#                             im.load()
#                             # Get the alpha band
#                             alpha = im.split()[-1]
#                             im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
#                             # Set all pixel values below 128 to 255,
#                             # and the rest to 0
#                             mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
#                             # Paste the color of index 255 and use alpha as a mask
#                             im.paste(255, mask)
#                             # The transparency index is 255
#                             im.save("i3s_temp.png", transparency=255)
#                             # with open("i3s_temp.png",'rb') as rf:
#                             #     gzipfile=gzip.compress(rf.read())
#                             w.write("i3s_temp.png", pngpath, zipfile.ZIP_STORED)
#                         else:
#                             jpg = "nodes/%s/textures/0.jpg" % nodeid
#                             try:
#                                 temp = z.read(jpg)
#                                 w.writestr(jpg, temp, zipfile.ZIP_STORED)
#                             except Exception as ms:
#                                 print(ms)
#
#             else:
#                 if flag[2] != "textures":
#                     temp = z.read(cursor)
#                     w.writestr(cursor, temp, zipfile.ZIP_STORED)
#     w.close()
#     z.close()
#     os.remove("i3s_temp.png")
#     print('finish!')


def f(a):
    list11 = []
    if "1" in a:
        list1 = a.split('1')
        for each in list1:
            data = each.replace("3", "1")
            list11.append(data)
        list2 = "3".join(list11)
        return list2
    else:
        return a

data = "abc1cc2vv3"
print(f(data))