# 使用Python 3.12官方镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖和字体
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    # 添加字体相关包
    fonts-droid-fallback \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 创建字体目录
RUN mkdir -p /app/fonts

# 复制项目字体文件（如果有的话）
COPY fonts/ ./fonts/

# 确保字体可用，创建备用字体链接
RUN ln -sf /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc /app/fonts/simhei.ttf \
    && fc-cache -fv

# 复制项目文件
COPY requirements.txt .
COPY app/ ./app/
COPY modules/ ./modules/
COPY ui/ ./ui/
COPY config.ini .
COPY *.py .

# 使用清华镜像源安装Python依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 创建必要的目录
RUN mkdir -p uploads results data

# 暴露端口
EXPOSE 7860

# 设置启动命令
CMD ["python", "app/main.py"]

