# SD-Monitor 监控面板

## 项目介绍
SD-Monitor 是一个用于监控多台 Stable Diffusion WebUI 服务器状态的实时监控面板。主要功能包括：

- 实时监控多台服务器的运行状态
- 显示服务器的 GPU、CPU 和内存使用情况
- 支持一键跳转到对应服务器的 WebUI 界面
- 支持浅色/深色主题切换
- 自适应布局，支持移动端访问

## 安装说明

### 本地开发环境

1. 克隆项目
```bash
git clone [项目地址]
cd SDMonitor
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置服务器
```bash
cp config/servers.template.json config/servers.json
```
根据实际环境修改 `config/servers.json` 中的服务器配置

4. 启动服务
```bash
flask run --host=0.0.0.0 --port=5000
```

### Docker 部署

1. 构建镜像
```bash
docker build -t sdmonitor .
```

2. 运行容器
```bash
# 使用默认配置
docker run -d -p 5000:5000 --name sdmonitor sdmonitor

# 使用自定义配置
docker run -d -p 5000:5000 \
  -v /path/to/your/servers.json:/app/config/servers.json \
  --name sdmonitor sdmonitor
```

### Docker Compose 部署
```yaml
version: '3'
services:
  sdmonitor:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config/servers.json:/app/config/servers.json
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```

## 配置文件说明

配置文件位于 `config/servers.json`，格式如下：

```json
{
    "server_id": {
        "name": "显示名称",
        "url": "http://服务器IP:端口"
    }
}
```

示例：
```json
{
    "gpu-1": {
        "name": "RTX4090服务器",
        "url": "http://192.168.1.100:17860"
    }
}
```

注意事项：
- 确保所有服务器的 WebUI 端口（默认17860）可访问
- 系统信息监控需要额外的监控端口（默认5001）
- 建议在内网环境使用，如需外网访问请做好安全防护

## 浏览器支持
- 推荐使用 Chrome、Firefox、Edge 等现代浏览器
- 需要启用 JavaScript
- 建议使用 1920x1080 或更高分辨率显示器

## 技术栈
- 后端：Python Flask
- 前端：React + TailwindCSS
- 图表：Chart.js
- 容器化：Docker 