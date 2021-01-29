import arcpy
import json

arcpy.env.overwriteOutput = True


def addTexturlField(inPlg, frontFieldName, upFieldName, typeFieldName):
    try:
        arcpy.AddField_management(inPlg, frontFieldName, "TEXT")
    except:
        arcpy.DeleteField_management(inPlg, frontFieldName)
        arcpy.AddField_management(inPlg, frontFieldName, "TEXT")

    try:
        arcpy.AddField_management(inPlg, upFieldName, "TEXT")
    except:
        arcpy.DeleteField_management(inPlg, upFieldName)
        arcpy.AddField_management(inPlg, upFieldName, "TEXT")

    try:
        arcpy.AddField_management(inPlg, typeFieldName, "TEXT")
    except:
        arcpy.DeleteField_management(inPlg, typeFieldName)
        arcpy.AddField_management(inPlg, typeFieldName, "TEXT")

    return inPlg


def calTypeField(inPlg, typeFieldName, floorFieldName, areaFieldName):
    codes = """def calTypeIdField(floor, area):
    if floor <= 2:
        if area <= 100:
            return '1_1'
        elif area <= 300:
            return '1_2'
        elif area <= 600:
            return '1_3'
        else:
            return '1_4'

    elif floor == 3:
        return '2_3'
    elif floor == 4:
        return '2_4'
    elif floor == 5:
        return '2_5'
    elif floor == 6:
        return '2_6'
    elif floor == 7:
        return '2_7'
    elif floor == 8:
        if area <= 300:
            return '2_8_1'
        else:
            return '2_8_2'
    elif floor == 9:
        return '2_9'
        
    else:
        return '3_x'"""

    arcpy.CalculateField_management(inPlg, typeFieldName, f"calTypeIdField(!{floorFieldName}!, !{areaFieldName}!)",
                                    "PYTHON3", codes)


def calTextureField(inPlg, typeFieldName, frontFieldName, upFieldName, textureMapping):
    # calculate fn texture
    codes = """def calFnTexture(typeFieldName, textureMapping):
    return textureMapping[typeFieldName]["fn"]"""

    arcpy.CalculateField_management(inPlg, frontFieldName, f"calFnTexture(!{typeFieldName}!, {textureMapping})",
                                    "PYTHON3", codes)

    # calculate up texture
    codes = """def calUpTexture(typeFieldName, textureMapping):
    return textureMapping[typeFieldName]["up"]"""

    arcpy.CalculateField_management(inPlg, upFieldName, f"calUpTexture(!{typeFieldName}!, {textureMapping})",
                                    "PYTHON3", codes)


def main(inPlg, frontFieldName, upFieldName, typeFieldName, floorFieldName, areaFieldName, textureMapping):
    # create texture url and type field
    addTexturlField(inPlg, frontFieldName, upFieldName, typeFieldName)

    # calculate type field
    calTypeField(inPlg, typeFieldName, floorFieldName, areaFieldName)

    # calculate texture url
    calTextureField(inPlg, typeFieldName, frontFieldName, upFieldName, textureMapping)


# textureMapping = {
#     "low": {
#         "small": {
#             "fn": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\low_small_fn.png",
#             "up": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\low_small_up.png"
#         },
#         "big": {
#             "fn": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\low_big_fn.png",
#             "up": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\low_big_up.png"
#         }
#     },
#     "mid": {
#         "small": {
#             "fn": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\mid_small_fn.png",
#             "up": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\mid_small_up.png"
#         },
#         "big": {
#             "fn": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\mid_big_fn.png",
#             "up": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\mid_big_up.png"
#         }
#     },
#     "high": {
#         "small": {
#             "fn": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\high_big_fn.png",
#             "up": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\high_big_up.png"
#         },
#         "big": {
#             "fn": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\high_big_fn.png",
#             "up": r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段_全数据量简易贴图拉伸_20210105\texture\high_big_up.png"
#         }
#     }
# }

# with open(r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段三_贴图及分类间隔调整\代码_配置文件\texture.json", "w", encoding="utf-8") as f:
#     json.dump(textureMapping, f, ensure_ascii=False, indent=4)


inPlg = r"E:\粗摸拉伸\数据\plg_modified_cgcs2000_all.shp"
frontFieldName = "texture_fn"
upFieldName = "texture_up"
typeFieldName = "text_type"
floorFieldName = "FLOOR"
areaFieldName = "area_m"
textureConf = r"F:\工作项目\项目_温州超图\任务_粗摸制作\阶段三_贴图及分类间隔调整\代码_配置文件\texture_cadsj.json"

with open(textureConf, "r", encoding="utf-8") as f:
    textureMapping = json.load(f)
print(textureMapping)
main(inPlg, frontFieldName, upFieldName, typeFieldName, floorFieldName, areaFieldName, textureMapping)
