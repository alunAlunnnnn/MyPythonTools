import arcpy
kX=True
kg=Exception
kw=isinstance
ko=tuple
kD=float
ki=len
kS=None
kO=int
kK=abs
kn=min
ks=max
ku=print
kT=round
kE=arcpy.AddError
kN=arcpy.GetParameterAsText
kr=arcpy.MosaicToNewRaster_management
kL=arcpy.PolygonToRaster_conversion
kx=arcpy.SelectLayerByAttribute_management
kj=arcpy.SetProgressorPosition
kU=arcpy.MakeFeatureLayer_management
kQ=arcpy.SetProgressor
kv=arcpy.sa
kq=arcpy.ClearEnvironment
kf=arcpy.Delete_management
kI=arcpy.ListRasters
km=arcpy.ListFeatureClasses
kc=arcpy.CalculateField_management
kW=arcpy.DeleteField_management
kl=arcpy.AddField_management
kF=arcpy.da
kV=arcpy.ListFields
kA=arcpy.NumPyArrayToRaster
ky=arcpy.Point
kG=arcpy.RasterToNumPyArray
kb=arcpy.Raster
kh=arcpy.env
import datetime
kz=datetime.datetime
import functools
kd=functools.wraps
import os
kt=os.makedirs
kC=os.path
import math
ke=math.sqrt
kh.overwriteOutput=kX
class NoFieldError(kg):
 pass
class pointError(kg):
 pass
class calKError(kg):
 pass
class GenerateSpatialIndexError(kg):
 pass
class lineEquation:
 def __init__(k,*M):
  k.points=[]
  for a in M[:2]:
   if not kw(a,ko):
    raise pointError
   k.points.append((kD(a[0]),kD(a[1]),kD(a[2])))
  k.extent_xmin=M[2][0]
  k.extent_ymin=M[2][1]
  k.extent_xmax=M[2][2]
  k.extent_ymax=M[2][3]
  k.extent=M[2]
  k.pntNum=ki(M)
  k.pipeSize=kS
  k.x1=k.points[0][0]
  k.y1=k.points[0][1]
  k.z1=k.points[0][2]
  k.x2=k.points[-1][0]
  k.y2=k.points[-1][1]
  k.z2=k.points[-1][2]
  k._extentAvailableDetect()
  k.spaindex=kS
  k.spaindex_row=kS
  k.spaindex_col=kS
  k.spaind_totalext=kS
  k.calculateK_xy()
  k.calculateB_xy()
  k.calculateK_yz()
  k.calculateB_yz()
  k.calculateK_xz()
  k.calculateB_xz()
  k.generateEquation()
 def calculateK_xy(k):
  if k.x1==k.x2:
   k.k_xy=-999
   return k
  k=(k.y2-k.y1)/(k.x2-k.x1)
  k.k_xy=k
  return k
 def calculateB_xy(k):
  if k.k_xy==-999:
   k.b_xy=-999
  else:
   b=k.y1-k.k_xy*k.x1
   k.b_xy=b
  return k
 def calculateK_yz(k):
  if k.y1==k.y2:
   k.k_yz=-999
   return k
  k=(k.z2-k.z1)/(k.y2-k.y1)
  k.k_yz=k
  return k
 def calculateB_yz(k):
  if k.k_yz==-999:
   k.b_yz=-999
  else:
   b=k.z1-k.k_yz*k.y1
   k.b_yz=b
  return k
 def calculateK_xz(k):
  if k.x1==k.x2:
   k.k_xz=-999
   return k
  k=(k.z2-k.z1)/(k.x2-k.x1)
  k.k_xz=k
  return k
 def calculateB_xz(k):
  if k.k_xz==-999:
   k.b_xz=-999
  else:
   b=k.z1-k.k_xz*k.x1
   k.b_xz=b
  return k
 def generateEquation(k):
  k.euqation_xy='%s * x + %s'%(k.k_xy,k.b_xy)
  k.euqation_yz='%s * x + %s'%(k.k_yz,k.b_yz)
  k.euqation_xz='%s * x + %s'%(k.k_xz,k.b_xz)
  return k
 def calculateIntersect(k,p):
  if k.k_xy==p.k_xy:
   k.intersect='false'
   p.intersect='false'
   return kS
  if k.b_xy==p.b_xy:
   x=0
   y=k.b_xy
  else:
   x=(p.b_xy-k.b_xy)/(k.k_xy-p.k_xy)
   y=k.k_xy*x+k.b_xy
  if x>k.extent_xmin and x<k.extent_xmax:
   if y>k.extent_ymin and y<k.extent_ymax:
    k.intersect='true'
   else:
    k.intersect='false'
  else:
   k.intersect='false'
  if x>p.extent_xmin and x<p.extent_xmax:
   if y>p.extent_ymin and y<p.extent_ymax:
    p.intersect='true'
   else:
    p.intersect='false'
  else:
   p.intersect='false'
  return x,y
 def calculateZCoord_yz(k,x,y):
  if k.k_yz!=-999:
   z=k.k_yz*y+k.b_yz
  else:
   if k.k_xz!=-999:
    z=k.k_xz*x+k.b_xz
   else:
    z=-999
  return z
 def calculateZCoord_xz(k,x,y):
  if k.k_xz!=-999:
   z=k.k_xz*x+k.b_xz
  else:
   if k.k_yz!=-999:
    z=k.k_yz*y+k.b_yz
   else:
    z=-999
  return z
 def _extentAvailableDetect(k):
  assert kO(k.extent_xmin*10**8)<=kO(k.extent_xmax*10**8),"Error --- Extent of line object is not available"
  assert kO(k.extent_ymin*10**8)<=kO(k.extent_ymax*10**8),"Error --- Extent of line object is not available"
 def calDisFromPnt(k,firstPoint):
  x,y,z=firstPoint[0],firstPoint[1],firstPoint[2]
  H=k.k_xy
  if H==-999:
   k=0
  elif-0.0001<=H<=0.0001:
   k=-999
  else:
   k=-1/H
  if k==-999:
   P=k.k_xy*x+k.b_xy
   Y=kK(y-P)
   R=k.b_xy
   h=y
   b=k.calculateZCoord_yz(h,R)
  elif k==0:
   Y=kK(x-k.extent_xmin)
   R=y
   h=k.extent_xmin
   b=k.calculateZCoord_yz(h,R)
  else:
   b=y-k*x
   G=k.extent_xmin
   y=k*G+b
   A=k.calculateZCoord_yz(G,y)
   V=(kn(x,G),kn(y,y),ks(x,G),ks(y,y))
   F=lineEquation((x,y,z),(G,y,A),V)
   h,R=k.calculateIntersect(F)
   b=k.calculateZCoord_yz(h,R)
   Y=ke((y-R)**2+(x-h)**2)
  if b!=-999:
   l=ke(Y**2+(z-b)**2)
  else:
   l=Y
  return l
