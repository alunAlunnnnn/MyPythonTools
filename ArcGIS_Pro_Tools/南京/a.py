import arcpy

data = r'D:\work\长江镇\cjz.gdb\RGCJDB84_process_0714\qy_process'
codes='''def f(a):
 try:
  a.replace(u'江苏', '')
 except:
  pass
 try:
  a.replace(u'南通', '')
 except:
  pass
 try:
  a.replace(u'有限公司', '')
 except:
  pass
 return a'''
arcpy.CalculateField_management(data, 'name_', 'f( !NAME! )', 'PYTHON3', codes)