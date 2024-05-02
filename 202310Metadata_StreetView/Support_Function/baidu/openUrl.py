# 该模块功能, 输入url, 返回内容
import requests
from fake_useragent import UserAgent
import time

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


def openUrl_json(_url):
    headers = {"User-Agent": ua.random}

    attempts = 0
    while attempts < 5:
        try:
            response = requests.get(_url, headers=headers, timeout=15)
            if response.status_code == 200:  # 如果状态码为200，寿命服务器已成功处理了请求，则继续处理数据
                return response.json()
            else:
                return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"[!] 请求失败，正在重试... ({attempts+1}/{5})")
            attempts += 1
            time.sleep(1)  # 等待1秒再重试
    print("[!] 请求失败次数过多，停止尝试。")
    return None