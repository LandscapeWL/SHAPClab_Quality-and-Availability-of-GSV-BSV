import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

# 准备球形树查询需要的数据
def prepare_ball_tree(data, radius):
    # 将经纬度转换为弧度，因为BallTree要求数据以弧度为单位
    data_rad = np.deg2rad(data[['lat', 'lon']].values)
    # 创建BallTree对象
    tree = BallTree(data_rad, metric='haversine')
    # 计算半径的弧度
    radius_rad = radius / 6371000  # 地球平均半径为6371km
    return tree, radius_rad

# 找到每个点半径内的最近邻点
def find_nearest_point(tree, data_rad, radius_rad):
    distances = []
    count = 0
    # 对于每个点，找到半径内的所有点
    for point in data_rad:
        # indices为索引，dist为距离（以弧度为单位）
        ind, dist = tree.query_radius([point], r=radius_rad, return_distance=True)
        if len(dist[0]) > 1:  # 如果找到了至少一个邻居（除了点本身）
            # 排序距离，并选择最近的邻居（排除自身）
            closest_dist = np.sort(dist[0])[1]
        else:
            closest_dist = np.nan  # 如果没有找到邻居，返回NaN
        distances.append(closest_dist)
        count += 1
        print('正在查询数量:',count)
    # 将距离转换为米
    distances = np.array(distances) * 6371000  # 将弧度转换为米
    return distances

# 读取数据
data = pd.read_csv('metadata.csv')

# 准备球形树
tree, radius_rad = prepare_ball_tree(data, radius=100)

# 对每个点找到半径内的最近邻点
data['distance'] = find_nearest_point(tree, np.deg2rad(data[['lat', 'lon']].values), radius_rad)

# 保存结果到CSV
data.to_csv('metadata_with_distances.csv', index=False)

