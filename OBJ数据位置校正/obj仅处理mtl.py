import os


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
print("finish!")
