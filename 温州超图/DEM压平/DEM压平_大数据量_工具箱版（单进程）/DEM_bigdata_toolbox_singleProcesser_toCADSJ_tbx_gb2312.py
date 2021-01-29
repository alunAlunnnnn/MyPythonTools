import arcpy
Li=True
Lb=Exception
Lz=isinstance
Lc=tuple
Le=float
Lh=len
Lj=None
LM=int
Lg=abs
Lx=min
LT=max
Lu=print
Ly=round
Ll=arcpy.AddError
Lk=arcpy.GetParameterAsText
LE=arcpy.MosaicToNewRaster_management
Lr=arcpy.PolygonToRaster_conversion
LC=arcpy.SelectLayerByAttribute_management
LA=arcpy.SetProgressorPosition
Lo=arcpy.MakeFeatureLayer_management
LG=arcpy.SetProgressor
LW=arcpy.sa
LB=arcpy.ClearEnvironment
LP=arcpy.Delete_management
Ld=arcpy.ListRasters
Lm=arcpy.ListFeatureClasses
Ln=arcpy.CalculateField_management
LY=arcpy.DeleteField_management
LF=arcpy.AddField_management
LD=arcpy.da
LO=arcpy.ListFields
LH=arcpy.NumPyArrayToRaster
LJ=arcpy.Point
Lv=arcpy.RasterToNumPyArray
La=arcpy.Raster
LI=arcpy.env
import datetime
Lq=datetime
Lp=datetime
LQ=datetime.datetime
import functools
LX=functools.wraps
import os
LN=os.makedirs
LU=os.path
import math
Lw=math.sqrt
LI.overwriteOutput=Li
class NoFieldError(Lb):
 pass
class pointError(Lb):
 pass
class calKError(Lb):
 pass
class GenerateSpatialIndexError(Lb):
 pass
