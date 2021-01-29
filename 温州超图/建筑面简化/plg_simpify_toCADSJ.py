import math
Aw=True
AR=print
Af=Exception
AK=isinstance
AW=tuple
Ag=float
Ax=len
AQ=None
Aa=int
Aj=round
Ao=False
AM=range
AU=str
AJ=min
AO=max
AF=abs
Ak=enumerate
AV=list
As=map
ui=math.sqrt
import os
uB=os.removedirs
uP=os.makedirs
uE=os.path
import arcpy
uy=arcpy.Point
uN=arcpy.CreateFeatureclass_management
ul=arcpy.SpatialReference
uS=arcpy.Describe
uh=arcpy.Delete_management
uc=arcpy.SimplifyPolygon_cartography
uv=arcpy.Eliminate_management
ud=arcpy.SelectLayerByAttribute_management
uY=arcpy.MakeFeatureLayer_management
ue=arcpy.CalculateField_management
um=arcpy.DeleteField_management
ur=arcpy.AddField_management
un=arcpy.AddError
uX=arcpy.AddWarning
ub=arcpy.AddMessage
uH=arcpy.GetParameterAsText
uz=arcpy.env
uD=arcpy.da
import functools
uL=functools.wraps
import datetime
ut=datetime.datetime
import sqlite3
AT=sqlite3.connect
uz.overwriteOutput=Aw
u=uH(0)
A=uH(1)
T=uH(2)
def _addMessage(mes):
 AR(mes)
 ub(mes)
def _addWarning(mes):
 AR(mes)
 uX(mes)
def _addError(mes):
 AR(mes)
 un(mes)
class pointError(Af):
 pass
class calKError(Af):
 pass
class GenerateSpatialIndexError(Af):
 pass
