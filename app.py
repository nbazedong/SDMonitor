from flask import Flask, jsonify, render_template
import requests
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

# Thread pool for concurrent requests
executor = ThreadPoolExecutor(max_workers=5)

# Cached URLs
URLS = {
    '101': 'http://192.168.14.101:17860',
    '102': 'http://192.168.14.102:17860',
    '115': 'http://192.168.14.115:17860',
    '105': 'http://192.168.14.105:17860',
    '241-4090': 'http://192.168.14.241:17860',
    # '27-4090': 'http://10.6.27.27:17860',
    '广告设计': 'http://192.168.14.7:17860',
    '角色原画': 'http://10.6.29.52:17860',
    '场景原画': 'http://10.6.29.59.7:17860'
}

# Cache to store server status
PROGRESS_CACHE = {}
SYSTEM_INFO_CACHE = {}
PROGRESS_CACHE_TIMEOUT = 2  # 进度信息缓存2秒
SYSTEM_INFO_CACHE_TIMEOUT = 3600  # 系统信息缓存1小时


def fetch_progress(url):
    """只获取进度信息"""
    try:
        response = requests.get(f'{url}/sdapi/v1/progress?skip_current_image=true', timeout=2)
        if not response.ok:
            return None
        return response.json().get("progress", 0)
    except requests.RequestException:
        return None

def fetch_system_info(url):
    """只获取系统信息"""
    try:
        response = requests.get(f'{url}/sdapi/v1/system-info', timeout=2)
        if not response.ok:
            return None
        return response.json()
    except requests.RequestException:
        return None

def get_cached_system_info(sign, url):
    """获取系统信息（优先使用缓存）"""
    now = time.time()
    if sign in SYSTEM_INFO_CACHE:
        cache_data = SYSTEM_INFO_CACHE[sign]
        if now - cache_data['timestamp'] < SYSTEM_INFO_CACHE_TIMEOUT:
            return cache_data['data']
    
    try:
        system_info = fetch_system_info(url)
        if system_info:
            SYSTEM_INFO_CACHE[sign] = {
                'data': system_info,
                'timestamp': now
            }
            return system_info
        elif sign in SYSTEM_INFO_CACHE:
            # 如果获取失败但有缓存，继续使用缓存
            return SYSTEM_INFO_CACHE[sign]['data']
    except Exception as e:
        print(f"Error fetching system info for {sign}: {e}")
        if sign in SYSTEM_INFO_CACHE:
            return SYSTEM_INFO_CACHE[sign]['data']
    return None

def server_check(signs):
    """获取所有服务器状态"""
    now = time.time()

    def fetch_status(sign):
        url = URLS[sign]
        
        # 检查进度信息缓存
        if sign in PROGRESS_CACHE and now - PROGRESS_CACHE[sign]['timestamp'] < PROGRESS_CACHE_TIMEOUT:
            progress_data = PROGRESS_CACHE[sign]
            progress = progress_data['progress']
            status = progress_data['status']
        else:
            progress = fetch_progress(url)
            if progress is None:
                status = "离线"
                progress = 0
            else:
                status = "运算中" if progress > 0 else "空闲"
            
            PROGRESS_CACHE[sign] = {
                'progress': progress,
                'status': status,
                'timestamp': now
            }
        
        # 获取系统信息（使用长期缓存）
        system_info = None
        if status != "离线":
            system_info = get_cached_system_info(sign, url)
        
        return sign, {
            "status": status,
            "progress": progress,
            "system_info": system_info
        }

    try:
        results = {}
        for sign, result in executor.map(fetch_status, signs):
            results[sign] = result
        return results
    except Exception as e:
        print(f"Error in server_check: {e}")
        return {}


@app.route('/server_status', methods=['GET'])
def server_status():
    signs = URLS.keys()
    data = server_check(signs)
    return jsonify(data)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