class lineEquation:
 def __init__(L,*R):
  L.points=[]
  for t in R[:2]:
   if not Lz(t,Lc):
    raise pointError
   L.points.append((Le(t[0]),Le(t[1]),Le(t[2])))
  L.extent_xmin=R[2][0]
  L.extent_ymin=R[2][1]
  L.extent_xmax=R[2][2]
  L.extent_ymax=R[2][3]
  L.extent=R[2]
  L.pntNum=Lh(R)
  L.pipeSize=Lj
  L.x1=L.points[0][0]
  L.y1=L.points[0][1]
  L.z1=L.points[0][2]
  L.x2=L.points[-1][0]
  L.y2=L.points[-1][1]
  L.z2=L.points[-1][2]
  L._extentAvailableDetect()
  L.spaindex=Lj
  L.spaindex_row=Lj
  L.spaindex_col=Lj
  L.spaind_totalext=Lj
  L.calculateK_xy()
  L.calculateB_xy()
  L.calculateK_yz()
  L.calculateB_yz()
  L.calculateK_xz()
  L.calculateB_xz()
  L.generateEquation()
 def calculateK_xy(L):
  if L.x1==L.x2:
   L.k_xy=-999
   return L
  k=(L.y2-L.y1)/(L.x2-L.x1)
  L.k_xy=k
  return L
 def calculateB_xy(L):
  if L.k_xy==-999:
   L.b_xy=-999
  else:
   b=L.y1-L.k_xy*L.x1
   L.b_xy=b
  return L
 def calculateK_yz(L):
  if L.y1==L.y2:
   L.k_yz=-999
   return L
  k=(L.z2-L.z1)/(L.y2-L.y1)
  L.k_yz=k
  return L
 def calculateB_yz(L):
  if L.k_yz==-999:
   L.b_yz=-999
  else:
   b=L.z1-L.k_yz*L.y1
   L.b_yz=b
  return L
 def calculateK_xz(L):
  if L.x1==L.x2:
   L.k_xz=-999
   return L
  k=(L.z2-L.z1)/(L.x2-L.x1)
  L.k_xz=k
  return L
 def calculateB_xz(L):
  if L.k_xz==-999:
   L.b_xz=-999
  else:
   b=L.z1-L.k_xz*L.x1
   L.b_xz=b
  return L
 def generateEquation(L):
  L.euqation_xy='%s * x + %s'%(L.k_xy,L.b_xy)
  L.euqation_yz='%s * x + %s'%(L.k_yz,L.b_yz)
  L.euqation_xz='%s * x + %s'%(L.k_xz,L.b_xz)
  return L
 def calculateIntersect(L,K):
  if L.k_xy==K.k_xy:
   L.intersect='false'
   K.intersect='false'
   return Lj
  if L.b_xy==K.b_xy:
   x=0
   y=L.b_xy
  else:
   x=(K.b_xy-L.b_xy)/(L.k_xy-K.k_xy)
   y=L.k_xy*x+L.b_xy
  if x>L.extent_xmin and x<L.extent_xmax:
   if y>L.extent_ymin and y<L.extent_ymax:
    L.intersect='true'
   else:
    L.intersect='false'
  else:
   L.intersect='false'
  if x>K.extent_xmin and x<K.extent_xmax:
   if y>K.extent_ymin and y<K.extent_ymax:
    K.intersect='true'
   else:
    K.intersect='false'
  else:
   K.intersect='false'
  return x,y
 def calculateZCoord_yz(L,x,y):
  if L.k_yz!=-999:
   z=L.k_yz*y+L.b_yz
  else:
   if L.k_xz!=-999:
    z=L.k_xz*x+L.b_xz
   else:
    z=-999
  return z
 def calculateZCoord_xz(L,x,y):
  if L.k_xz!=-999:
   z=L.k_xz*x+L.b_xz
  else:
   if L.k_yz!=-999:
    z=L.k_yz*y+L.b_yz
   else:
    z=-999
  return z
 def _extentAvailableDetect(L):
  assert LM(L.extent_xmin*10**8)<=LM(L.extent_xmax*10**8),"Error --- Extent of line object is not available"
  assert LM(L.extent_ymin*10**8)<=LM(L.extent_ymax*10**8),"Error --- Extent of line object is not available"
 def calDisFromPnt(L,firstPoint):
  x,y,z=firstPoint[0],firstPoint[1],firstPoint[2]
  V=L.k_xy
  if V==-999:
   k=0
  elif-0.0001<=V<=0.0001:
   k=-999
  else:
   k=-1/V
  if k==-999:
   S=L.k_xy*x+L.b_xy
   s=Lg(y-S)
   f=L.b_xy
   I=y
   a=L.calculateZCoord_yz(I,f)
  elif k==0:
   s=Lg(x-L.extent_xmin)
   f=y
   I=L.extent_xmin
   a=L.calculateZCoord_yz(I,f)
  else:
   b=y-k*x
   v=L.extent_xmin
   J=k*v+b
   H=L.calculateZCoord_yz(v,J)
   O=(Lx(x,v),Lx(y,J),LT(x,v),LT(y,J))
   D=lineEquation((x,y,z),(v,J,H),O)
   I,f=L.calculateIntersect(D)
   a=L.calculateZCoord_yz(I,f)
   s=Lw((y-f)**2+(x-I)**2)
  if a!=-999:
   F=Lw(s**2+(z-a)**2)
  else:
   F=s
  return F
class MyRas:
 def __init__(L,Y):
  L.inRas=Y
  L.getInfoFromRas(Y)
 def getInfoFromRas(L,Y):
  n=La(Y)
  L.sr=n.spatialReference
  L.extent=[n.extent.XMin,n.extent.YMin,n.extent.XMax,n.extent.YMax]
  L.extentObj=n.extent
  L.lowerLeft=n.extent.lowerLeft
  L.nodata=n.noDataValue
  if n.format.lower()=="imagine image":
   L.format=".img"
  elif n.format.lower()=="tiff":
   L.format=".tif"
  elif n.format.lower()=="fgdbr":
   L.format=""
  else:
   L.format=n.format
  L.maxValue=n.maximum
  L.minValue=n.minimum
  L.meanValue=n.mean
  L.meanCellWidth=n.meanCellWidth
  L.meanCellHeight=n.meanCellHeight
  L.dataPath=n.path
  L.pixelType=n.pixelType
  return L
 def toNDArray(L):
  m=Lv(L.inRas)
  return m
def getRunTime(func):
 @LX(func)
 def _wrapper(*R,**kwargs):
  d=LQ.now()
  Lu("Start run function {}, at {}".format(func.__name__,d))
  P=func(*R,**kwargs)
  B=LQ.now()
  W=B-d
  Lu("*"*16)
  Lu("Function {} run infomation".format(func.__name__,))
  Lu("Start: {}".format(d))
  Lu("End: {}".format(B))
  Lu("Cost: {}".format(W))
  Lu("*"*16)
  return P
 return _wrapper
