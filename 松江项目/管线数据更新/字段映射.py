import arcpy


arcpy.env.overwriteOutput = True

# create field mapping
def _AddFieldMapping(inRas2pnt, fieldList, mergeRuleList, mergeFieldList):
    fieldMappings = arcpy.FieldMappings()
    fieldMapList = []

    # create fieldMap with all field
    for i in range(len(fieldList)):
        fieldMap = arcpy.FieldMap()
        fieldMapList.append(fieldMap)

    # add all fieldMap to fieldMappings
    for i, each in enumerate(fieldList):
        fieldMapList[i].addInputField(inRas2pnt, each)
        # fieldMapList[i].addInputField(inRas2pnt, mergeFieldList[i])
        fieldMapList[i].mergeRule = mergeRuleList[i]
        fieldMapList[i].joinDelimiter = ','

        fieldObj = fieldMapList[i].outputField
        fieldObj.name = 'kaer'
        fieldObj.aliasName = 'erka'
        fieldObj.length = 255
        fieldMapList[i].outputField = fieldObj
        fieldMappings.addFieldMap(fieldMapList[i])
    return fieldMappings

plgFC = r'E:\sjgl_sjgx\tool_test\plg2018test.gdb\DL_GD_A'
pntFC = r'E:\sjgl_sjgx\tool_test\plg2018test.gdb\pnt_T81010102'
fieldList = ['TEXT']
mergeRuleList = ['Join']
mergeFieldList = ['TEXT']

fms = _AddFieldMapping(pntFC, fieldList, mergeRuleList, mergeFieldList)

# try:
#     arcpy.AddField_management(plgFC, 'TEXT', 'TEXT', field_length=255)
# except:
#     arcpy.DeleteField_management(plgFC, 'TEXT')
#     arcpy.AddField_management(plgFC, 'TEXT', 'TEXT', field_length=255)

arcpy.SpatialJoin_analysis(plgFC, pntFC, r'E:\sjgl_sjgx\tool_test\plg2018test.gdb\testplg', '', '', fms)


#
# import arcpy
#
# # Set the workspace
# arcpy.env.workspace = 'c:/base'
#
# in_file1 = 'data.gdb/Trees'
# in_file2 = 'Plants.shp'
# output_file = 'data.gdb/Vegetation'
#
# # Create the required FieldMap and FieldMappings objects
# fm_type = arcpy.FieldMap()
# fm_diam = arcpy.FieldMap()
# fms = arcpy.FieldMappings()
#
# # Get the field names of vegetation type and diameter for both original
# # files
# tree_type = "Tree_Type"
# plant_type = "Plant_Type"
#
# tree_diam = "Tree_Diameter"
# plant_diam = "Diameter"
#
# # Add fields to their corresponding FieldMap objects
# fm_type.addInputField(in_file1, tree_type)
# fm_type.addInputField(in_file2, plant_type)
#
# fm_diam.addInputField(in_file1, tree_diam)
# fm_diam.addInputField(in_file2, plant_diam)
#
# # Set the output field properties for both FieldMap objects
# type_name = fm_type.outputField
# type_name.name = 'Veg_Type'
# fm_type.outputField = type_name
#
# diam_name = fm_diam.outputField
# diam_name.name = 'Veg_Diam'
# fm_diam.outputField = diam_name
#
# # Add the FieldMap objects to the FieldMappings object
# fms.addFieldMap(fm_type)
# fms.addFieldMap(fm_diam)
#
# # Merge the two feature classes
# arcpy.Merge_management([in_file1, in_file2], output_file, fms)
#
#
#
#
#
#
#
# import arcpy
#
# # Set the workspace
# arcpy.env.workspace = 'c:/base/data.gdb'
#
# in_file = 'AccidentData'
# out_file = 'AverageAccidents'
#
# # Create the necessary FieldMap and FieldMappings objects
# fm = arcpy.FieldMap()
# fm1 = arcpy.FieldMap()
# fms = arcpy.FieldMappings()
#
# # Each field with accident data begins with 'Yr' (from Yr2007 to Yr2012).
# # The next step loops through each of the fields beginning with 'Yr',
# # and adds them to the FieldMap Object
# for field in arcpy.ListFields(in_file, 'Yr*'):
#     fm.addInputField(in_file, field.name)
#
# # Set the merge rule to find the mean value of all fields in the
# # FieldMap object
# fm.mergeRule = 'Mean'
#
# # Set properties of the output name.
# f_name = fm.outputField
# f_name.name = 'AvgAccidents'
# f_name.aliasName = 'AvgAccidents'
# fm.outputField = f_name
#
# # Add the intersection field to the second FieldMap object
# fm1.addInputField(in_file, "Intersection")
#
# # Add both FieldMaps to the FieldMappings Object
# fms.addFieldMap(fm)
# fms.addFieldMap(fm1)
#
# # Create the output feature class, using the FieldMappings object
# arcpy.FeatureClassToFeatureClass_conversion(
#     in_file, arcpy.env.workspace, out_file, field_mapping=fms)