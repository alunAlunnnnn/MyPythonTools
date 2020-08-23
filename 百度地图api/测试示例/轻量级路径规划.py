import requests
import urllib
from pprint import pprint
import math
import arcpy


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
* gps_direction    int64    用于提高计算的精度。起点的定位方向，车头方向与正北方向的夹角，当speed>1.5 m/s 且 gps_direction存在时，该参数生效
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
class BaiDuRouteLite:
    def __init__(self):
        self.response = None

    # 常量定义
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626  # π
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 偏心率平方

    # 发送请求，获取驾车路径规划
    def getDrivingRoute_ip(self, originCoord, destCoord, coord_type, tactics, waypoints=None):
        '''
        :param originCoord: tuple or list, format --- (longitude, latitude)
        :param destCoord: tuple or list, format --- (longitude, latitude)
        :return: response object
        '''

        baseurl = 'http://api.map.baidu.com/directionlite/v1/driving'

        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'

        if not waypoints:
            para = {
                'ak': 'KRx4yS11gIPRDIiNgHIrcirf4ZsMKGhw',
                'origin': '%s,%s' % (originCoord[1], originCoord[0]),
                'destination': '%s,%s' % (destCoord[1], destCoord[0]),
                'output': 'json',
                'coord_type': coord_type,
                'tactics': tactics
            }
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

        self.response = requests.get(baseurl, headers={'User-Agent': ua}, params=para)
        self.coord_type = coord_type
        return self

    # 解析响应
    def parseRouteRes(self):
        data = self.response.text
        self.route_distance = data['result']['routes']['distance']
        self.route_duration = data['result']['routes']['duration']
        self.traffic_condition = data['result']['routes']['traffic_condition']
        self.toll = data['result']['routes']['toll']
        self.steps = data['result']['routes']['steps']
        return self

    # 生成路线要素类
    def generateRouteFeatureClass(self, outputData):
        if self.coord_type == 'wgs84':
            arcpy.CreateFeatureclass_management()
        for eachStep in self.steps:
            attr_distance = eachStep['distance']
            attr_duration = eachStep['duration']
            attr_direction = eachStep['direction']
            attr_turn = eachStep['turn']
            attr_road_type = eachStep['road_type']

            # 获取导航描述，并清除加粗标记
            attr_instruction = eachStep['instruction'].replace('<b>').replace('<\/b>')


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
        dlat = (dlat * 180.0) / ((BaiDuRouteLite.a * (1 - BaiDuRouteLite.ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (BaiDuRouteLite.a / sqrtmagic * math.cos(radlat) * pi)
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
        dlat = (dlat * 180.0) / ((BaiDuRouteLite.a * (1 - BaiDuRouteLite.ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (BaiDuRouteLite.a / sqrtmagic * math.cos(radlat) * pi)
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


originCoord = (121.443996, 31.189405)
destCoord = (121.556707, 31.199413)
with open(r'D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\百度地图api\测试示例\轻量级路径规划\响应示例1.txt') as res:
    pprint(res.read())


