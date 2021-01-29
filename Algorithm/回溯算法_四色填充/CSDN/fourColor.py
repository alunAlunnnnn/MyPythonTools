import arcpy
import math
import string
from numpy import *
InputFeature = arcpy.GetParameterAsText(0)
UniqueField = arcpy.GetParameterAsText(1)
ConnectField = arcpy.GetParameterAsText(2)
level = arcpy.GetParameterAsText(3)
#�ȼ��color�ֶ��Ƿ���ڣ��������򴴽����ֶ�
arcpy.AddField_management(InputFeature,"color","SHORT")

U = []
C = []
S = []
N = 0    #ͼ���ж���εĸ���
rows = arcpy.UpdateCursor(InputFeature)
#��ȡ����
if (level):
    for row in rows:
        N=N+1
        U.append(str(row.getValue(UniqueField)))
        C.append(str(row.getValue(ConnectField)))
        S.append(row.getValue(level))
else:
    for row in rows:
        N=N+1
        U.append(str(row.getValue(UniqueField)))
        C.append(str(row.getValue(ConnectField)))
        S.append(u'ȫ��')

sheng =list(set(S))
for each_sheng in sheng:
    u=[]
    c=[]
    arcpy.AddMessage(u'���ڼ��㣺'+each_sheng)
    for i in range(0,N):
        if (S[i]==each_sheng):
            u.append(U[i])
            c.append(C[i])
    #�����ڽӾ���
    n=len(u)
    mat=zeros([n,n],int)
    for i in range(0,n):
        #arcpy.AddMessage(c[i])
        tem = c[i].split(" ")
        for j in tem:
            if (j in u):
                ind=u.index(j)
                if(ind != i):
                    mat[i][ind]=1
                    #arcpy.AddMessage("mat["+str(i)+"]["+str(ind)+"]")
    #������ɫ
    maxColor=4
    colorIndex = ones(n,int)
    I=1
    colorI=1
    #arcpy.AddMessage(maxColor)
    while (I<n and I>=0):
        arcpy.AddMessage(str(I))
        while (colorI<=maxColor and I<n):
            for k in range(0,I):
                if(mat[k][I] and colorIndex[k]==colorI):
                    k=k-1
                    break
            if((k+1)==I):
                colorIndex[I]=colorI
                colorI=1
                I=I+1
            else:
                colorI=colorI+1
        if(colorI>maxColor):
            #arcpy.AddMessage(str(I))
            I=I-1
            colorI=colorIndex[I]+1


    i=0
    j=0
    rows = arcpy.UpdateCursor(InputFeature)
    for row in rows:
        if (S[j]==each_sheng):
            row.color = colorIndex[i]
            rows.updateRow(row)
            i=i+1
        j=j+1

