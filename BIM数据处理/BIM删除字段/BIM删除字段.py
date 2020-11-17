import arcpy


def _deleteFields(inFC):
    fieldName = ["Bldg_Name", "BldgLevel_IsBuildingStory",
                 "BldgLevel_RoomOffset", "DemolishedPhase",
                 "ElementType", "Discipline", "Function",
                 "DocPath", "DocVer", "DocUpdate", "DocId",
                 "AssemblyCode", "AssemblyDesc", "OmniClass",
                 "OmniClassDescription", "Typ_Mark", "BldgLevel_Desc",
                 "DocName", "TopLevel", "TopLevel_IsBuildingStory",
                 "TopLevel_Elev", "TopLevel_RoomOffset", "TopLevel_Desc",
                 "ScheduleLevel_Elev", "ScheduleLevel_RoomOffset",
                 "ScheduleLevel_IsBuildingStory", "ScheduleLevel", "ScheduleLevel_Desc",
                 "Fam_输出容量", "Fam_联系方式", "Typ_Comments", "Typ_联系方式",
                 "Typ_输出容量", "Typ_t编码方式", "Typ_执行标准", "Typ_t工作温度",
                 "Typ_t壳体颜色",  "Fam_t编码方式", "Fam_t线制", "Fam_t指示灯",
                 "Fam_t工作温度", "Fam_t文字", "t文字", "Typ_t文字", "Typ_字体颜色",
                 "Fam_字体颜色", "Typ_来源", "t控制箱", "BaseLevel_IsBuildingStory",  "BaseLevel"]
    for each in fieldName:
        try:
            arcpy.DeleteField_management(inFC, each)
        except:
            pass


aprx = arcpy.mp.ArcGISProject("CURRENT")
scene = aprx.listMaps("Scene")[0]

lyrs = scene.listLayers()

for each in lyrs:
    if each.isFeatureLayer:
        print(each)
        print(each.name)
        _deleteFields(each)
