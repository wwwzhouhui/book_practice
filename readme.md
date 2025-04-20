# 1.运行环境

​    python3.12+

# 2.安装依赖

```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

# 3.运行

```
python app/main.py
# linux 后台运行
nohup python3 app/main.py> main.log&
```



浏览器打开http://localhost:7860/

 公网访问地址http://14.103.204.132:7860 

![image-20250402152606807](https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/image-20250402152606807.png)

# 4.docker环境运行

## 构建镜像

```
docker build -t book_practice:v0.0.1 .
```

## 运行容器
docker run -d -p 7860:7860 --name book_practice book_practice:v0.0.1

## 如果需要持久化存储，可以添加卷挂载
docker run -d \
    -p 7860:7860 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/results:/app/results \
    -v $(pwd)/uploads:/app/uploads \
    --name homework \
    book_practice:v0.0.1