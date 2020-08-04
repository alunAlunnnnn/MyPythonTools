import pandas as pd
import os, datetime, functools
from numba import jit


def addMessage(mes):
    print(mes)
    # arcpy.AddMessage(mes)


def addWarning(mes):
    print(mes)
    # arcpy.AddMessage(mes)


def addError(mes):
    print(mes)
    # arcpy.AddMessage(mes)


# points type is not tuple
class pointError(Exception):
    pass


class calKError(Exception):
    pass


class lineEquation:
    def __init__(self, *args):
        # save all points
        self.points = []

        for each in args[:2]:
            if not isinstance(each, tuple):
                addMessage('Point coord is not tuple type')
                raise pointError

            self.points.append((float(each[0]), float(each[1]), float(each[2])))

        self.extent_xmin = args[2][0]
        self.extent_ymin = args[2][1]
        self.extent_xmax = args[2][2]
        self.extent_ymax = args[2][3]

        # get point number, start with 1
        self.pntNum = len(args)

        # set coord of start point and finish point
        self.x1 = self.points[0][0]
        self.y1 = self.points[0][1]
        self.z1 = self.points[0][2]
        self.x2 = self.points[-1][0]
        self.y2 = self.points[-1][1]
        self.z2 = self.points[-1][2]

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
            addError('ERROR --- calculate k_xy faild, x1 is equal to x2')
            self.k_xy = 0
            return self
            # raise calKError
        k = (self.y2 - self.y1) / (self.x2 - self.x1)
        self.k_xy = k
        return self

    # calculate b --- y1 - k * x1
    def calculateB_xy(self):
        b = self.y1 - self.k_xy * self.x1
        self.b_xy = b
        return self

    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_yz(self):
        if self.y1 == self.y2:
            # addError('ERROR --- calculate k_yz faild, y1 is equal to y2. y1 is %s' % self.y1)
            self.k_yz = 0
            return self
            # raise calKError
        k = (self.z2 - self.z1) / (self.y2 - self.y1)
        self.k_yz = k
        return self

    # calculate b --- z1 - k * y1
    def calculateB_yz(self):
        b = self.z1 - self.k_yz * self.y1
        self.b_yz = b
        return self

    # calculate k --- ( z2 - z1 ) / ( y2 - y1 )
    def calculateK_xz(self):
        if self.x1 == self.x2:
            # addError('ERROR --- calculate k_xz faild, x1 is equal to x2')
            self.k_xz = 0
            return self
            # raise calKError
        k = (self.z2 - self.z1) / (self.x2 - self.x1)
        self.k_xz = k
        return self

    # calculate b --- z1 - k * y1
    def calculateB_xz(self):
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
    def calculateZCoord_yz(self, y):
        z = self.k_yz * y + self.b_yz
        return z

    # calculate z value in intersect x,y
    def calculateZCoord_xz(self, x):
        z = self.k_xz * x + self.b_xz
        return z


# get run time for each function
def getRunTime(func):
    @functools.wraps(func)
    def _getRunTime(*args, **kwargs):
        start = datetime.datetime.now()
        res = func(*args, **kwargs)
        finish = datetime.datetime.now()
        cost = finish - start
        addMessage('start at: %s, finish at: %s \n cost : %s \n' % (start, finish, cost))
        return res
    return _getRunTime


