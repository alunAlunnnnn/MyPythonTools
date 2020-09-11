import logging

logs = r"E:\GIS算法\道格拉斯和普克算法\测试数据\log\log.txt"
logging.basicConfig(filename=logs, filemode="w",
                    format="%(levelname)s --- %(asctime)s --- %(message)s",
                    level=logging.DEBUG)

try:
    import math
    import os
    import functools
    import datetime
    import sys
    import sqlite3
    logging.info("All module needed have imported successfully")

except BaseException as e:
    logging.error(f"Lack of module. Error Message --- {e}")


sys.setrecursionlimit(1000000000)


# points type is not tuple
class pointError(Exception):
    pass


class calKError(Exception):
    pass


class GenerateSpatialIndexError(Exception):
    pass


class lineEquation:
    """
    usage: generate a line object
    :param args: accept as
     --- (fp_x, fp_y, fp_z), (lp_x, lp_y, lp_z), (ex_xin, ex_ymin, ex_xmax, ex_ymax)
    firstPoint --- fp
    lastPoint --- lp
    extent --- ex
    """

    def __init__(self, *args):
        # save all points
        self.points = []

        for each in args[:2]:
            if not isinstance(each, tuple):
                raise pointError

            self.points.append((float(each[0]), float(each[1]), float(each[2])))

        self.extent_xmin = args[2][0]
        self.extent_ymin = args[2][1]
        self.extent_xmax = args[2][2]
        self.extent_ymax = args[2][3]
        self.extent = args[2]

        # get point number, start with 1
        self.pntNum = len(args)

        # init pipe size
        self.pipeSize = None

        # set coord of start point and finish point
        self.x1 = self.points[0][0]
        self.y1 = self.points[0][1]
        self.z1 = self.points[0][2]
        self.x2 = self.points[-1][0]
        self.y2 = self.points[-1][1]
        self.z2 = self.points[-1][2]

        # extent available detect
        self._extentAvailableDetect()

        self.spaindex = None
        self.spaindex_row = None
        self.spaindex_col = None
        self.spaind_totalext = None

        self.calculateK_xy()
        self.calculateB_xy()

        self.calculateK_yz()
        self.calculateB_yz()

        self.calculateK_xz()
        self.calculateB_xz()

        self.generateEquation()


    # calculate k --- ( y2 - y1 ) / ( x2 - x1 )
    def calculateK_xy(self):
        if self.x1 == self.x2:
            self.k_xy = -999
            return self
        k = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.k_xy = k
        return self


    # calculate b --- y1 - k * x1
    def calculateB_xy(self):
        if self.k_xy == -999:
            self.b_xy = -999
        else:
            b = self.y1 - self.k_xy * self.x1
            self.b_xy = b
        return self


    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_yz(self):
        if self.y1 == self.y2:
            self.k_yz = -999
            return self
        k = (self.z2 - self.z1) / (self.y2 - self.y1)
        self.k_yz = k
        return self


    # calculate b --- z1 - k * y1
    def calculateB_yz(self):
        if self.k_yz == -999:
            self.b_yz = -999
        else:
            b = self.z1 - self.k_yz * self.y1
            self.b_yz = b
        return self


    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_xz(self):
        if self.x1 == self.x2:
            self.k_xz = -999
            return self
        k = (self.z2 - self.z1) / (self.x2 - self.x1)
        self.k_xz = k
        return self


    # calculate b --- z1 - k * y1
    def calculateB_xz(self):
        if self.k_xz == -999:
            self.b_xz = -999
        else:
            b = self.z1 - self.k_xz * self.x1
            self.b_xz = b
        return self


    # generate function equation
    def generateEquation(self):
        self.euqation_xy = '%s * x + %s' % (self.k_xy, self.b_xy)
        self.euqation_yz = '%s * x + %s' % (self.k_yz, self.b_yz)
        self.euqation_xz = '%s * x + %s' % (self.k_xz, self.b_xz)
        return self


    # calculate the intersect point
    def calculateIntersect(self, otherLineObj):
        if self.k_xy == otherLineObj.k_xy:
            self.intersect = 'false'
            otherLineObj.intersect = 'false'
            return None

        if self.b_xy == otherLineObj.b_xy:
            x = 0
            y = self.b_xy
        else:
            x = (otherLineObj.b_xy - self.b_xy) / (self.k_xy - otherLineObj.k_xy)
            y = self.k_xy * x + self.b_xy

        # detect whether the point in the rectangle of self line
        if x > self.extent_xmin and x < self.extent_xmax:
            if y > self.extent_ymin and y < self.extent_ymax:
                self.intersect = 'true'
            else:
                self.intersect = 'false'
        else:
            self.intersect = 'false'

        # detect whether the point in the rectangle of another line
        if x > otherLineObj.extent_xmin and x < otherLineObj.extent_xmax:
            if y > otherLineObj.extent_ymin and y < otherLineObj.extent_ymax:
                otherLineObj.intersect = 'true'
            else:
                otherLineObj.intersect = 'false'
        else:
            otherLineObj.intersect = 'false'

        return x, y


    # calculate z value in intersect x,y
    def calculateZCoord_yz(self, x, y):
        if self.k_yz != -999:
            z = self.k_yz * y + self.b_yz
        else:
            if self.k_xz != -999:
                z = self.k_xz * x + self.b_xz
            # the line is totally vertical to the floor(x, y)
            else:
                z = -999
        return z

    # calculate z value in intersect x,y
    def calculateZCoord_xz(self, x, y):
        if self.k_xz != -999:
            z = self.k_xz * x + self.b_xz
        else:
            if self.k_yz != -999:
                z = self.k_yz * y + self.b_yz
            else:
                z = -999
        return z

    # make sure the x_min, y_min is less or equal than x_max, y_max in extent
    def _extentAvailableDetect(self):
        assert int(self.extent_xmin * 10 ** 8) <= int(
            self.extent_xmax * 10 ** 8), "Error --- Extent of line object is not available"
        assert int(self.extent_ymin * 10 ** 8) <= int(
            self.extent_ymax * 10 ** 8), "Error --- Extent of line object is not available"


    def calDisFromPnt(self, firstPoint):
        """
        usage: 使用第一个点坐标及 k 、 b 值来生成 line 对象
        :param firstPoint: Tuple --- 点坐标（x, y, z）
        :return: Double --- 距离值
        """
        x, y, z = firstPoint[0], firstPoint[1], firstPoint[2]

        # get k value
        originK = self.k_xy
        if originK == -999:
            k = 0
        elif -0.0001 <= originK <= 0.0001:
            k = -999
        else:
            k = -1 / originK

        # origin line is y = n
        if k == -999:
            # x = n (k is infinity)
            originY = self.k_xy * x + self.b_xy
            dis_xy = abs(y - originY)
            interY = self.b_xy
            interX = y
            interZ = self.calculateZCoord_yz(interX, interY)
        # origin line is x = n (k is -999, b is -999)
        elif k == 0:
            dis_xy = abs(x - self.extent_xmin)
            interY = y
            interX = self.extent_xmin
            interZ = self.calculateZCoord_yz(interX, interY)
        else:
            b = y - k * x
            calX = self.extent_xmin
            calY = k * calX + b
            calZ = self.calculateZCoord_yz(calX, calY)

            ext = (min(x, calX), min(y, calY), max(x, calX), max(y, calY))

            # calculate the point of intersect between line and it's vertical line
            newlineObj = lineEquation((x, y, z), (calX, calY, calZ), ext)
            interX, interY = self.calculateIntersect(newlineObj)
            interZ = self.calculateZCoord_yz(interX, interY)

            # calculate x, y, z in the point of intersect between two line obj
            dis_xy = math.sqrt((y - interY) ** 2 + (x - interX) ** 2)

        if interZ != -999:
            dis = math.sqrt(dis_xy ** 2 + (z - interZ) ** 2)
        else:
            dis = dis_xy

        return dis


