import requests
import json
from fake_useragent import UserAgent
import time,random

# 通过panoid获取json格式数据
def GetJson_FromPanoid(panoId):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    url = "https://www.google.com/maps/photometa/v1?authuser=0&hl=en&pb=!1m4!1smaps_sv.tactile!11m2!2m1!1b1!2m2!1szh-CN!2sus!3m3!1m2!1e2!2s{}!4m57!1e1!1e2!1e3!1e4!1e5!1e6!1e8!1e12!2m1!1e1!4m1!1i48!5m1!1e1!5m1!1e2!6m1!1e1!6m1!1e2!9m36!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e1!2b0!3e3!1m3!1e4!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e3"
    url = url.format(panoId)

    attempts = 0
    while attempts < 5:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            line = resp.text.replace(")]}'\n", "")
            if len(line) > 10000:
                jdata = json.loads(line)
                return jdata
            else:
                jdata = 1551
                return jdata

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"[!] 请求失败，正在重试... ({attempts+1}/{5})")
            attempts += 1
            time.sleep(1)  # 等待1秒再重试
    print("[!] 请求失败次数过多，停止尝试。")
    return None




def Get_Links_data(jdata):
    all_panoid = jdata[1][0][5][0][3][0]                # 准备所有panoid (包含相邻道路panoid+历史街景panoid)

    try:                                                # 准备历史街景所在位置 从pano_list中排除这些
        his_panoid = jdata[1][0][5][0][8]               # 有历史街景的情况

        his_panoid_new_year, his_panoid_new_month = int(his_panoid[0][1][0]),int(his_panoid[0][1][1]) # 历史街景中最新的年/月

        min, max = his_panoid[0][0], his_panoid[-1][0]  # dates[0]是最新的街景年份(数字是小), dates[-1]是最老的街景年份(数字是大)
        del_all_panoid = all_panoid.copy()              # 复制原始列表
        del del_all_panoid[min:max + 1]                 # 将历史街景的panoid删除
        panoid_list = del_all_panoid
    except:                                             # 解决无历史街景的情况
        panoid_list = all_panoid
        his_panoid_new_year, his_panoid_new_month = 0,0

    links_panoid_list = []                              # 设置储存数据的空列表
    for info in panoid_list:
        panoid = info[0][1]
        links_panoid_list.append(panoid)
    return links_panoid_list, his_panoid_new_year, his_panoid_new_month

# 获取panoid的元数据
def Get_PANOIDdata(_panoId):
    jdata = GetJson_FromPanoid(_panoId)
    if len(str(jdata)) < 1000:
        return None, None
    lon_true_wgs84 = jdata[1][0][5][0][1][0][3]                                 # 真实经度
    lat_true_wgs84 = jdata[1][0][5][0][1][0][2]                                 # 真实纬度
    Data_year, Data_month = int(jdata[1][0][6][7][0]), int(jdata[1][0][6][7][1]) # 拍摄年/月


    Date = int('{}{}'.format(Data_year, Data_month))                            # 拍摄日期
    north_angle =  float(jdata[1][0][5][0][1][2][0])                            # 与北的夹角
    try:
        count_timeline = len(jdata[1][0][5][0][8])                              # 尝试访问历史街景数量
    except:
        count_timeline = 0                                                      # 如果没有历史街景则返回0

    # 组合数据
    PANOID_data = [_panoId,lon_true_wgs84, lat_true_wgs84, Date, count_timeline, north_angle]
    PANOIDs, his_panoid_new_year, his_panoid_new_month = Get_Links_data(jdata)

    # 判断这个panoid是不是最新的街景信息
    # print('拍摄日期', Data_year, Data_month)
    # print('历史拍摄最新', his_panoid_new_year, his_panoid_new_month)
    if Data_year >= his_panoid_new_year and Data_month >= his_panoid_new_month:
        return PANOID_data, PANOIDs
    else:
        return None,None


# lon = 114.15739539598744
# lat = 22.283968941984877
# panoid = 'X1eWlT2R72Oq1U2OcOE49A'

# 获取每个panoid的各项元数据
# PANOID_data, PANOIDs = Get_PANOIDdata(panoid)
# print(PANOID_data, PANOIDs)




