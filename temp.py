import arcpy
from pyautocad import Autocad, APoint

data = r"E:\同济数据\DSM转高程点和等高线\fme\pro\高程点.shp"
dataf = r"E:\同济数据\DSM转高程点和等高线\fme\pro\data.txt"
dataf = r"E:\同济数据\DSM转高程点和等高线\fme\pro\data_part50.txt"
# acad = Autocad()

f = open(dataf, "w", encoding="utf-8")

with arcpy.da.SearchCursor(data, ["SHAPE@", "grid_code"]) as cur:
    i = 0
    j = 0
    for row in cur:
        i += 1
        if i % 3 == 0:
            continue
        j += 1
        x = row[0].centroid.X
        y = row[0].centroid.Y
        z = row[1]
        # p1 = APoint(x, y, z)
        # acad.model.AddText(p1)
        f.write(str(j) + ",," + str(x) + "," + str(y) + "," + str(z) + "\n")
        if j % 5000 == 0:
            print(i)

f.close()


