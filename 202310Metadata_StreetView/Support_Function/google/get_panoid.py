import requests
import json
from fake_useragent import UserAgent

# 初始化 UserAgent 对象
ua = UserAgent()

# 通过经纬度获取panoid
def GetPanoid_FromLonLat(lon, lat):
    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2&callback=_xdc_._v2mub5"
    url = url.format(lat, lon)

    headers = {"User-Agent": ua.random}  # 使用随机生成的用户代理

    resp = requests.get(url, headers=headers, proxies=None)
    line = resp.text.replace("/**/_xdc_._v2mub5 && _xdc_._v2mub5( ", "")[:-2]

    if len(line) > 3000:
        jdata = json.loads(line)
        panoid = jdata[1][1][1]
        # north_angle = jdata[1][5][0][1][2][0]
        # pano_lon = jdata[1][5][0][1][0][3]
        # pano_lat = jdata[1][5][0][1][0][2]
        return panoid
    else:
        return None


lon = 114.15739539598744
lat = 22.283968941984877
panoid = 'yhj1EJ8czrzONstJ_gBIwQ'

# panoid = GetPanoid_FromLonLat(lon,lat)
# print(panoid)