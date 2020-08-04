import os
import shutil

# formats = {
#     "安装包": [".exe", ".msi"] ,
#     "视频": [".mp4", ".wmv", ".avi", ".mov"] ,
#     "音频": [".mp3", ".wav"] ,
#     "音频": [".jpg", ".png"] ,
#     "压缩包": [".zip", ".rar"],
#     "文本文档/txt数据": [".txt"],
#     "文本文档/word数据": [".doc", ".docx"],
#     "文本文档/excel数据": [".xls", ".xlsx"],
#     "文本文档/电子书": [".epub", ".mobi"] ,
#     "文本文档/pdf数据": [".pdf"],
#     "HTML数据": [".htm", ".html"] ,
#     "三维数据/BIM数据": [".ifc", ".rvt"] ,
#     "三维数据/GIS_BIM数据": [".slpk"] ,
#     "GIS数据/shp数据": [".shp", ".dbf", ".prj", ".sbn", ".sbx", ".shx"],
#     "GIS数据/mxd数据": [".mxd", ".mpk"],
#     "GIS数据/cad数据": [".dwg", ".dxf"]
# }

formats = {
    "安装包": [".exe", ".msi"] ,
    "视频": [".mp4", ".wmv", ".avi", ".mov"] ,
    "音频": [".mp3", ".wav"] ,
    "音频": [".jpg", ".png"] ,
    "压缩包": [".zip", ".rar"],
    "文本文档/txt数据": [".txt"],
    "文本文档/word数据": [".doc", ".docx"],
    "文本文档/excel数据": [".xls", ".xlsx"],
    "文本文档/电子书": [".epub", ".mobi"] ,
    "文本文档/pdf数据": [".pdf"],
    "HTML数据": [".htm", ".html"] ,
    "三维数据/BIM数据": [".ifc", ".rvt"] ,
    "三维数据/GIS_BIM数据": [".slpk"] ,
    "GIS数据/shp数据": [".shp", ".dbf", ".prj", ".sbn", ".sbx", ".shx"],
    "GIS数据/mxd数据": [".mxd", ".mpk"],
    "GIS数据/cad数据": [".dwg", ".dxf"]
}


def GetKey(inDict, inValue):
    key = [k for k, _ in inDict.items() if _ == inValue]
    return key


def FileArrangement(arrDir, targetDir, diGui=False):
    # 通过assert来判断输入的参数---是否递归，是否合法（递归需谨慎，尤其是对桌面文件进行整理时）
    assert isinstance(eval(diGui), bool), "参数 “递归”，非布尔值"
    # 多使用一个os.chdir()，提升对切换工作目录的记忆
    os.chdir(targetDir)
    fileList = os.listdir(arrDir)
    for eachFile in fileList:
        # 判断是否为目录，如果是目录就继续向下递归
        if os.path.isdir(os.path.join(arrDir, eachFile)) and eval(diGui) == True:
            FileArrangement(os.path.join(arrDir, eachFile), targetDir, diGui)
        # 如果不是目录则进行判断，并移动
        else:
            for values in formats.values():
                if os.path.splitext(eachFile)[-1] in values:
                    key = GetKey(formats, values)
                    print(key)
                    # shutil.move(os.path.join(arrDir, eachFile), os.path.join(key[0], eachFile))
                    if not os.path.exists(key[0]):
                        os.makedirs(key[0])
                    shutil.move(os.path.join(arrDir, eachFile), os.path.join(key[0], eachFile))
                elif os.path.splitext(eachFile)[-1] == ".tmp" or os.path.splitext(eachFile)[-1] == ".pyc":
                    try:
                        os.remove(eachFile)
                    except:
                        pass
    print("整理结束！")
arrDir = r"C:\Users\Administrator\Desktop"
targetDir = r"C:\Users\Administrator\Desktop"
diGui = "False"
FileArrangement(arrDir, targetDir, diGui)