import functools
import math
import arcpy
import re
import sys
import pandas as pd
import os
import openpyxl


class dataTypeNotAvailable(Exception):
    pass


class fileExtionNotAvailable(Exception):
    pass


class myXYLine:
    """
    usage: 平面线段类，用以实例化仅有首尾两点的线段
    """

    def __init__(self, startPnt, endPnt):
        """
        usage: 该类仅支持平面的 x, y 坐标，不支持带有 z 值线
        :param startPnt: tuple or list, like (x1, y1)
        :param endPnt: tuple or list, like (x2, y2)

        该类的对象具有如下属性：
            * x1, y1, x2, y2 —— 数据的坐标值
            * length —— 线路长度
            * center —— 由起终点计算的中间点
            * centroid —— 由extent计算点中心点（在线段中与center相同）
            * directionRadian —— 线段的方向角（0~2pi）
            * directionDegree —— 线段的方向角（0~360）
            * normal —— 法线的坐标二元组，((xc, yc), (xn, yn))
                xc, yc: 中心点的 x, y;
                xn, yn: 法线长度为1的点坐标;
            * normalDegree —— 法线角度（其中一个，另外一个为 180 + 该度数）
        """

        # 验证传入的元组为数值型元组，若非尝试将其中数据转为数值，无法转换则抛出 “dataTypeNotAvailable” 异常
        # 并且将坐标值限定到小数点后9位，进行四舍五入
        startPnt = myXYLine.coordTupleTest(startPnt)
        endPnt = myXYLine.coordTupleTest(endPnt)

        # 初始话坐标属性
        self.x1, self.y1 = startPnt
        self.x2, self.y2 = endPnt
        # 计算长度，并添加 .length 属性
        self._calGeometry()

    @staticmethod
    def coordTupleTest(coordTup):
        newCoordTup = []
        for each in coordTup:
            if not isinstance(each, (int, float)):
                try:
                    newCoordTup.append(round(float(each), 9))
                except:
                    print("Error --- ")
                    raise dataTypeNotAvailable
            else:
                newCoordTup.append(round(each, 9))
        return newCoordTup

    def _calGeometry(self):
        # 长度
        self.length = math.sqrt((self.y2 - self.y1) ** 2 + (self.x2 - self.x1) ** 2)
        # 中间点
        self.center = ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
        # 中心点
        self.centroid = ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
        # 方向弧度
        self.directionRadian = math.atan2((self.y1 - self.y2), (self.x1 - self.x2)) + math.pi
        # 方向角度
        self.directionDegree = math.degrees(math.atan2((self.y1 - self.y2), (self.x1 - self.x2))) + 180
        # 直线的k
        if self.directionDegree == 90 or self.directionDegree == -90 or \
                self.directionDegree == 270 or self.directionDegree == -270:
            self.k = "infinity"
        elif self.directionDegree == 180 or self.directionDegree == 180 or self.directionDegree == 360:
            self.k = 0
        else:
            self.k = math.tan(self.directionRadian)
        # 直线的b
        if self.k != "infinity":
            self.b = self.y2 - self.k * self.x2
        else:
            self.b = 0
        # 线段法线（长度为1单位，由终点向外指向），用起终点元组表组，避免直接实例化后的无限调用（法线再求法线....）
        self.calNormalLine()
        return None

    def calNormalLine(self):
        # 以中点作为一点，求其中垂线
        xc, yc = self.center

        # 求法线参数
        self.normalDegree = self.directionDegree + 90
        self.normalRadian = math.radians(self.normalDegree)
        yNormal = math.sin(self.normalRadian) + yc
        xNormal = math.sqrt(1 - (yNormal - yc) ** 2) + xc
        self.normal = ((xc, yc), (xNormal, yNormal))
        return None

    def calDisAndInterPnt(self, tarPnt):
        """
        usage: 用于计算某点到线的最近距离
        :param tarPnt: tuple, (x, y)
        :return: (交点坐标元组， 距离) --- ((xInter, yInter), distance)
        """
        xt, yt = tarPnt
        # 法线的k 与 垂线相同
        norLineObj = myXYLine(*self.normal)

        # 线段本身是否为竖直线
        if self.k == "infinity":
            dis = abs(xt - self.x1)
            pntInter = (self.x1, yt)
        # 线段本身为水平线，则法线为竖直线
        elif norLineObj.k == "infinity":
            dis = abs(yt - self.y1)
            pntInter = (xt, self.y1)
        else:
            xInter = (norLineObj.b - self.b) / (self.k - norLineObj.k)
            yInter = self.k * xInter + self.b
            pntInter = (xInter, yInter)
            dis = math.sqrt((yInter - yt) ** 2 + (xInter - xt) ** 2)
        return (pntInter, dis)