class lineEquation:
 def __init__(G,*R):
  G.points=[]
  for w in R[:2]:
   if not AK(w,AW):
    _addMessage('Point coord is not tuple type')
    raise pointError
   G.points.append((Ag(w[0]),Ag(w[1]),Ag(w[2])))
  G.extent_xmin=R[2][0]
  G.extent_ymin=R[2][1]
  G.extent_xmax=R[2][2]
  G.extent_ymax=R[2][3]
  G.extent=R[2]
  G.pntNum=Ax(R)
  G.pipeSize=AQ
  G.x1=G.points[0][0]
  G.y1=G.points[0][1]
  G.z1=G.points[0][2]
  G.x2=G.points[-1][0]
  G.y2=G.points[-1][1]
  G.z2=G.points[-1][2]
  G._extentAvailableDetect()
  G.spaindex=AQ
  G.spaindex_row=AQ
  G.spaindex_col=AQ
  G.spaind_totalext=AQ
  G.calculateK_xy()
  G.calculateB_xy()
  G.calculateK_yz()
  G.calculateB_yz()
  G.calculateK_xz()
  G.calculateB_xz()
  G.generateEquation()
 def calculateK_xy(G):
  if G.x1==G.x2:
   G.k_xy=-999
   return G
  k=(G.y2-G.y1)/(G.x2-G.x1)
  G.k_xy=k
  return G
 def calculateB_xy(G):
  if G.k_xy==-999:
   G.b_xy=-999
  else:
   b=G.y1-G.k_xy*G.x1
   G.b_xy=b
  return G
 def calculateK_yz(G):
  if G.y1==G.y2:
   G.k_yz=-999
   return G
  k=(G.z2-G.z1)/(G.y2-G.y1)
  G.k_yz=k
  return G
 def calculateB_yz(G):
  if G.k_yz==-999:
   G.b_yz=-999
  else:
   b=G.z1-G.k_yz*G.y1
   G.b_yz=b
  return G
 def calculateK_xz(G):
  if G.x1==G.x2:
   G.k_xz=-999
   return G
  k=(G.z2-G.z1)/(G.x2-G.x1)
  G.k_xz=k
  return G
 def calculateB_xz(G):
  if G.k_xz==-999:
   G.b_xz=-999
  else:
   b=G.z1-G.k_xz*G.x1
   G.b_xz=b
  return G
 def generateEquation(G):
  G.euqation_xy='%s * x + %s'%(G.k_xy,G.b_xy)
  G.euqation_yz='%s * x + %s'%(G.k_yz,G.b_yz)
  G.euqation_xz='%s * x + %s'%(G.k_xz,G.b_xz)
  return G
 def calculateIntersect(G,f):
  if G.k_xy==f.k_xy:
   G.intersect='false'
   f.intersect='false'
   return AQ
  if G.b_xy==f.b_xy:
   x=0
   y=G.b_xy
  else:
   x=(f.b_xy-G.b_xy)/(G.k_xy-f.k_xy)
   y=G.k_xy*x+G.b_xy
  if x>G.extent_xmin and x<G.extent_xmax:
   if y>G.extent_ymin and y<G.extent_ymax:
    G.intersect='true'
   else:
    G.intersect='false'
  else:
   G.intersect='false'
  if x>f.extent_xmin and x<f.extent_xmax:
   if y>f.extent_ymin and y<f.extent_ymax:
    f.intersect='true'
   else:
    f.intersect='false'
  else:
   f.intersect='false'
  return x,y
 def calculateZCoord_yz(G,x,y):
  if G.k_yz!=-999:
   z=G.k_yz*y+G.b_yz
  else:
   if G.k_xz!=-999:
    z=G.k_xz*x+G.b_xz
   else:
    z=-999
  return z
 def calculateZCoord_xz(G,x,y):
  if G.k_xz!=-999:
   z=G.k_xz*x+G.b_xz
  else:
   if G.k_yz!=-999:
    z=G.k_yz*y+G.b_yz
   else:
    z=-999
  return z
 def _extentAvailableDetect(G):
  assert Aa(G.extent_xmin*10**8)<=Aa(G.extent_xmax*10**8),"Error --- Extent of line object is not available"
  assert Aa(G.extent_ymin*10**8)<=Aa(G.extent_ymax*10**8),"Error --- Extent of line object is not available"
 def pointTouchDet(G,pnt,tolerance,k):
  K,W=pnt[0],pnt[1]
  g=AQ
  x=1
  Q=1
  a=Aj(Ag((k[2]-k[0])/x),6)+0.0001
  j=Aj(Ag((k[3]-k[1])/Q),6)+0.0001
  o=k[3]
  M=k[2]
  if(G.extent_xmax>k[2]+0.0001 or G.extent_ymax>k[3]+0.0001 or G.extent_xmin<k[0]-0.0001 or G.extent_ymin<k[1]-0.0001):
   if G.extent_xmax>k[2]+0.0001:
    AR("pnt xxxx1xxxx pnt")
   if G.extent_ymax>k[3]+0.0001:
    AR("pnt xxxx2xxxx pnt")
   if G.extent_xmin<k[0]-0.0001:
    AR("pnt xxxx3xxxx pnt")
   if G.extent_ymin<k[1]-0.0001:
    AR("pnt xxxx4xxxx pnt")
   _addError("Error --- generate spatial index for point failed, " "the point is ({}, {})".format(K,W))
   _addError("total extent is {}".format(k))
   raise GenerateSpatialIndexError
  U=Ao
  for i in AM(1,Q+1):
   if U:
    break
   if W>=o-i*j:
    J=AU(i)
    for j in AM(1,x+1):
     if K>=M-j*a:
      O=AU(j)
      g=(AU(i)+","+AU(j))
      U=Aw
      break
  assert g,"there are no spatial index in point"
  if g==G.spaindex:
   if(G.extent_xmin-tolerance<=K<=G.extent_xmax+tolerance and G.extent_ymin-tolerance<=W<=G.extent_ymax+tolerance):
    if G.k_xy==-999:
     if AJ(G.x1,G.x2)-tolerance<=K<=AO(G.x1,G.x2)+tolerance:
      if AJ(G.y1,G.y2)-tolerance<=W<=AO(G.y1,G.y2)+tolerance:
       return Aw
      else:
       return Ao
     else:
      return Ao
    elif G.k_xy==0:
     if AJ(G.y1,G.y2)-tolerance<=W<=AO(G.y1,G.y2)+tolerance:
      if AJ(G.x1,G.x2)-tolerance<=K<=AO(G.x1,G.x2)+tolerance:
       return Aw
      else:
       return Ao
     else:
      return Ao
    else:
     F=G.k_xy*K+G.b_xy
     if F-tolerance<=W<=F+tolerance:
      return Aw
     else:
      return Ao
   else:
    return Ao
  else:
   return Ao
 def generateSpatialIndex(G,k):
  x=1
  Q=1
  a=Aj(Ag((k[2]-k[0])/x),6)+0.0001
  j=Aj(Ag((k[3]-k[1])/Q),6)+0.0001
  o=k[3]
  M=k[2]
  G.spaind_totalext=k
  if(G.extent_xmax>k[2]+0.0001 or G.extent_ymax>k[3]+0.0001 or G.extent_xmin<k[0]-0.0001 or G.extent_ymin<k[1]-0.0001):
   if G.extent_xmax>k[2]+0.0001:
    AR("xxxx1xxxx")
   if G.extent_ymax>k[3]+0.0001:
    AR("xxxx2xxxx")
   if G.extent_xmin<k[0]-0.0001:
    AR("xxxx3xxxx")
   if G.extent_ymin<k[1]-0.0001:
    AR("xxxx4xxxx")
   _addError("Error --- generate spatial index failed, " "line object's extent is not in total extent. " "the line's first point is ({}, {})".format(G.x1,G.y1))
   _addError("total extent is {}".format(k))
   _addError("ply extent is {}".format(G.extent))
   raise GenerateSpatialIndexError
  U=Ao
  for i in AM(1,Q+1):
   if U:
    break
   if G.extent_ymax>=o-i*j:
    G.spaindex_row=AU(i)
    for j in AM(1,Q+1):
     if G.extent_xmax>=M-j*a:
      G.spaindex_col=AU(j)
      G.spaindex=(AU(i)+","+AU(j))
      U=Aw
      break
  return G
 def setPipeSize(G,V):
  if AK(V,Aa)or AK(V,Ag):
   G.pipeSize=V
  else:
   _addWarning("Warning --- pipe size is not a number type, pipe size init failed")
   G.pipeSize=AQ
 def calDisFromPnt(G,firstPoint):
  x,y,z=firstPoint[0],firstPoint[1],firstPoint[2]
  s=G.k_xy
  if s==-999:
   k=0
  elif-0.0001<=s<=0.0001:
   k=-999
  else:
   k=-1/s
  if k==-999:
   p=G.k_xy*x+G.b_xy
   I=AF(y-p)
   C=G.b_xy
   q=y
   i=G.calculateZCoord_yz(q,C)
  elif k==0:
   I=AF(x-G.extent_xmin)
   C=y
   q=G.extent_xmin
   i=G.calculateZCoord_yz(q,C)
  else:
   b=y-k*x
   E=G.extent_xmin
   P=k*E+b
   B=G.calculateZCoord_yz(E,P)
   D=(AJ(x,E),AJ(y,P),AO(x,E),AO(y,P))
   z=lineEquation((x,y,z),(E,P,B),D)
   q,C=G.calculateIntersect(z)
   i=G.calculateZCoord_yz(q,C)
   I=ui((y-C)**2+(x-q)**2)
  if i!=-999:
   H=ui(I**2+(z-i)**2)
  else:
   H=I
  return H
