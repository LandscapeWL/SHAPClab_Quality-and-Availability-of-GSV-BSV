import random
import os
import time, glob
import threading
import queue
from Support_Function.google.get_panoid_metadata_json import Get_PANOIDdata
from Support_Function.google.get_panoid import GetPanoid_FromLonLat
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

def lnglat_2_panoid(_lng,_lat):
    # 根据lng,lat采集panoid
    _panoid = GetPanoid_FromLonLat(_lng,_lat)            # 获取panoid
    if _panoid == None:                                  # 如果该坐标无效终止程序, 并提示更改坐标
        print('[!] 起始坐标无效, 采集终止, 请重新拾取坐标！')
        raise SystemExit
    print('[-] 起始坐标有效, 继续运行！')
    return _panoid

def create_database(_database_root):
    # 创建数据库
    conn = sqlite3.connect(_database_root)      # 连接到数据库
    cursor = conn.cursor()
    # 创建第一个表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS record (
        panoid TEXT PRIMARY KEY,
        lon REAL,
        lat REAL,
        date INTEGER,
        count_timeline INTEGER,
        north_angle REAL)''')
    # 创建第二个表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temp (
        panoid TEXT PRIMARY KEY)''')
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

def filter_existing_panoids(_database_root, _PANOIDs):
    """参数:_database_root: 数据库路径  PANOIDs: 一个包含panoid的列表
       返回:一个新的列表，其中不包含已经存在于record表中的panoid"""
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT panoid FROM record")                             # 查询record表中所有的panoid
        existing_panoids = set([row[0] for row in cursor.fetchall()])
        filtered_PANOIDs = [panoid for panoid in _PANOIDs if panoid not in existing_panoids] # 过滤掉已经存在的panoid
    return filtered_PANOIDs

def save_data(_database_root, _PANOID_data, _PANOIDs):
    # 保存数据
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        # 检查点是否在行政区范围内
        if not point_within_shapefile(_PANOID_data[1], _PANOID_data[2], gdf):
            print('[!] 点不在行政区范围内, 跳过')
            return
        # PANOID_data保存到record表中
        # 示例: data_record = ['09024300121902241252289488D', 117.12243185791468, 39.140244119131076, 20190224, 2, 271.438]
        cursor.execute("INSERT OR IGNORE INTO record (panoid, lon, lat, date, count_timeline, north_angle) VALUES (?, ?, ?, ?, ?, ?)", _PANOID_data)
        # PANOIDs保存到temp表中
        # 示例: data_temp = ['09024300121902261213180748D', '09024300121902251320186278D', '09024300121902241252312658D']
        for panoid in _PANOIDs:
            cursor.execute("INSERT OR IGNORE INTO temp (panoid) VALUES (?)", [panoid])
        conn.commit()

def fetch_and_delete_panoid_from_temp(_database_root):
    """从temp表中获取一个panoid，并随后删除它。确保这个panoid不在record表中"""
    with DatabaseConnection(_database_root) as conn:
        cursor = conn.cursor()
        while True:
            cursor.execute("SELECT panoid FROM temp LIMIT 1")  # 从temp表中获取一个panoid
            panoid = cursor.fetchone()
            if not panoid:                                     # 如果temp表为空，直接结束程序
                print('[!] temp表中为空, 全部采集完毕！')
                raise SystemExit
            panoid_value = panoid[0]
            cursor.execute("DELETE FROM temp WHERE panoid = ?", (panoid_value,))    # 无论panoid是否在record表中，都从temp表中删除它
            conn.commit()

            # 检查panoid是否已经存在于record表中
            cursor.execute("SELECT panoid FROM record WHERE panoid = ?", (panoid_value,))
            if not cursor.fetchone():  # 如果panoid不在record表中，跳出循环
                break
    return panoid_value

def panoid_2_collect(_panoid):
    # 根据panoid采集相邻街景并保存
    PANOID_data, PANOIDs = Get_PANOIDdata(_panoid)                      # 根据PANOID采集相邻PANOID
    if PANOID_data is not None and PANOIDs is not None:                 # 确认没有None再处理/ 如果相邻街景是历史的街景不是最新的，可能会是None
        filler_PANOIDs = filter_existing_panoids(database_root,PANOIDs) # 将PANOIDs中record已经有的删除
        save_data(database_root,PANOID_data, filler_PANOIDs)            # 将PANOID_data保存到record 将PANOIDs保存到temp

class PanoidCollector(threading.Thread):
    def __init__(self, database_root, gdf, thread_id):
        threading.Thread.__init__(self)
        self.database_root = database_root
        self.gdf = gdf
        self.thread_id = thread_id

    def run(self):
        while get_db_count(self.database_root)[1] > 0:
            try:
                panoid = fetch_and_delete_panoid_from_temp(self.database_root)
                panoid_2_collect(panoid)
                print(f"[线程 {self.thread_id}] 已采集 {get_db_count(self.database_root)[0]} 个街景点,待采集 {get_db_count(self.database_root)[1]} 个街景点, {time.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(random.randint(0, 6))  # 根据需要启用
            except Exception as e:
                print(f"[线程 {self.thread_id}] 错误: {e}")

if __name__ == "__main__":
    # 坐标拾取：https://tool.lu/coordinate
    lng, lat = 114.15739539598744,22.283968941984877              # 输入城市中心点位置wgs84地理坐标系的坐标
    shapefile_path = "./restriction_area/hongkong_distrct.shp"    # 读取行政区范围限制shp数据(先判断坐标系是否是4326)
    database_root = './google_hongkong.db'                               # 设置数据库的路径

    gdf = process_gdf(shapefile_path)                             # 判断坐标系
    create_database(database_root)                                # 创建数据库
    panoid = lnglat_2_panoid(lng,lat)                             # 根据lng,lat采集panoid
    panoid_2_collect(panoid)                                      # 根据panoid采集相邻街景并保存
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