
# data2d = 'xxx'
# data3d = 'yyy'
# d2d = arcpy.Sort_management(data2d, 'in_memory/temp_2d_', [['x_temp_', 'Ascending'], ['y_temp_', 'Ascending'], ['z_temp_', 'Ascending']])
# d3d = arcpy.Sort_management(data3d, 'in_memory/temp_3d_', [['x_temp_', 'Ascending'], ['y_temp_', 'Ascending'], ['z_temp_', 'Ascending']])
# codes='''a = None
# def getDis(x):
#     global a
#     if a is None:
#         a = x
#         return 0
#     else:
#         return float(x) - float(a)'''
#
# arcpy.AddField_management(d2d, 'x_dis_', 'DOUBLE')
# arcpy.AddField_management(d3d, 'x_dis_', 'DOUBLE')
#
# arcpy.CalculateField_management(d2d, 'x_dis_', 'getDis(!x_temp_!)', 'PYTHON3', codes)
# arcpy.CalculateField_management(d3d, 'x_dis_', 'getDis(!x_temp_!)', 'PYTHON3', codes)



# data2d = 'xxx'
# data3d = 'yyy'
#
# field = ['x_uni_', 'y_uni_', 'z_uni_']
# fieldCal = ['getUni(!x_temp_!)', 'getUni(!y_temp_!)', 'getUni(!z_temp!)']
# codes = '''a = []
# def getUni(x):
#     global a
#     a.append(x)
#     return a.count(x)'''
# for i, each in enumerate(field):
#     arcpy.AddField_management(data2d, each, 'DOUBLE')
#     arcpy.AddField_management(data3d, each, 'DOUBLE')
#     arcpy.CalculateField_management(data2d, each, fieldCal[i], 'PYTHON3', codes)
#     arcpy.CalculateField_management(data3d, each, fieldCal[i], 'PYTHON3', codes)
#
#
# a = []
# def getUni(x):
#     global a
#     a.append(x)
#     return a.count(x)
#
#
# data2d = 'xxx'
# data3d = 'yyy'
#
# field = ['x_uni_2', 'y_uni_2', 'z_uni_2']
# fieldCal = ['getUni(!x_temp_!)', 'getUni(!y_temp_!)', 'getUni(!z_temp!)']
# codes = '''a = []
# def getUni(x):
#     global a
#     if '.' in str(x):
#         x = float(str(x).split('.')[0] + '.' + str(x).split('.')[1][:2])
#     a.append(x)
#     return a.count(x)'''
# for i, each in enumerate(field):
#     arcpy.AddField_management(data2d, each, 'DOUBLE')
#     arcpy.AddField_management(data3d, each, 'DOUBLE')
#     arcpy.CalculateField_management(data2d, each, fieldCal[i], 'PYTHON3', codes)
#     arcpy.CalculateField_management(data3d, each, fieldCal[i], 'PYTHON3', codes)
#
#
#
#
#
# a = []
# def getUni(x):
#     global a
#     if '.' in str(x):
#         x = float(str(x).split('.')[0] + '.' + str(x).split('.')[1][:2])
#     a.append(x)
#     return a.count(x)