def addField(inData,N,y):
 try:
  ur(inData,N,y)
 except:
  um(inData,N)
  ur(inData,N,y)
 return inData
def makeTempDir(A):
 b=uE.join(A,"tmdRunDir_")
 if not uE.exists(b):
  uP(b)
 return b
def simpiyPlg(u,A,T):
 X=[]
 addField(u,"area_","DOUBLE")
 ue(u,"area_","!shape.area@meters!","PYTHON3")
 n=uY(u,"splg_")
 ud(n,"NEW_SELECTION","area_ < 50")
 b=makeTempDir(A)
 r=uE.join(b,"plgSim_1.shp")
 uv(n,r)
 X.append(r)
 n=uY(r,"splg_1")
 ud(n,"NEW_SELECTION","area_ < 100")
 m=uE.join(b,"plgSim_2.shp")
 uv(n,m)
 X.append(m)
 n=uY(m,"splg_2")
 ud(n,"NEW_SELECTION","area_ < 150")
 e=uE.join(b,"plgSim_3.shp")
 uv(n,e)
 X.append(e)
 Y=uE.join(A,T)
 uc(e,Y,"POINT_REMOVE","0.1 Meters",collapsed_point_option="NO_KEEP")
 v=["InPoly_FID","SimPgnFlag","MaxSimpTol","MinSimpTol"]
 for c in v:
  try:
   um(Y,c)
  except:
   pass
 for w in X:
  try:
   uh(w)
  except:
   pass
 try:
  uB(b)
 except:
  pass
