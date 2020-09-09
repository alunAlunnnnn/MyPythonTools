import json
import os
import requests
import math
import logging

try:
    import arcpy
    ESRI_LIB = True
except:
    ESRI_LIB = False

if ESRI_LIB:
    arcpy.env.overwriteOutput = True

try:
    import shapefile
    SHP_LIB = True
except:
    SHP_LIB = False


'''
官网信息
官网帮助url: http://lbsyun.baidu.com/index.php?title=webapi/directionlite-v1
API: http://api.map.baidu.com/directionlite/v1/driving?origin=40.01116,116.339303&destination=39.936404,116.452562&ak=您的AK  //GET请求
baseURL: http://api.map.baidu.com/directionlite/v1/driving
params: 
- 必选参数
- origin=40.01116,116.339303    double, double
- destination=39.936404,116.452562    double, double
- ak=您的AK    string

* 可选参数
* coord_type    string    输入坐标的类型，默认 bd09ll。 支持 wgs84、bd09ll（百度经纬度）、bd09mc（百度墨卡托投影）、gcj02（国测02）
* waypoints='40.465,116.314|40.232,116.352|40.121,116.453'    string    支持5个以内的途径点
* ret_coordtype    string    返回的坐标值的类型，bd09ll（默认）、gcj02
* sn    string    当用户AK设置为sn时，填写此值
* timestamp    string    时间戳，配合sn使用，填sn时候，此值必填
* tactics=0 / 1 / 2 / 3    int    路径偏好，0 --- 常规路线、 1 --- 不走高速、 2 --- 躲避拥堵、 3 --- 距离较短
* gps_direction    int64    用于提高计算的精度。起点的定位方向，车头方向与正北方向的夹角，当speed>1.5 m/s 且 gps_direction 存在时，该参数生效
* radius    float    起点定位精度，取值范围[0, 2000]
* speed    float    起点车辆速度，单位 m/s ，用于配合gps_direction确定车辆行走方向与道路方向的符合性


返回对象属性：
- status
- message
- routes    返回的方案集
-- distance    方案的距离，单位 米
-- duration    路线耗时，单位 秒
-- toll    路线的过路费
-- traffic_condition    路线整体情况评价，0 --- 无路况、 1 --- 畅行、 2 --- 缓行、 3 --- 拥堵、 4 --- 严重拥堵

-- steps    路线分段
--- leg_index    途径点序号，用于标识step所属的途径点
--- direction    进入道路的角度，12分位图，0 --- [345°, 15°] 其他顺时针递增
--- turn    转向
--- distance    路段距离
--- duration    路段耗时
--- road_types    路段类型
--- instruction    路段描述
--- start_location.lng/.lat    分段起点的经纬度
--- end_location.lng/.lat    分段终点的经纬度
--- path    分段坐标
--- traffic_condition   分段路况详情


- result    
- origin.lng
- origin.lat
- destination.lng
- destination.lat


骑行API: http://api.map.baidu.com/directionlite/v1/riding?origin=40.01116,116.339303&destination=39.936404,116.452562&ak=您的AK   //GET请求

步行API: http://api.map.baidu.com/directionlite/v1/walking?origin=40.01116,116.339303&destination=39.936404,116.452562&ak=您的AK  //GET请求

公交API: http://api.map.baidu.com/directionlite/v1/transit?origin=40.056878,116.30815&destination=31.222965,121.505821&ak=您的AK  //GET请求

'''

class ModuleNotExistsError(Exception):
    pass


