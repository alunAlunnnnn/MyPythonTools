import os

path = r'E:\cesium\cesium测试_0824\东方有线max\obj\OBJ_YQ'
# xoff=330000.0190
# yoff=347000.0875
xoff = 13520542.39
yoff = 3696391.63
zoff = 0
for root, dirs, files in os.walk(path):
    for f in files:
        if f[-3:] == "mtl":
            newmtl = ""
            mtlpath = os.path.join(root, f)
            print(mtlpath)
            with open(mtlpath, 'r')as rf:
                lines = rf.readlines()
                for line in lines:
                    if "	d " in line or "	Tr " in line:
                        pass
                    else:
                        newmtl += line
            with open(mtlpath, 'w')as rf:
                rf.write(newmtl)
        if f[-3:] == "obj":
            newobj = ""
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
