import os

xoff = 121.4558094
yoff = 31.4876612
zoff = 0
path = r'E:\cesium\objtest'
for root, dirs, files in os.walk(path):
    for f in files:
        if f[-3:] == "mtl":
            newmtl = ""
            mtlpath = os.path.join(root, f)
            print(mtlpath)
            with open(mtlpath, 'r')as rf:
                lines = rf.readlines()
                for line in lines:
                    if "	Tr " in line or "	d " in line:
                        pass
                    else:
                        newmtl += line
            with open(mtlpath, 'w')as rf:
                rf.write(newmtl)
        if f[-3:] == "obj":
            newobj = "powered by esri china hacter\n"
            objpath = os.path.join(root, f)
            print(objpath)
            with open(objpath, 'r')as rf:
                lines = rf.readlines()
                for line in lines:
                    if line[:2] == "v ":
                        temp = line.rstrip().split(" ")
                        newobj += "v %f %f %f\n" % (
                            float(temp[-3]) + xoff, float(temp[-2]) + yoff, float(temp[-1]) + zoff)
                    else:
                        newobj += line
            with open(objpath, 'w')as rf:
                rf.write(newobj)
print("finish!")
