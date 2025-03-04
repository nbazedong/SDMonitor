from flask import Flask, jsonify, render_template
import requests
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import time
import os
import json
from pathlib import Path

app = Flask(__name__)

# Thread pool for concurrent requests
executor = ThreadPoolExecutor(max_workers=5)

def load_server_config():
    """从配置文件加载服务器配置"""
    try:
        config_path = os.getenv('CONFIG_PATH', 'config/servers.json')
        print(f"Loading config from: {config_path}")
        if not os.path.isfile(config_path):
            print(f"Config file not found at {config_path}")
            return {}, {}
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"Loaded config: {json.dumps(config, ensure_ascii=False, indent=2)}")
            
        urls = {}
        for key, server in config.items():
            print(f"Processing server: {key} -> {server['name']}: {server['url']}")
            urls[server['name']] = server['url']
            
        print(f"Final URL mapping: {json.dumps(urls, ensure_ascii=False, indent=2)}")
        return urls, config
    except Exception as e:
        print(f"Error loading server config: {e}")
        return {}, {}

# 从配置文件加载服务器配置
URLS, SERVERS_CONFIG = load_server_config()

# Cache to store server status
PROGRESS_CACHE = {}
SYSTEM_INFO_CACHE = {}
PROGRESS_CACHE_TIMEOUT = 2  # 进度信息缓存2秒
SYSTEM_INFO_CACHE_TIMEOUT = 5  # 系统信息缓存5秒


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
        # 从新的系统信息接口获取数据
        base_url = url.replace('17860', '5001')
        response = requests.get(f'{base_url}/api/system-info', timeout=2)
        if not response.ok:
            return None
        data = response.json()
        
        # 处理返回的数据
        system_info = {
            'gpu_model': 'CPU Only',  # 默认值
            'gpu_memory': 0,  # 默认值
            'gpu_usage': 0,  # 默认值
            'memory_total': data['memory']['total_memory'],
            'memory_usage': data['memory']['memory_usage'],
            'cpu_cores': data['cpu']['cpu_cores'],
            'cpu_usage': data['cpu']['cpu_usage']
        }

        # 如果有GPU信息则更新
        if data.get('gpu') and len(data['gpu']) > 0:
            gpu_data = data['gpu'][0]  # 获取第一个GPU的信息
            system_info.update({
                'gpu_model': gpu_data['gpu_model'],
                'gpu_memory': gpu_data['gpu_memory_total'],
                'gpu_usage': gpu_data['gpu_memory_usage']
            })

        return system_info
    except requests.RequestException as e:
        print(f"Request error for {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error processing data for {url}: {str(e)}")
        return None

def get_cached_system_info(sign, url):
    """获取系统信息（优先使用缓存）"""
    # 对于特定机器不获取系统信息
    if sign in ['场景原画', '广告设计', '角色原画']:
        return None
        
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

@app.route('/server_config')
def server_config():
    """提供服务器配置信息的API端点"""
    return jsonify(SERVERS_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