@getRunTime
def featureClassMatch(df1, matchList, inFC1):
    # 遍历所有被匹配的数据表，检测是否有冲突
    inFC1 = inFC1[:-5]
    for eachMatched in matchList:
        print('*** 正在处理 %s --- %s ' % (inFC1, eachMatched[:-5]))
        start_time = datetime.datetime.now()
        print('*** 开始时间: ', start_time)

        # 写入检测结果
        interDetectFile = open(r'E:\南京管线\冲突excel数据抽取\冲突数据属性表\result\%s_%s.txt' % (inFC1, eachMatched), 'w')

        # 列含义
        # OBJECTID_1、Shape_Length、GJ_TEMP_、x_temp_f、y_temp_f、z_temp_f、x_temp_l
        # y_temp_l、z_temp_l、unic_id_、ext_xmin、ext_xmax、ext_ymin、ext_ymax
        df2 = pd.read_excel(eachMatched)

        # 迭代df1中每一行，与df2中每一行进行匹配
        df1_rowNum = df1.shape[0]
        df2_rowNum = df2.shape[0]

        # 检测数据的每一行
        for i in range(df1_rowNum):
            df1_rowDataList = df1.iloc[i].values

            # 获取 df1 当前数据的范围
            # df1_extent = (df1_rowDataList[10], df1_rowDataList[12],
            #               df1_rowDataList[11], df1_rowDataList[13])
            # df1_gj = df1_rowDataList[2]
            # df1_firstPnt = (df1_rowDataList[3], df1_rowDataList[4], df1_rowDataList[5])
            # df1_lastPnt = (df1_rowDataList[6], df1_rowDataList[7], df1_rowDataList[8])

            df1_extent = (df1_rowDataList[9], df1_rowDataList[11],
                          df1_rowDataList[10], df1_rowDataList[12])
            df1_gj = df1_rowDataList[1]
            df1_firstPnt = (df1_rowDataList[2], df1_rowDataList[3], df1_rowDataList[4])
            df1_lastPnt = (df1_rowDataList[5], df1_rowDataList[6], df1_rowDataList[7])

            line1 = lineEquation(df1_firstPnt, df1_lastPnt, df1_extent)

            # 被检测数据的每一行
            for j in range(df2_rowNum):
                df2_rowDataList = df2.iloc[j].values

                # 获取 df2 当前数据的范围
                # df2_extent = (df2_rowDataList[10], df2_rowDataList[12],
                #               df2_rowDataList[11], df2_rowDataList[13])
                # df2_gj = df2_rowDataList[2]
                # df2_firstPnt = (df2_rowDataList[3], df2_rowDataList[4], df2_rowDataList[5])
                # df2_lastPnt = (df2_rowDataList[6], df2_rowDataList[7], df2_rowDataList[8])

                df2_extent = (df2_rowDataList[9], df2_rowDataList[11],
                              df2_rowDataList[10], df2_rowDataList[12])
                df2_gj = df2_rowDataList[1]
                df2_firstPnt = (df2_rowDataList[2], df2_rowDataList[3], df2_rowDataList[4])
                df2_lastPnt = (df2_rowDataList[5], df2_rowDataList[6], df2_rowDataList[7])

                # 实例化 df2 线
                line2 = lineEquation(df2_firstPnt, df2_lastPnt, df2_extent)

                # 计算两线交点
                res = line1.calculateIntersect(line2)

                # 判断是否空间相交
                if line1.intersect == 'true' and line2.intersect == 'true':
                    if line1.k_xz != 0:
                        z1 = line1.calculateZCoord_xz(res[0])
                    else:
                        z1 = line1.calculateZCoord_yz(res[0])

                    if line2.k_xz != 0:
                        z_det = line2.calculateZCoord_xz(res[0])
                    else:
                        z_det = line2.calculateZCoord_yz(res[0])

                    z1 = float(z1)
                    z_det = float(z_det)
                    gj = float(df1_gj) * 0.75
                    gj_det = float(df2_gj) * 0.75

                    # if z1 > z_det:
                    #     if (z1 - gj / 2) < (z_det + gj_det / 2):
                    #         interDetectFile.write('data %s - %s and %s'
                    #                               ' - %s \n' % (inFC1, df1_rowDataList[9],
                    #                                             eachMatched[:-5], df2_rowDataList[9]))
                    # else:
                    #     if (z1 + gj / 2) > (z_det - gj_det / 2):
                    #         interDetectFile.write('data %s - %s and %s'
                    #                               ' - %s \n' % (inFC1, df1_rowDataList[9],
                    #                                             eachMatched[:-5], df2_rowDataList[9]))

                    if z1 > z_det:
                        if (z1 - gj / 2) < (z_det + gj_det / 2):
                            interDetectFile.write('data %s - %s and %s'
                                                  ' - %s \n' % (inFC1, df1_rowDataList[8],
                                                                eachMatched[:-5], df2_rowDataList[8]))
                    else:
                        if (z1 + gj / 2) > (z_det - gj_det / 2):
                            interDetectFile.write('data %s - %s and %s'
                                                  ' - %s \n' % (inFC1, df1_rowDataList[8],
                                                                eachMatched[:-5], df2_rowDataList[8]))

        end_time = datetime.datetime.now()
        print('*** 结束时间: ', end_time)
        print('*** 运行耗时: %s \n' % (end_time - start_time))
        interDetectFile.close()



@getRunTime
def main():
    # 遍历当前文件夹中除了最后一个外的所有excel
    for each in dataList[:-1]:
        # 保证被匹配的数据不重复
        index = matchList.index(each)
        matchList.pop(index)
        print('--- 现在正在匹配', each)


        # 读取匹配的excel文件
        df1 = pd.read_excel(each)

        # 如果管线类型一致则不检测冲突(数据名前两个字母相同, 前两个为XX的 按照后面的 TXX 和 YXX 来分)
        special = False
        if each[:2] == 'XX':
            special = True

        if special:
            lineType = each[3:6]
            matchList_temp = [eachData for eachData in matchList if eachData[3:6] != lineType]
        else:
            lineType = each[:2]
            matchList_temp = [eachData for eachData in matchList if eachData[:2] != lineType]

        print('--- 被匹配的数据总数还有 "%s" 个, 除去同类型的还有 %s 个: '
              '%s \n\n' % (len(matchList), len(matchList_temp), matchList_temp))

        # 迭代所有被匹配的数据，一一匹配
        featureClassMatch(df1, matchList_temp, each)



# dir = r'E:\南京管线\excel_new'
dir = r'E:\南京管线\冲突excel数据抽取\冲突数据属性表'
# resDir = r'E:\南京管线\excel_new\result'
resDir = r'E:\南京管线\冲突excel数据抽取\冲突数据属性表\result'

# 获取当前目录下的所有excel文件
os.chdir(dir)
dataList = os.listdir()
dataList.remove('result')

matchList = dataList[:]
print(matchList)
# print(len(matchList))

main()










# xls1 = r'E:\南京管线\excel_new\BM_BMG_LINE_Y.xlsx'
# xls2 = r'E:\南京管线\excel_new\DL_GDX_L_F.xlsx'
#
# df1 = pd.read_excel(xls1)
# df2 = pd.read_excel(xls2)
#
# rowLen1 = df1.shape[0]
# rowLen2 = df2.shape[0]
#
# for i in range(rowLen1):
#     data = df1.iloc[i].values
#     print(data)

