import os


path=r'E:\cesium\cesium测试_0824\东方有线max\newobj'
# xoff=330000.0190
# yoff=347000.0875
xoff=13520542.39
yoff=3696391.63
# zoff=-1.924
for root,dirs,files in os.walk(path):
    for f in files:
        if f[-3:]=="mtl":
            newmtl="powered by esri china hacter\n"
            mtlpath=os.path.join(root,f)
            print(mtlpath)
            with open(mtlpath,'r')as rf:
                lines=rf.readlines()
                for line in lines:
                    if "Tr" in line:
                        pass
                    elif "map_Ke" in line:
                        pass
                    elif "map_d" in line:
                        pass
                    elif "map_Ka" in line and "tga" in line:
                        newmtl+=line[:-5]+".png\n"
                    elif "map_Kd" in line and "tga" in line:
                        newmtl+=line[:-5]+".png\n"
                    elif "	Ka" in line:
                        newmtl+="	Ka 1 1 1\n"
                    elif "	Kd" in line:
                        newmtl+="	Kd 1 1 1\n"
                    else:
                        newmtl+=line
            with open(mtlpath,'w')as rf:
                rf.write(newmtl)
        if f[-3:]=="obj":
            newobj="powered by esri china hacter\n"
            objpath=os.path.join(root,f)
            print(objpath)
            with open(objpath,'r')as rf:
                lines=rf.readlines()
                for line in lines:
                    if line[:2]=="v ":
                        temp=line.rstrip().split(" ")
                        newobj+="v %f %f %f\n"%(float(temp[-3])+xoff,float(temp[-2])+yoff,float(temp[-1])+zoff)
                    else:
                        newobj+=line
            with open(objpath,'w')as rf:
                rf.write(newobj)
print("finish!")
