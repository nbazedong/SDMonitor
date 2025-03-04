# 使用官方 Python 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量（保持 ENV 语法正确）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装依赖
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .


# 在 COPY . . 之后添加
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]
# CMD：容器启动时执行的命令