def rasterProcessWithNumpy(Y,outRas):
 n=La(Y)
 sr=n.spatialReference
 Lu("nodata value: ",n.noDataValue)
 Lu("sr: ",sr.name)
 m=Lv(Y,nodata_to_value=Lj)
 Lu(m)
 G=LJ(n.extent.XMin,n.extent.YMin)
 o=n.meanCellWidth
 A=n.meanCellHeight
 C=LH(m,G,o,A,value_to_nodata=n.noDataValue)
 C.save(outRas)
def getFCOIDName(inFC):
 r=[t.name for t in LO(inFC)if t.type=="OID"][0]
 return r
def getFCOIDValue(inFC):
 E=getFCOIDName(inFC)
 k=[]
 with LD.SearchCursor(inFC,[E])as cur:
  for l in cur:
   k.append(l[0])
  del l
 return E,k
def _addConvertField(inFC):
 try:
  LF(inFC,"HSCONF_","SHORT")
 except:
  LY(inFC,"HSCONF_")
  LF(inFC,"HSCONF_","SHORT")
 if Lh([t.name for t in LO(inFC)if t.name=="HSCONF_"])>0:
  Ln(inFC,"HSCONF_","1","PYTHON_9.3")
  return inFC
 else:
  Lu("No Such Field Named HSCONF_ In Feature Class {}".format(inFC))
  raise NoFieldError
def _delTempData(inFC,p):
 try:
  LY(inFC,"HSCONF_")
 except:
  pass
 Q=Lj
 if LI.workspace:
  Q=LI.workspace
 LI.workspace=p
 q=Lm()
 X=Ld()
 for t in q:
  try:
   LP(t)
  except:
   pass
 for t in X:
  try:
   LP(t)
  except:
   pass
 if Q:
  LI.workspace=Q
 else:
  LB("workspace")
 q=Lm()
def makeTempDir(LS):
 p=LU.join(LS,"tmdRunDir_")
 if not LU.exists(p):
  LN(p)
 return p
def vailOutdataFormat(LS,U,N):
 if LS[-4:]==".gdb" or LS[-4:]==".mdb":
  U.format=""
  if N[-4:].lower()==".tif" or N[-4:].lower()==".img":
   N=N[:-4]
 return N
@getRunTime
def main(Y,i,LS,N):
 w=MyRas(Y)
 p=makeTempDir(LS)
 E,k=getFCOIDValue(i)
 i=_addConvertField(i)
 LI.snapRaster=Y
 LI.compression=Lj
 N=vailOutdataFormat(LS,w,N)
 b=LW.CreateConstantRaster(0,"INTEGER",w.meanCellWidth,w.extentObj)
 LG("step","processing...",0,Lh(k)+10,1)
 z=[]
 c=Lo(i)
 for e in k:
  LA()
  h=LC(c,"NEW_SELECTION","{} = {}".format(E,e))
  Lu(w.format)
  j=LU.join(p,"ras_{}{}".format(e,w.format))
  Lu(j)
  Lr(h,"HSCONF_",j,cellsize=Lx(w.meanCellWidth,w.meanCellHeight))
  g=LU.join(p,"demTime_{}{}".format(e,w.format))
  x=LW.Times(La(j),La(Y))
  T=LW.Con(x>=Ly(x.mean),(Ly(x.mean)-x),-(x-Ly(x.mean)))
  u=LU.join(p,"min_{}{}".format(e,w.format))
  T.save(u)
  z.append(u)
 LE(z,p,"mergedRaster.img",pixel_type="32_BIT_FLOAT",number_of_bands=1)
 Lt=LU.join(p,"mergedRaster.img")
 LI.extent=w.extentObj
 LR=LW.Con(LW.IsNull(Lt),0,Lt)
 LK=LU.join(LS,N)
 LV=LW.Plus(Y,LR)
 LV.save(LK)
 LA()
 LB("snapRaster")
 LB("extent")
 _delTempData(i,p)
Y=Lk(0)
i=Lk(1)
LS=Lk(2)
N=Lk(3)
if __name__=="__main__":
 Ls=LQ.now()
 Lf=LQ.strptime("2021-03-01 00:00:00","%Y-%m-%d %H:%M:%S")
 if Lf>Ls:
  main(Y,i,LS,N)
 else:
  Ll("failed")

