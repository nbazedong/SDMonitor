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
CACHE = {}
CACHE_TIMEOUT = 10  # Cache expiry in seconds


def fetch_progress(url):
    """Fetch progress from a single server."""
    try:
        response = requests.get(f'{url}/sdapi/v1/progress?skip_current_image=true', timeout=2)
        response.raise_for_status()
        # print(response.json().get("progress", 0))
        return response.json().get("progress", 0)
    except requests.RequestException:
        return None


def server_check(signs):
    """Fetch status for all servers."""
    global CACHE
    now = time.time()

    # Fetch status using ThreadPoolExecutor
    def fetch_status(sign):
        url = URLS[sign]
        if sign in CACHE and now - CACHE[sign]['timestamp'] < CACHE_TIMEOUT:
            return CACHE[sign]['status']  # Use cached result
        progress = fetch_progress(url)
        if progress is None:
            status = f"{sign} | 离线"
        elif progress > 0:
            status = f"{sign} | 运算中"
        else:
            status = f"{sign} | 空闲"
        # Cache the result
        CACHE[sign] = {"status": status, "progress": progress, "timestamp": now}
        return status

    results = {}
    for sign, result in zip(signs, executor.map(fetch_status, signs)):
        results[result] = CACHE[sign]['progress']
    return results


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