def getRunTime(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        print(f"Start function '{func.__name__}' at : {start}")
        res = func(*args, **kwargs)
        end = datetime.datetime.now()
        print("*" * 30)
        print(f"Start function '{func.__name__}' at : {start}")
        print(f"Finish function '{func.__name__}' at : {end}")
        print(f"Function '{func.__name__}' total cost  at : {end - start}")
        print("*" * 30)
        return res

    return _wrapper


def writeDataToDB(pntList, db, table):
    table += "_res"
    print("input", pntList)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS {table};")
    c.execute(f"CREATE TABLE IF NOT EXISTS {table}(X real, Y real, Z real); ")
    c.executemany(f"INSERT INTO {table} VALUES(?, ?, ?);", pntList)
    conn.commit()
    conn.close()
    return db


def readDataFromDB(db, table):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    data = c.execute(f"SELECT * FROM {table};").fetchall()
    print("db data is : ", data)

    return data


def DP(pntList, tolerance):
    """
    :param pntList: [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), ....]
    :return:
    """
    global resList
    global line, pntList1, pntList2
    if len(pntList) > 2:

        x_f, y_f, z_f = (pntList[0])
        x_l, y_l, z_l = (pntList[-1])
        ext = (min(x_f, x_l), min(y_f, y_l), max(x_f, x_l), max(y_f, y_l))

        # 实例化起点到终点的线
        line = lineEquation((x_f, y_f, z_f), (x_l, y_l, z_l), ext)

        for eachPnt in pntList[1:-1]:
            x, y, z = eachPnt
            dis = line.calDisFromPnt((x, y, z))
            # 筛出点到线距离小于容差的点集
            if dis < tolerance:
                # 遍历结束后，将此列表中的所有点位全部清除
                pntList.remove(eachPnt)

        maxDis = 0
        maxDisPntIndex = 0
        for i, eachPnt in enumerate(pntList[1:-1]):
            x, y, z = eachPnt
            dis = line.calDisFromPnt((x, y, z))
            if dis > maxDis:
                maxDis = dis
                maxDisPntIndex = i + 1

        # 找到距离最远的点，将线拆分为两条
        pntList1 = pntList[:maxDisPntIndex + 1]
        pntList2 = pntList[maxDisPntIndex:]
        if len(pntList1) > 2 and len(pntList2) > 2:
            DP(pntList1, tolerance)
            DP(pntList2, tolerance)
        elif len(pntList1) > 2 and len(pntList2) <= 2:
            DP(pntList1, tolerance)
        elif len(pntList2) > 2 and len(pntList1) <= 2:
            DP(pntList2, tolerance)
        else:
            resList = resList + pntList1
            return resList

    else:
        resList = resList + pntList
        return resList


@getRunTime
def main(tolerance, outdb, table):
    global resList
    pntDataList = readDataFromDB(outdb, table)
    pnts = (tuple(pntDataList[0]), tuple(pntDataList[-1]))
    print("start pnt, end pnt: ", pnts)

    logging.debug(f"Points coord information is {pntDataList}\n")
    logging.info("Step5 --- Process points with Douglas–Peucker algorithm")

    DP(pntDataList, tolerance)

    logging.debug(f"The result of points with DP algorithm are {resList}\n")
    logging.info("Step6 --- Create line feature class")

    if pnts[0] not in resList:
        print(1)
        resList.insert(0, pnts[0])
    if pnts[1] not in resList:
        print(2)
        resList.append(pnts[1])

    writeDataToDB(resList, outdb, table)


# 内置参数
resList = []


for i in range(1, 8):
    print("=" * 30)
    print(i)
    print("=" * 30)
    # 内置参数
    resList = []

    outdb = r"E:\GIS算法\道格拉斯和普克算法\测试数据\DPTest.db"
    table = fr"shp_{i}"
    tolerance = 0.001

    if __name__ == "__main__":
        main(tolerance, outdb, table)
        print(resList)
