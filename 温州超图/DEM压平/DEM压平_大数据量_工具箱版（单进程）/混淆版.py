import arcpy
j=print
E=dir
y=None
s=arcpy.Raster
V=arcpy.RasterToNumPyArray
B=arcpy.MosaicToNewRaster_management
K=arcpy.env
l=arcpy.sa
j=j
T=E
u=y
S=l
q=K
l=B
b=V
R=s
import os
F=os.walk
D=os.path
i=D
m=F
import datetime
T=datetime.datetime
M=S
h=T
import functools
w=functools.wraps
B=w
class L:
 def __init__(s,g):
  s.inRas=g
  s.f(g)
 def f(s,g):
  e=R(g)
  s.sr=e.spatialReference
  s.extent=[e.extent.XMin,e.extent.YMin,e.extent.XMax,e.extent.YMax]
  s.extentObj=e.extent
  s.lowerLeft=e.extent.lowerLeft
  s.nodata=e.noDataValue
  if e.format.lower()=="imagine image":
   s.format=".img"
  elif e.format.lower()=="tiff":
   s.format=".tif"
  elif e.format.lower()=="fgdbr":
   s.format=""
  else:
   s.format=e.format
  s.maxValue=e.maximum
  s.minValue=e.minimum
  s.meanValue=e.mean
  s.meanCellWidth=e.meanCellWidth
  s.meanCellHeight=e.meanCellHeight
  s.dataPath=e.path
  s.pixelType=e.pixelType
  return s
 def A(s):
  v=b(s.inRas)
  return v
def r(func):
 @B(func)
 def D(*args,**kwargs):
  P=h.now()
  j(f"Start run function {func.__name__}, at {P}")
  Q=func(*args,**kwargs)
  O=h.now()
  U=O-P
  j("*"*16)
  j(f"Function {func.__name__} run infomation")
  j(f"Start: {P}")
  j(f"End: {O}")
  j(f"Cost: {U}")
  j("*"*16)
  return Q
 return D
def k(Y):
 G=[]
 for c,T,files in m(Y):
  if files:
   X=[i.join(c,each)for each in files if each[:3]=="min" and each[-4:]==".img"]
   G+=X
 return G
def H(G,J,W):
 l(G,J,W,pixel_type="32_BIT_FLOAT",number_of_bands=1)
 return i.join(J,W)
def E(V,I,J,W):
 o=L(V)
 q.compression=u
 q.snapRaster=V
 q.extent=o.extentObj
 t=S.Con(S.IsNull(I),0,I)
 t.save(i.join(J,"demFillNull.img"))
 C=S.Plus(V,t)
 C.save(i.join(J,W))
@r
def x(Y,J,mosaicData,W):
 G=k(Y)
 j(G)
 I=H(G,J,mosaicData)
 E(V,I,J,W)
V=r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\DEM\DEM30.img"
Y=r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\数据拆分_30米\processing_raster"
J=r"F:\工作项目\项目_温州超图\任务_30米DEM压平\白模场景\代码debug2"
p="mosaic_30m_2.img"
W="dem_yaping_30m_2.img"
if __name__=="__main__":
 x(Y,J,p,W)