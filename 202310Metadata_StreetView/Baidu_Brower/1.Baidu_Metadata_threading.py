import random
import os
import time, glob
import threading
import queue
from Support_Function.baidu.wgs84_to_bd09 import wgs84_to_bd09mc
from Support_Function.baidu.get_svid import GetSVid_FromLonLat
from Support_Function.baidu.get_SVIDdata import Get_SVIDdata
import sqlite3
import geopandas as gpd
from shapely.geometry import Point

def process_gdf(_shapefile_path):
    # 判断面的坐标系 如果不是则转换
    gdf = gpd.read_file(_shapefile_path)        # 载入shapefile
    print('[-] shp坐标系为:', gdf.crs)                # 打印CRS
    if gdf.crs != 'epsg:4326':                  # 转换坐标系
        gdf = gdf.to_crs('epsg:4326')
        gdf.to_file(_shapefile_path, driver='ESRI Shapefile')
        print('已重设坐标系为:', gdf.crs)
    return gdf

def point_within_shapefile(lng, lat, gdf):
    # 判断点是否在行政区内
    point = Point(lng, lat)
    return gdf.geometry.contains(point).any()

def lnglat_2_svid(_lng,_lat):
    # 根据lng,lat采集SVID
    bd09mc_x, bd09mc_y = wgs84_to_bd09mc(_lng, _lat)   # wgs84地理坐标系 转换 bd09投影坐标
    _svid = GetSVid_FromLonLat(bd09mc_x, bd09mc_y)               # 获取svid
    if _svid == None:                                  # 如果该坐标无效终止程序, 并提示更改坐标
        print('[!] 起始坐标无效, 采集终止, 请重新拾取坐标！')
        raise SystemExit
    print('[-] 起始坐标有效, 继续运行！')
    return _svid

def create_database(_database_root):
    # 创建数据库
    conn = sqlite3.connect(_database_root)      # 连接到数据库
    cursor = conn.cursor()
    # 创建第一个表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS record (
        svid TEXT PRIMARY KEY,
        lon REAL,
        lat REAL,
        date INTEGER,
        count_timeline INTEGER,
        north_angle REAL)''')
    # 创建第二个表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temp (
        svid TEXT PRIMARY KEY)''')
    conn.commit()                        # 提交更改
    conn.close()                         # 关闭连接

class DatabaseConnection:
    # 定义一个上下文管理器类：
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

def get_db_count(_database_root):
    # 获取temp表中的行数
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM record")
        record_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM temp")
        temp_count = cursor.fetchone()[0]
    return record_count,temp_count

def filter_existing_svids(_database_root, _SVIDs):
    """参数:_database_root: 数据库路径  SVIDs: 一个包含svid的列表
       返回:一个新的列表，其中不包含已经存在于record表中的svid"""
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT svid FROM record")                             # 查询record表中所有的svid
        existing_svids = set([row[0] for row in cursor.fetchall()])
        filtered_SVIDs = [svid for svid in _SVIDs if svid not in existing_svids] # 过滤掉已经存在的svid
    return filtered_SVIDs

def save_data(_database_root, _SVID_data, _SVIDs):
    # 保存数据
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        # 检查点是否在行政区范围内
        if not point_within_shapefile(_SVID_data[1], _SVID_data[2], gdf):
            print('[!] 点不在行政区范围内, 跳过')
            return
        # SVID_data保存到record表中
        # 示例: data_record = ['09024300121902241252289488D', 117.12243185791468, 39.140244119131076, 20190224, 2, 271.438]
        cursor.execute("INSERT OR IGNORE INTO record (svid, lon, lat, date, count_timeline, north_angle) VALUES (?, ?, ?, ?, ?, ?)", _SVID_data)
        # SVIDs保存到temp表中
        # 示例: data_temp = ['09024300121902261213180748D', '09024300121902251320186278D', '09024300121902241252312658D']
        for svid in _SVIDs:
            cursor.execute("INSERT OR IGNORE INTO temp (svid) VALUES (?)", [svid])
        conn.commit()

def fetch_and_delete_svid_from_temp(_database_root):
    """从temp表中获取一个svid，并随后删除它。确保这个svid不在record表中"""
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        while True:
            cursor.execute("SELECT svid FROM temp LIMIT 1")  # 从temp表中获取一个svid
            svid = cursor.fetchone()
            if not svid:                                     # 如果temp表为空，直接结束程序
                print('[!] temp表中为空, 全部采集完毕！')
                raise SystemExit
            svid_value = svid[0]
            cursor.execute("DELETE FROM temp WHERE svid = ?", (svid_value,))    # 无论svid是否在record表中，都从temp表中删除它
            conn.commit()

            # 检查svid是否已经存在于record表中
            cursor.execute("SELECT svid FROM record WHERE svid = ?", (svid_value,))
            if not cursor.fetchone():  # 如果svid不在record表中，跳出循环
                break
    return svid_value

def svid_2_collect(_svid):
    # 根据svid采集相邻街景并保存
    SVID_data, SVIDs = Get_SVIDdata(_svid)                        # 根据SVID采集相邻SVID
    if SVID_data is not None and SVIDs is not None:               # 确认没有None再处理
        filler_SVIDs = filter_existing_svids(database_root,SVIDs) # 将SVIDs中record已经有的删除
        save_data(database_root,SVID_data, filler_SVIDs)          # 将SVID_data保存到record 将SVIDs保存到temp

class PanoidCollector(threading.Thread):
    def __init__(self, database_root, gdf, thread_id):
        threading.Thread.__init__(self)
        self.database_root = database_root
        self.gdf = gdf
        self.thread_id = thread_id

    def run(self):
        while get_db_count(self.database_root)[1] > 0:
            try:
                panoid = fetch_and_delete_svid_from_temp(self.database_root)
                svid_2_collect(panoid)
                print(f"[线程 {self.thread_id}] 已采集 {get_db_count(self.database_root)[0]} 个街景点,待采集 {get_db_count(self.database_root)[1]} 个街景点, {time.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(random.randint(0, 6))  # 根据需要启用
            except Exception as e:
                print(f"[线程 {self.thread_id}] 错误: {e}")

if __name__ == "__main__":
    # 坐标拾取：https://tool.lu/coordinate
    lng, lat = 114.15739539598744,22.283968941984877              # 输入城市中心点位置wgs84地理坐标系的坐标
    shapefile_path = "./restriction_area/hongkong_distrct.shp"    # 读取行政区范围限制shp数据(先判断坐标系是否是4326)
    database_root = './baidu_hongkong.db'                               # 设置数据库的路径

    gdf = process_gdf(shapefile_path)                             # 判断坐标系
    create_database(database_root)                                # 创建数据库
    svid = lnglat_2_svid(lng,lat)                                 # 根据lng,lat采集SVID
    svid_2_collect(svid)                                          # 根据svid采集相邻街景并保存

    record_count,temp_count = get_db_count(database_root)         # 获得已经采集的数量
    print(f'[-] 目前record采集{record_count}, temp采集{temp_count}')

    # 启动多个线程
    thread_count = 10  # 可以根据需要调整线程数量
    threads = []
    for i in range(thread_count):
        thread = PanoidCollector(database_root, gdf, i)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    print('[-] 本次街景图片采集结束 谢谢使用\n\n                   __Development by Phd.WangLei')