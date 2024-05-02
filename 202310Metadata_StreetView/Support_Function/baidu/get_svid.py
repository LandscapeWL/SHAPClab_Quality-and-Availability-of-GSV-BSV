import re
from Support_Function.baidu.openUrl import openUrl

# 获取百度街景中的svid get svid of baidu streetview
def GetSVid_FromLonLat(_lng, _lat):
    url = "https://mapsv0.bdimg.com/?&qt=qsdata&x={}&y={}&l=17.031000000000002&action=0&mode=day&t=1530956939770".format(_lng, _lat)
    response = openUrl(url).decode("utf8")
    # print(response)

    reg = r'"id":"(.+?)",'
    pat = re.compile(reg)
    try:
        svid = re.findall(pat, response)[0]
        return svid
    except:
        return None

# 此处需要bd09投影坐标系！
# result = GetSVid_FromLonLat(116.404763,39.914051)
# result = GetSVid_FromLonLat(12959666.537416186,4826899.2388450205)
# print(result)