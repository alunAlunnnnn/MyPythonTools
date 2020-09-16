import os

path = r'E:\cesium\obj测试\fly_obj'
for root, dirs, files in os.walk(path):
    for f in files:
        if f[-3:] == "mtl":
            newmtl = "powered by esri china hacter\n"
            mtlpath = os.path.join(root, f)
            print(mtlpath)
            with open(mtlpath, 'r')as rf:
                lines = rf.readlines()
                for line in lines:
                    if "Tr" in line:
                        pass
                    elif "map_Ke" in line:
                        pass
                    elif "map_d" in line:
                        pass
                    elif "map_Ka" in line and "tga" in line:
                        newmtl += line[:-5] + ".png\n"
                    elif "map_Kd" in line and "tga" in line:
                        newmtl += line[:-5] + ".png\n"
                    elif "	Ka" in line:
                        newmtl += "	Ka 1 1 1\n"
                    elif "	Kd" in line:
                        newmtl += "	Kd 1 1 1\n"
                    else:
                        newmtl += line
            with open(mtlpath, 'w')as rf:
                rf.write(newmtl)
print("finish!")
