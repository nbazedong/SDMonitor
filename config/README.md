# 服务器配置说明

## 配置文件
- `servers.template.json`: 配置文件模板，用于 Git 提交和 Docker 构建
- `servers.json`: 实际的服务器配置文件（本地开发使用，不提交到 Git）

## 使用方法

1. 开发环境：
   - 复制 `servers.template.json` 为 `servers.json`
   - 根据实际环境修改 `servers.json` 中的服务器配置

2. Docker 环境：
   - 构建时会自动使用 `servers.template.json`
   - 如需自定义配置，可以挂载外部配置文件：
     ```bash
     docker run -v /path/to/your/servers.json:/app/config/servers.json ...
     ```

## 配置文件格式
```json
{
    "server_id": {
        "name": "服务器名称",
        "url": "http://server:port"
    }
}
``` 