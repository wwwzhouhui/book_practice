# 辅导大师--基于AI教育的错题管理系统

基于Gradio的辅导大师--基于AI教育的错题管理系统，可以识别试卷中的印刷体和手写体文本，划分试题，并自动给出答案。

## 功能特点

- 支持上传多种格式的试卷图片（PNG、JPG等）
- 使用Qwen2.5-VL-32B-Instruct模型识别试卷中的文本和结构
- 区分印刷体试题和手写笔记，识别不同颜色的笔迹
- 自动划分试卷中的大题和小题
- 使用QwQ-32B模型核对试题并提供详细答案和解析
- 生成结构化的JSON格式结果，便于存储和查询
- 简洁美观的Gradio用户界面

## 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app/main.py
```

### 3. 使用方法

- 打开浏览器访问 `http://localhost:7860`
- 切换到"作业上传"选项卡
- 上传试卷图片
- 点击"开始处理"按钮
- 系统将自动处理图片，识别试题，并生成答案

## 技术架构

- **前端界面**: Gradio构建的Web界面
- **图像处理**: OpenCV进行图像预处理和分割
- **文本识别**: Qwen2.5-VL-32B-Instruct多模态大模型
- **答案生成**: QwQ-32B大语言模型
- **API集成**: 基于Gitee AI API

## 模块说明

- **app**: 主应用模块
- **modules/image_processing**: 图像处理模块
  - image_processor.py: 主处理类
  - api_client.py: API客户端
  - color_analysis.py: 颜色分析
  - document_segmentation.py: 文档分割
  - result_formatter.py: 结果格式化
- **ui**: 用户界面模块

## 提示

- 处理高分辨率图片可能需要较长时间
- 识别效果受图片质量影响，建议使用清晰图片
- 处理结果会保存在results目录下 