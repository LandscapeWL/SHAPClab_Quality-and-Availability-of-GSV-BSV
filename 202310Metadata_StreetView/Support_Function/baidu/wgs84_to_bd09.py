# 该模块功能, 将wgs84坐标 转换为bd09坐标
import json
import requests
from fake_useragent import UserAgent
import math

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

class LLT:
    def __init__(self,x,y):
        self.x=x
        self.y=y
def convertor(cC, cD):
    if (cC==None or cD==None):
        print('null')
        return None
    T = cD[0] + cD[1] * abs(cC.x)
    cB = abs(cC.y) / cD[9]
    cE = cD[2] + cD[3] * cB + cD[4] * cB * cB +cD[5] * cB * cB * cB + cD[6] * cB * cB * cB * cB +cD[7] * cB * cB * cB * cB * cB +cD[8] * cB * cB * cB * cB * cB * cB
    if(cC.x<0):
        T=T*-1
    else:
        T=T
    if(cC.y<0):
        cE=cE*-1
    else:
        cE=cE
    return [T, cE]

#百度墨卡托投影纠正矩阵
LLBAND =[75, 60, 45, 30, 15, 0]
LL2MC = [[-0.0015702102444, 111320.7020616939, 1704480524535203, -10338987376042340, 26112667856603880, -35149669176653700, 26595700718403920, -10725012454188240, 1800819912950474, 82.5],
         [0.0008277824516172526, 111320.7020463578, 647795574.6671607, -4082003173.641316, 10774905663.51142, -15171875531.51559, 12053065338.62167, -5124939663.577472, 913311935.9512032, 67.5],
         [0.00337398766765, 111320.7020202162, 4481351.045890365, -23393751.19931662, 79682215.47186455, -115964993.2797253, 97236711.15602145, -43661946.33752821, 8477230.501135234, 52.5],
         [0.00220636496208, 111320.7020209128, 51751.86112841131, 3796837.749470245, 992013.7397791013, -1221952.21711287, 1340652.697009075, -620943.6990984312, 144416.9293806241, 37.5],
         [-0.0003441963504368392, 111320.7020576856, 278.2353980772752, 2485758.690035394, 6070.750963243378, 54821.18345352118, 9540.606633304236, -2710.55326746645, 1405.483844121726, 22.5],
         [-0.0003218135878613132, 111320.7020701615, 0.00369383431289, 823725.6402795718, 0.46104986909093, 2351.343141331292, 1.58060784298199, 8.77738589078284, 0.37238884252424, 7.45]]
# 百度墨卡托转回到百度经纬度纠正矩阵
MCBAND = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
MC2LL = [[1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331, 200.9824383106796, -187.2403703815547, 91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
      [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289, 96.32687599759846, -1.85204757529826, -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
      [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616, 59.74293618442277, 7.357984074871, -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
      [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591, 40.31678527705744, 0.65659298677277, -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
      [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062, 23.10934304144901, -0.00023663490511, -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
      [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8, 7.47137025468032, -0.00000353937994, -0.02145144861037, -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5]]

def getRange(cC, cB, T):
    if (cB != None):
        cC = max(cC, cB)
    if (T != None):
        cC = min(cC, T)
    return cC

def getLoop(cC, cB, T):
    while (cC > T):
        cC -= T - cB
    while (cC < cB):
        cC += T - cB
    return cC

def convertLL2MC(T) :
    cD=None
    T.x = getLoop(T.x, -180, 180)
    T.y = getRange(T.y, -74, 74)
    cB = T
    for cC in range(0,len(LLBAND),1):
        if (cB.y >= LLBAND[cC]) :
            cD = LL2MC[cC]
            break
    if (cD!=None) :
        for cC in range(len(LLBAND) - 1,-1,-1):
            if (cB.y <= -LLBAND[cC]):
                cD = LL2MC[cC]
                break
    cE = convertor(T, cD)
    return cE

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def convertMC2LL(cB):
    cC=LLT(abs(cB.x),abs(cB.y))
    cE=None
    for cD in range(0,len(MCBAND),1):
        if (cC.y >= MCBAND[cD]) :
            cE = MC2LL[cD]
            break
    T = convertor(cB, cE)
    return T

def mercatortobd09(x,y):
    x, y = float(x), float(y)
    baidut=LLT(x,y)
    return convertMC2LL(baidut)

def out_of_china(lng, lat): # 判断是否在国内，不在国内不做偏移
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def wgs84_to_gcj02(lng, lat): # WGS84转GCJ02(火星坐标系)
    # 判断是否在国内
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]
def gcj02_to_bd09(lng, lat):
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]
def bd09tomercator(lng,lat): # bd09投影到百度墨卡托
    baidut=LLT(lng,lat)
    return convertLL2MC(baidut)

def bd09togcj02(bd_lon, bd_lat):
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]
def gcj02towgs84(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def bd09_to_wgs84(lon, lat):
    lon, lat = float(lon), float(lat)
    lon, lat = bd09togcj02(lon, lat)
    lon, lat = gcj02towgs84(lon, lat)
    return lon, lat

def wgs84_to_bd09mc(lon, lat):
    lon, lat = float(lon), float(lat)
    lon, lat = wgs84_to_gcj02(lon, lat)
    lon, lat = gcj02_to_bd09(lon, lat)
    lon, lat = bd09tomercator(lon, lat)
    return lon, lat





# 设置虚拟浏览器
# ua = UserAgent(use_cache_server=False)
ua = UserAgent()
# 设置请求头 request header
def openUrl(_url):
    headers = {"User-Agent": ua.random}
    response = requests.get(_url, headers=headers)
    if response.status_code == 200:  # 如果状态码为200，寿命服务器已成功处理了请求，则继续处理数据
        return response.content
    else:
        return None
# 百度官方转换API接口 key可以替换为自己的 (wgs84 → bd09)
# 因为百度街景获取时采用的是经过二次加密的百度墨卡托投影bd09mc
# 官方开发文档 https://lbsyun.baidu.com/index.php?title=webapi/guide/changeposition
# api Vd88SC0LpGjiGNQywXsyVxZPOTcyear9 / mYL7zDrHfcb0ziXBqhBOcqFefrbRUnuq
def wgs84_to_bd09mc_api(wgs_x, wgs_y):
    print(type(wgs_x),wgs_y)
    # to:5是转为bd0911，6是转为百度墨卡托
    url = 'http://api.map.baidu.com/geoconv/v1/?coords={}+&from=1&to=6&output=json&ak={}'.format(
        wgs_x + ',' + wgs_y, 'mYL7zDrHfcb0ziXBqhBOcqFefrbRUnuq')
    res = openUrl(url).decode()
    temp = json.loads(res)
    bd09mc_x = 0
    bd09mc_y = 0
    if temp['status'] == 0:
        bd09mc_x = temp['result'][0]['x']
        bd09mc_y = temp['result'][0]['y']
        print(type(bd09mc_x),bd09mc_y)
    return bd09mc_x, bd09mc_y

# bd09mc_x, bd09mc_y = wgs84_to_bd09mc_api(str(116.404763),str(39.914051))
# print(bd09mc_x, bd09mc_y)