import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import os

interval_list = ['200','100','50','40','30','20','10','5']

for interval in interval_list:
    # 读取CSV文件
    points = pd.read_csv('./1.different_interval_csv/points_{}m.csv'.format(interval))   # 不同间隔点坐标
    baidu = pd.read_csv('./1.metedata_csv/baidu_hongkong.csv')                           # metedata数据
    save_path = './2.result_csv/search_baidu_{}m.csv'.format(interval)                   # 结果储存路径
    search_radius = 50  # 搜索半径
    save_interval = 100  # 每处理100个点后保存一次

    # 准备球形树查询需要的数据
    def prepare_ball_tree(data, radius):
        # 将经纬度转换为弧度
        data_rad = np.deg2rad(data[['truly_lat', 'truly_lng']].values)  # 修改列名
        # 创建BallTree对象
        tree = BallTree(data_rad, metric='haversine')
        # 计算半径的弧度
        radius_rad = radius / 6371000  # 地球平均半径为6371km
        return tree, radius_rad

    # 找到每个点半径内的最近邻点
    def find_nearest_point(tree, point, radius_rad):
        ind, dist = tree.query_radius([point], r=radius_rad, return_distance=True)
        if len(dist[0]) > 0:
            closest_idx = ind[0][np.argmin(dist[0])]
            return closest_idx
        else:
            return None

    # 准备球形树
    tree, radius_rad = prepare_ball_tree(baidu[['truly_lat', 'truly_lng']], search_radius)  # 修改列名

    # 对points中每个点寻找最近的点
    results_df = pd.DataFrame()  # 创建一个空的DataFrame

    # 指定新的表头
    columns = ['FID', 'lng', 'lat', 'svid', 'truly_lng', 'truly_lat', 'date', 'count_timeline', 'north_angle']

    for index, row in points.iterrows():
        nearest_idx = find_nearest_point(tree, np.deg2rad([row['lat'], row['lng']]), radius_rad)
        if nearest_idx is not None:
            nearest_row = baidu.iloc[nearest_idx]
            result = pd.concat([row, nearest_row])
        else:
            result = pd.concat([row, pd.Series([None] * len(baidu.columns), index=baidu.columns)])

        # 创建一个包含新列名的DataFrame
        result_df = pd.DataFrame([result], columns=columns)
        results_df = pd.concat([results_df, result_df], ignore_index=True)

        # 每处理save_interval个点后保存一次
        if (index + 1) % save_interval == 0 or (index + 1) == len(points):
            print('处理{}m间隔轮次:'.format(interval), index + 1)
            # 检查文件是否已经存在
            file_exists = os.path.isfile(save_path)
            # 仅当文件不存在时，才包含表头
            results_df.to_csv(save_path, mode='a', header=not file_exists, index=False)
            results_df = pd.DataFrame()  # 清空DataFrame以保存下一批结果