class MyRas:
 def __init__(k,W):
  k.inRas=W
  k.getInfoFromRas(W)
 def getInfoFromRas(k,W):
  c=kb(W)
  k.sr=c.spatialReference
  k.extent=[c.extent.XMin,c.extent.YMin,c.extent.XMax,c.extent.YMax]
  k.extentObj=c.extent
  k.lowerLeft=c.extent.lowerLeft
  k.nodata=c.noDataValue
  if c.format.lower()=="imagine image":
   k.format=".img"
  elif c.format.lower()=="tiff":
   k.format=".tif"
  elif c.format.lower()=="fgdbr":
   k.format=""
  else:
   k.format=c.format
  k.maxValue=c.maximum
  k.minValue=c.minimum
  k.meanValue=c.mean
  k.meanCellWidth=c.meanCellWidth
  k.meanCellHeight=c.meanCellHeight
  k.dataPath=c.path
  k.pixelType=c.pixelType
  return k
 def toNDArray(k):
  m=kG(k.inRas)
  return m
def getRunTime(func):
 @kd(func)
 def _wrapper(*M,**kwargs):
  I=kz.now()
  ku("Start run function {}, at {}".format(func.__name__,I))
  f=func(*M,**kwargs)
  q=kz.now()
  v=q-I
  ku("*"*16)
  ku("Function {} run infomation".format(func.__name__))
  ku("Start: {}".format(I))
  ku("End: {}".format(q))
  ku("Cost: {}".format(v))
  ku("*"*16)
  return f
 return _wrapper