class BaiDuRouteLite:
    def __init__(self):
        self.response = None

    # 常量定义
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626  # π
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 偏心率平方

    # 发送请求，获取驾车路径规划
    def getDrivingRoute_ip(self, originCoord, destCoord, coord_type, tactics=0, waypoints=None):
        """
        usage: 数据获取主函数，向百度地图服务器发送请求，以获取其路径规划（lite版）数据
        :param originCoord: 起点坐标，（维度， 经度） —— tuple or list, format --- (longitude, latitude)
        :param destCoord: 终点坐标，（维度， 经度） —— tuple or list, format --- (longitude, latitude)
        :param coord_type: 传入点坐标的坐标系，默认百度 09II —— 支持 bd09ll：百度经纬度坐标， bd09mc：百度墨卡托坐标， gcj02：国测局加密坐标， wgs84：gps设备获取的坐标
        :param tactics: 规划路线的偏好 —— 支持 0、1、2、3， 代表 常规、不走高速、躲避拥堵、距离较短
        :param waypoints: 必须要经过的点位，最多支持5个 —— 不同点位用 '|' 作为分割， 如 40.465,116.314|40.232,116.352|40.121,116.453
        :return: 查询结果对象（JSON）
        """

        baseurl = 'http://api.map.baidu.com/directionlite/v1/driving'

        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'

        # 无途径点的请求参数
        if not waypoints:
            para = {
                'ak': 'KRx4yS11gIPRDIiNgHIrcirf4ZsMKGhw',
                'origin': '%s,%s' % (originCoord[1], originCoord[0]),
                'destination': '%s,%s' % (destCoord[1], destCoord[0]),
                'output': 'json',
                'coord_type': coord_type,
                'tactics': tactics
            }
        # 有途径点的请求参数
        else:
            para = {
                'ak': 'KRx4yS11gIPRDIiNgHIrcirf4ZsMKGhw',
                'origin': '%s,%s' % (originCoord[1], originCoord[0]),
                'destination': '%s,%s' % (destCoord[1], destCoord[0]),
                'output': 'json',
                'coord_type': coord_type,
                'tactics': tactics,
                'waypoints': waypoints
            }

        # 发送get请求，参数拼接入url，明码传输
        self.response = requests.get(baseurl, headers={'User-Agent': ua}, params=para)
        self.coord_type = coord_type
        return self

    # 解析响应
    def parseRouteRes(self):
        # 以json形式读取数据
        data = self.response.json()

        with open(r"E:\百度地图API\测试\路径规划lite结果数据\json\test.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(data))

        self.route_distance, self.route_duration, self.traffic_condition, self.toll, self.steps = [], [], [], [], []

        for eachRoute in data["result"]["routes"]:
            self.route_distance.append(eachRoute['distance'])
            self.route_duration.append(eachRoute['duration'])
            self.traffic_condition.append(eachRoute['traffic_condition'])
            self.toll.append(eachRoute['toll'])
            self.steps.append(eachRoute['steps'])

        return self

    # 生成路线要素类
    def generateRouteFeatureClass(self, outputData):
        # 坐标转换
        # if self.coord_type == 'wgs84':
        #     arcpy.CreateFeatureclass_management()
        ply_fc_total = []
        ply_fc_total_attr = []
        for routeNum, eachRoute in enumerate(self.steps):
            routeNum += 1
            ply_fc = []
            ply_fc_attr = []
            for eachStep in eachRoute:
                ply_part_attr = {}
                attr_legIndex = eachStep['leg_index']
                attr_distance = eachStep['distance']
                attr_duration = eachStep['duration']
                attr_direction = eachStep['direction']
                attr_turn = eachStep['turn']
                attr_road_type = eachStep['road_type']

                # 获取导航描述，并清除加粗标记
                attr_instruction = eachStep['instruction'].replace('<b>', '').replace('<\/b>', '')

                ply_part_attr['leg_index'] = attr_legIndex
                ply_part_attr['distance'] = attr_distance
                ply_part_attr['duration'] = attr_duration
                ply_part_attr['direction'] = attr_direction
                ply_part_attr['turn'] = attr_turn
                ply_part_attr['road_type'] = attr_road_type
                ply_part_attr['instruction'] = attr_instruction

                # 路径点集
                geo_metry = eachStep["path"].split(";")

                # 每段step线
                ply_part = []

                for eachPnt in geo_metry:
                    pnt_x = float(eachPnt.split(",")[0])
                    pnt_y = float(eachPnt.split(",")[1])
                    ply_part.append([pnt_x, pnt_y])

                # 线要素类
                ply_fc.append(ply_part)
                ply_fc_attr.append(ply_part_attr)

            # 多个线要素集合
            ply_fc_total.append(ply_fc)
            ply_fc_total_attr.append(ply_fc_attr)
        self.ply_fc_total = ply_fc_total
        self.ply_fc_total_attr = ply_fc_total_attr

        return self

    def generateLine_ESRI(self):
        # make sure the module named arcpy is exists
        assert ESRI_LIB, "ERROR --- There is no module named arcpy"

        features = []
        print("*" * 30)
        print(self.ply_fc_total)
        for i, eachFC in enumerate(self.ply_fc_total):
            for plyFC in eachFC:
                print("=" * 30)
                print(plyFC)
                features.append(arcpy.Polyline(arcpy.Array(
                    [arcpy.Point(*coord) for coord in plyFC]
                )))

            baseDir = os.path.dirname(outputData)
            baseName = os.path.basename(outputData)
            if ".gdb" in baseDir or ".mdb" in baseDir or ".sde" in baseDir:
                if ".shp" in baseName:
                    baseName = baseName.split(".shp")[0]

                baseName_noext = baseName
            else:
                if ".shp" not in baseName:
                    baseName_noext = baseName
                    baseName = baseName + ".shp"
                else:
                    baseName_noext = baseName.split(".shp")[0]

            arcpy.CopyFeatures_management(features, os.path.join(baseDir, baseName_noext + "_" + str(i)))
            # todo 添加要素属性

    def generateLine_SHP(self):
        assert SHP_LIB, "ERROR --- There is no module named arcpy"

        baseDir = os.path.dirname(outputData)
        baseName = os.path.basename(outputData)
        if ".gdb" in baseDir or ".mdb" in baseDir or ".sde" in baseDir:
            if ".shp" in baseName:
                baseName = baseName.split(".shp")[0]

            baseName_noext = baseName
        else:
            if ".shp" not in baseName:
                baseName_noext = baseName
                baseName = baseName + ".shp"
            else:
                baseName_noext = baseName.split(".shp")[0]

        # 创建要写入的文件，只保留无后缀的数据名
        with shapefile.Writer(baseName_noext, shapeType=3) as shp_writer:
            # 初始化字段
            shp_writer.field('leg_index', "N", 3)
            shp_writer.field('distance', "N", 50)
            shp_writer.field('duration', "N", 50)
            shp_writer.field('direction', "N", 2)
            shp_writer.field('turn', "N", 2)
            shp_writer.field('road_type', "N", 2)
            shp_writer.field('instruction', "C", 255)
            shp_writer.null()



        features = []
        print("*" * 30)
        print(self.ply_fc_total)
        for i, eachFC in enumerate(self.ply_fc_total):
            for plyFC in eachFC:
                print("=" * 30)
                print(plyFC)
                features.append(arcpy.Polyline(arcpy.Array(
                    [arcpy.Point(*coord) for coord in plyFC]
                )))

            arcpy.CopyFeatures_management(features, os.path.join(baseDir, baseName_noext + "_" + str(i)))



    @staticmethod
    def out_of_china(lng, lat):
        """
        判断是否在国内，不在国内不做偏移
        :param lng:
        :param lat:
        :return:
        """
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

    def gcj02_to_bd09(self, lng, lat):
        global x_pi
        """
        火星坐标系(GCJ-02)转百度坐标系(BD-09)
        谷歌、高德——>百度
        :param lng:火星坐标经度
        :param lat:火星坐标纬度
        :return:
        """
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return [bd_lng, bd_lat]

    @staticmethod
    def bd09_to_gcj02(bd_lon, bd_lat):
        """
        百度坐标系(BD-09)转火星坐标系(GCJ-02)
        百度——>谷歌、高德
        :param bd_lat:百度坐标纬度
        :param bd_lon:百度坐标经度
        :return:转换后的坐标列表形式
        """
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]

    @staticmethod
    def _transformlng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * BaiDuRouteLite.pi) + 20.0 *
                math.sin(2.0 * lng * BaiDuRouteLite.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * BaiDuRouteLite.pi) + 40.0 *
                math.sin(lng / 3.0 * BaiDuRouteLite.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * BaiDuRouteLite.pi) + 300.0 *
                math.sin(lng / 30.0 * BaiDuRouteLite.pi)) * 2.0 / 3.0
        return ret

    @staticmethod
    def wgs84_to_gcj02(lng, lat):
        """
        WGS84转GCJ02(火星坐标系)
        :param lng:WGS84坐标系的经度
        :param lat:WGS84坐标系的纬度
        :return:
        """
        if BaiDuRouteLite.out_of_china(lng, lat):  # 判断是否在国内
            return [lng, lat]
        dlat = BaiDuRouteLite._transformlat(lng - 105.0, lat - 35.0)
        dlng = BaiDuRouteLite._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * BaiDuRouteLite.pi
        magic = math.sin(radlat)
        magic = 1 - BaiDuRouteLite.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((BaiDuRouteLite.a * (1 - BaiDuRouteLite.ee)) / (magic * sqrtmagic) * BaiDuRouteLite.pi)
        dlng = (dlng * 180.0) / (BaiDuRouteLite.a / sqrtmagic * math.cos(radlat) * BaiDuRouteLite.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [mglng, mglat]

    @staticmethod
    def gcj02_to_wgs84(lng, lat):
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系的经度
        :param lat:火星坐标系纬度
        :return:
        """
        if BaiDuRouteLite.out_of_china(lng, lat):
            return [lng, lat]
        dlat = BaiDuRouteLite._transformlat(lng - 105.0, lat - 35.0)
        dlng = BaiDuRouteLite._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * BaiDuRouteLite.pi
        magic = math.sin(radlat)
        magic = 1 - BaiDuRouteLite.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((BaiDuRouteLite.a * (1 - BaiDuRouteLite.ee)) / (magic * sqrtmagic) * BaiDuRouteLite.pi)
        dlng = (dlng * 180.0) / (BaiDuRouteLite.a / sqrtmagic * math.cos(radlat) * BaiDuRouteLite.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]

    @staticmethod
    def bd09_to_wgs84(bd_lon, bd_lat):
        lon, lat = BaiDuRouteLite.bd09_to_gcj02(bd_lon, bd_lat)
        return BaiDuRouteLite.gcj02_to_wgs84(lon, lat)

    @staticmethod
    def wgs84_to_bd09(lon, lat):
        lon, lat = BaiDuRouteLite.wgs84_to_gcj02(lon, lat)
        return BaiDuRouteLite.gcj02_to_bd09(lon, lat)

    @staticmethod
    def _transformlat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * BaiDuRouteLite.pi) + 20.0 *
                math.sin(2.0 * lng * BaiDuRouteLite.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * BaiDuRouteLite.pi) + 40.0 *
                math.sin(lat / 3.0 * BaiDuRouteLite.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * BaiDuRouteLite.pi) + 320 *
                math.sin(lat * BaiDuRouteLite.pi / 30.0)) * 2.0 / 3.0
        return ret


originCoord = (121.443996, 31.189405)
destCoord = (121.556707, 31.199413)
coord_type = "wgs84"
outputData = r"E:\百度地图API\测试\路径规划lite结果数据\test.shp"
# with open(r'D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\百度地图api\测试示例\轻量级路径规划\响应示例1.txt') as res:
#     pprint(res.read())


# 发送请求测试
routeObj = BaiDuRouteLite()
routeObj.getDrivingRoute_ip(originCoord, destCoord, coord_type).parseRouteRes().generateRouteFeatureClass(outputData)
