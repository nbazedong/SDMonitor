# 使用官方 Python 基础镜像
FROM python:3.12-slim as builder

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 使用更小的基础镜像作为最终镜像
FROM python:3.12-slim

WORKDIR /app

# 从 builder 阶段复制 Python 环境和应用代码
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /app .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["flask", "run", "--host=0.0.0.0"] 