def rasterProcessWithNumpy(W,outRas):
 c=kb(W)
 sr=c.spatialReference
 ku("nodata value: ",c.noDataValue)
 ku("sr: ",sr.name)
 m=kG(W,nodata_to_value=kS)
 ku(m)
 Q=ky(c.extent.XMin,c.extent.YMin)
 U=c.meanCellWidth
 j=c.meanCellHeight
 x=kA(m,Q,U,j,value_to_nodata=c.noDataValue)
 x.save(outRas)
def getFCOIDName(inFC):
 L=[a.name for a in kV(inFC)if a.type=="OID"][0]
 return L
def getFCOIDValue(inFC):
 r=getFCOIDName(inFC)
 N=[]
 with kF.SearchCursor(inFC,[r])as cur:
  for E in cur:
   N.append(E[0])
  del E
 return r,N
def _addConvertField(inFC):
 try:
  kl(inFC,"HSCONF_","SHORT")
 except:
  kW(inFC,"HSCONF_")
  kl(inFC,"HSCONF_","SHORT")
 if ki([a.name for a in kV(inFC)if a.name=="HSCONF_"])>0:
  kc(inFC,"HSCONF_","1","PYTHON_9.3")
  return inFC
 else:
  ku("No Such Field Named HSCONF_ In Feature Class {}".format(inFC))
  raise NoFieldError
def _delTempData(inFC,J):
 try:
  kW(inFC,"HSCONF_")
 except:
  pass
 z=kS
 if kh.workspace:
  z=kh.workspace
 kh.workspace=J
 B=km()
 d=kI()
 for a in B:
  try:
   kf(a)
  except:
   pass
 for a in d:
  try:
   kf(a)
  except:
   pass
 if z:
  kh.workspace=z
 else:
  kq("workspace")
 B=km()
def makeTempDir(kP):
 J=kC.join(kP,"tmdRunDir_")
 if not kC.exists(J):
  kt(J)
 return J
def vailOutdataFormat(kP,C,t):
 if kP[-4:]==".gdb" or kP[-4:]==".mdb":
  C.format=""
  if t[-4:].lower()==".tif" or t[-4:].lower()==".img":
   t=t[:-4]
 return t
@getRunTime
def main(W,X,kP,t):
 e=MyRas(W)
 J=makeTempDir(kP)
 r,N=getFCOIDValue(X)
 X=_addConvertField(X)
 kh.snapRaster=W
 kh.extent=e.extentObj
 kh.compression=kS
 t=vailOutdataFormat(kP,e,t)
 g=kv.CreateConstantRaster(0,"INTEGER",e.meanCellWidth,e.extentObj)
 kQ("step","processing...",0,ki(N)+10,1)
 w=[]
 o=kU(X)
 for D in N:
  kj()
  i=kx(o,"NEW_SELECTION","{} = {}".format(r,D))
  ku(e.format)
  S=kC.join(J,"ras_{}{}".format(D,e.format))
  ku(S)
  kL(i,"HSCONF_",S,cellsize=kn(e.meanCellWidth,e.meanCellHeight))
  K=kC.join(J,"demTime_{}{}".format(D,e.format))
  n=kv.Times(kb(S),kb(W))
  s=kv.Con(n>=kT(n.mean),(kT(n.mean)-n),-(n-kT(n.mean)))
  u=kC.join(J,"min_{}{}".format(D,e.format))
  s.save(u)
  w.append(u)
 kr(w,J,"mergedRaster.img",pixel_type="32_BIT_FLOAT",number_of_bands=1)
 ka=kC.join(J,"mergedRaster.img")
 kM=kv.Con(kv.IsNull(ka),0,ka)
 kp=kC.join(kP,t)
 kH=kv.Plus(W,kM)
 kH.save(kp)
 kj()
 kq("snapRaster")
 kq("extent")
 _delTempData(X,J)
W=kN(0)
X=kN(1)
kP=kN(2)
t=kN(3)
if __name__=="__main__":
 kY=kz.now()
 kR=kz.strptime("2021-03-01 00:00:00","%Y-%m-%d %H:%M:%S")
 if kR>kY:
  main(W,X,kP,t)
 else:
  kE("failed")
# Created by pyminifier (https://github.com/liftoff/pyminifier)