def getLineWKT(inFC, upOrDownFieldName):
    """
    usage: 获取输入的线要素类中每条线要素的坐标点集
    :param inFC: str, 输入不带z值的线要素类
    :param upOrDownFieldName: str, 字段名，用以标识哪个字段区分上下行
    :return: list, [[”线1上行或下行“, [x1, y1], [x2, y2], .... ], [”线2上行或下行“, [x1, y1], [x2, y2], .... ], ....]
    """
    plyCoordList = []
    with arcpy.da.SearchCursor(inFC, ["SHAPE@WKT", upOrDownFieldName]) as cur:
        for row in cur:
            wkt = row[0]
            wkt = re.findall(r"-?\d+\.?\d+\s?-?\d+\.?\d+", wkt)
            coord = [list(map(float, eachPnt.split(" "))) for eachPnt in wkt]
            direction = row[1]
            coord.insert(0, direction)
            plyCoordList.append(coord)
            print(coord)
    print(plyCoordList)
    return plyCoordList


def readSplitPntFromXLS(xls):
    # 确保文件类型为 .xlsx
    data, ext = os.path.splitext(xls)
    if ext == ".xls":
        # todo 目前需要将一个xls的多个sheet各自读取并写入到新的xlsx中
        df = pd.read_excel(xls)
        xlsx = data + ".xlsx"

        if os.path.exists(xlsx):
            os.remove(xlsx)

        df.to_excel(xlsx, index=False)
    elif ext != ".xlsx":
        print("Error --- the extension of input file not in (.xls, .xlsx)")
        raise fileExtionNotAvailable
    else:
        xlsx = xls

    wb = openpyxl.load_workbook(xlsx)
    shts = wb.sheetnames
    print(shts)

    xlsxDataList = []
    for eachSht in shts:
        shtDataList = []
        # 每个单独的sheet
        sht = wb[eachSht]
        rowMax = sht.max_row
        # 有效数据从第三行开始
        for i in range(3, rowMax + 1):
            dataDict = {}
            oId, oStart, oEnd, oDir = (sht.cell(i, 1).value, sht.cell(i, 2).value,
                                       sht.cell(i, 3).value, sht.cell(i, 4).value)
            (dataDict["id"], dataDict["start"],
             dataDict["end"], dataDict["direc"]) = (oId, oStart, oEnd, oDir)
            shtDataList.append(dataDict)
        xlsxDataList.append(shtDataList)
    print(xlsxDataList)


# todo 现在已经获取了excel中需要打断的数据，明天按打断的数据 先做复制 6 个图层，每个图层打断一次
# todo 图层集合拆分掉




inFC = r"F:\工作项目\项目_上海申通\数据_cass打断线\ditie\zhengxian.gdb\zhengxian"
upOrDownFieldName = "行别"
xls = r"F:\工作项目\项目_上海申通\数据_cass打断线\地铁正线分段表序号.xlsx"

# plyCoord = getLineWKT(inFC, upOrDownFieldName)

# 调试用
readSplitPntFromXLS(xls)

# line1 = myXYLine((1, 1), (2, 1))
# # line1 = myXYLine((0, 0), (0, 1))
# pnt, dis = line1.calDisAndInterPnt((0.5, 0.5))
# print("normal: ", line1.normal)
# print("k: ", line1.k)
# print("b: ", line1.b)
# print("directionDegree: ", line1.directionDegree)
# print("directionRadian: ", line1.directionRadian)
# print("normalDegree: ", line1.normalDegree)
# print("pnt: ", pnt)
# print("dis: ", dis)
