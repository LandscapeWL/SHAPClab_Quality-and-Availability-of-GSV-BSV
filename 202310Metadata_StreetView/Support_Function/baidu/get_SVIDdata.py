import time
import random
from Support_Function.baidu.openUrl import openUrl_json
from Support_Function.baidu.wgs84_to_bd09 import bd09_to_wgs84
from Support_Function.baidu.wgs84_to_bd09 import mercatortobd09

# 获取百度街景中相邻的svid, 路中间的是road下字段, 路口是link
def Get_SVIDdata(_svid):
    url = "https://mapsv0.bdimg.com/?qt=sdata&sid=%s" % (str(_svid))
    response = openUrl_json(url)
    content = response.get('content')

    # 判断坐标是否有效, 无效返回None
    if content == None or len(content[0]) < 5:
        return None, None

    else:
        # 获取返回的具体内容
        content = content[0]

        # 每次访问只能取得svid对应的1个角度, 每个历史街景需要分别去访问获得精确的角度
        TimeLine = content['TimeLine']

        count_timeline = len(TimeLine)
        his_svid_new_year_month = int(TimeLine[0]['TimeLine'])

        # 获取真实的经纬度坐标
        # 获取投影坐标系的XY, 为XY加上小数点, 将投影坐标系转为bd09地理坐标系, 将bd09转化为wgs84坐标系
        X, Y = str(content['X']),str(content['Y'])
        X, Y = X[:8] + '.' + X[8:], Y[:7] + '.' + Y[7:]
        lon_true_bd09, lat_true_bd09 = mercatortobd09(X, Y)
        lon_true_wgs84, lat_true_wgs84 = bd09_to_wgs84(lon_true_bd09, lat_true_bd09)

        # 获取元数据
        north_angle = content['MoveDir']
        Date = int(content['Date'])                     # 示例：20170306
        shoot_Data = int(content['Date'][:6])           # 示例：201703
        # DeviceHeight = content['DeviceHeight']
        # Heading = content['Heading']
        # Pitch = content['Pitch']
        # Roll = content['Roll']
        # 该参数有时候没有
        # RoadWidth = content['Roads'][-1]['Width']

        # 获取links相邻数据
        Links = content['Links']
        Links_svid = [item['PID'] for item in Links]
        # 获取roads相邻数据
        Roads = content['Roads']
        # print(Roads)

        # 获取svid相邻的
        Roads_svid = []                                 # 存储所有PID的列表
        for item in Roads:                              # 遍历列表中的每个元素
            panos = item.get('Panos', [])               # 获取'Panos'键对应的值，如果存在的话
            if isinstance(panos, list):                 # 如果'Panos'是一个列表，继续遍历获取每个'PID'
                for pano in panos:
                    pid = pano.get('PID')
                    if pid:
                        Roads_svid.append(pid)

        # 组合数据
        SVID_data = [_svid,lon_true_wgs84, lat_true_wgs84, Date, count_timeline, north_angle]
        SVIDs = Links_svid + Roads_svid

        # 判断这个svid是不是最新的街景信息
        # print('拍摄日期', shoot_Data,type(Date))
        # print('历史拍摄最新', his_svid_new_year_month,type(his_svid_new_year_month))
        if shoot_Data >= his_svid_new_year_month:
            return SVID_data, SVIDs
        else:
            return None, None



# 测试
# _svid = '01024300001310241529131215F' # 历史街景
# _svid = '09024300122002171358298765A' # 正常街景

# _svid = 'a'
# metadata, PIDs = Get_SVIDdata(_svid)
# print(metadata, PIDs)