simpiyPlg(u,A,T)
def getRunTime(func):
 @uL(func)
 def _wrapper(*R,**kwargs):
  h=ut.now()
  AR("Start function '{}' at : {}".format(func.__name__,h))
  S=func(*R,**kwargs)
  l=ut.now()
  AR("*"*30)
  AR("Start function '{}' at : {}".format(func.__name__,h))
  AR("Finish function '{}' at : {}".format(func.__name__,l))
  AR("Function '{}' total cost  at : {}".format(func.__name__,l-h))
  AR("*"*30)
  return S
 return _wrapper
def addCoordField(uf):
 N=["id_","x_cen_","y_cen_","z_cen_"]
 y=["LONG","DOUBLE","DOUBLE","DOUBLE"]
 L=["f()","!shape.centroid.X!","!shape.centroid.Y!","!shape.centroid.Z!"]
 t="""a = -1
def f():
    global a
    a += 1
    return a"""
 uA=N.index("z_cen_")
 uT=N.index("id_")
 uG=uE.basename(uf)
 uw=uE.dirname(uf)
 if not uz.workspace:
  uz.workspace=uw
 uR=uS(uf)
 for i,c in Ak(N):
  AR(c)
  try:
   ur(uf,c,y[i],field_is_nullable=Aw)
  except:
   um(uf,c)
   ur(uf,c,y[i],field_is_nullable=Aw)
  if i==uT:
   ue(uf,c,L[i],"PYTHON3",t)
  else:
   if uR.hasZ:
    ue(uf,c,L[i],"PYTHON3")
   else:
    if i!=uA:
     ue(uf,c,L[i],"PYTHON3")
    else:
     ue(uf,c,"0","PYTHON3")
def writeDataToDB(uO,db,table):
 AR("input",uO)
 uW=AT(db)
 c=uW.cursor()
 c.execute("DROP TABLE IF EXISTS {};".format(table))
 c.execute("CREATE TABLE IF NOT EXISTS {}(X real, Y real, Z real); ".format(table))
 c.executemany("INSERT INTO {} VALUES(?, ?, ?);".format(table),uO)
 uW.commit()
 uW.close()
 return db
def readDataFromDB(db,table):
 uW=AT(db)
 c=uW.cursor()
 ug=c.execute("SELECT * FROM {};".format(table)).fetchall()
 AR("db data is : ",ug)
 return ug
def DP(uO,tolerance):
 global up
 if Ax(uO)>2:
  ux,uQ,ua=(uO[0])
  uj,uo,uM=(uO[-1])
  D=(AJ(ux,uj),AJ(uQ,uo),AO(ux,uj),AO(uQ,uo))
  uU=lineEquation((ux,uQ,ua),(uj,uo,uM),D)
  for uJ in uO[1:-1]:
   x,y,z=uJ
   H=uU.calDisFromPnt((x,y,z))
   if H<tolerance:
    uO.remove(uJ)
  uF=0
  uk=0
  for i,uJ in Ak(uO[1:-1]):
   x,y,z=uJ
   H=uU.calDisFromPnt((x,y,z))
   if H>uF:
    uF=H
    uk=i+1
  uV=uO[:uk+1]
  us=uO[uk:]
  if Ax(uV)>2 and Ax(us)>2:
   DP(uV,tolerance)
   DP(us,tolerance)
  elif Ax(uV)>2 and Ax(us)<=2:
   DP(uV,tolerance)
  elif Ax(us)>2 and Ax(uV)<=2:
   DP(us,tolerance)
  else:
   up=up+uV
   return up
 else:
  up=up+uO
  return up
def createLineFC(uO,outputData):
 uz.outputZFlag="Enabled"
 ug=uO
 uw=uE.dirname(outputData)
 uG=uE.basename(outputData)
 sr=ul(4326)
 uN(uw,uG,"POINT",has_z="ENABLED",spatial_reference=sr)
 with uD.InsertCursor(outputData,["SHAPE@"])as uq:
  uC=[uy(*w)for w in[AV(As(Ag,pnt))for pnt in ug]]
  for uJ in uC:
   uq.insertRow([uJ])
# Created by pyminifier (https://github.com/liftoff/pyminifier)

