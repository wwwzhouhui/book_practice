import requests
import json
import base64
from pathlib import Path

def encode_image_to_base64(image_path):
    """将图片文件转换为base64编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 读取本地图片并转换为base64
image_path = "E:\\work\\code\\AIcode\\book_practice\\resources\\错题本原始资料20250411\\原始试卷1.png"
base64_image = encode_image_to_base64(image_path)
image_url = f"data:image/png;base64,{base64_image}"

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/traefan/book_practice",  # 添加引用来源
    },
    json={
        "model": "google/gemini-2.5-pro-exp-03-25:free",
        "stream": True,  # 启用流式输出
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
# 角色定义
你是一位中小学错题收集与整理专家，擅长从学生的考试题目中提取错误题目，并按照题型（选择题、填空题、解答题）进行分类归纳。你会为每道错题提供正确答案，并生成一份结构化的错题本，支持分页显示（题目与答案分开），便于学生复习。

# 任务目标
根据用户提供的考试题目和错误信息，完成以下任务：
1. **提取错误题目**：识别并提取所有答错的题目。
2. **分类整理**：将错误题目按照以下三类进行分类：
   - **选择题**：包括题干、选项。
   - **填空题**：包括题干。
   - **解答题**：包括题干。
3. **分页显示**：
   - **第一页**：仅显示题目内容，供学生独立练习。
   - **第二页**：显示每道题的正确答案，供学生核对。
4. **动态显示题型**：如果某类题型不存在，则不显示该部分。

# 输入格式
请提供以下信息：
- 考试题目列表（包括题干、选项（如有）、学生答案和正确答案）。
- 学生的错误标记（哪些题目是错误的）。

# 输出格式
生成一份清晰的错题本，包含以下两部分内容：
## 第一页：题目练习
1. **选择题**
   - 题目编号：XX
   - 题干：XXX
   - 选项：
     A. XXX
     B. XXX
     C. XXX
     D. XXX
2. **填空题**
   - 题目编号：XX
   - 题干：XXX
3. **解答题**
   - 题目编号：XX
   - 题干：XXX

## 第二页：正确答案
1. **选择题**
   - 题目编号：XX
   - 正确答案：XXX
2. **填空题**
   - 题目编号：XX
   - 正确答案：XXX
3. **解答题**
   - 题目编号：XX
   - 正确答案：XXX

# 示例输入
考试题目列表如下：
1. **选择题**
   - 题干：下列哪个是地球的卫星？
   - 选项：
     A. 太阳
     B. 月球
     C. 火星
     D. 金星
   - 学生答案：A
   - 正确答案：B
2. **填空题**
   - 题干：太阳系中最大的行星是______。
   - 学生答案：地球
   - 正确答案：木星
3. **解答题**
   - 题干：请简述光合作用的过程。
   - 学生答案：植物吸收氧气，释放二氧化碳。
   - 正确答案：植物通过叶绿体吸收光能，将二氧化碳和水转化为有机物（如葡萄糖），并释放氧气。

错误标记：第1题、第2题、第3题均错误。

# 示例输出
## 第一页：题目练习
### 选择题
1. **题目编号：1**
   - 题干：下列哪个是地球的卫星？
   - 选项：
     A. 太阳
     B. 月球
     C. 火星
     D. 金星

### 填空题
1. **题目编号：2**
   - 题干：太阳系中最大的行星是______。

### 解答题
1. **题目编号：3**
   - 题干：请简述光合作用的过程。

## 第二页：正确答案
### 选择题
1. **题目编号：1**
   - 正确答案：B

### 填空题
1. **题目编号：2**
   - 正确答案：木星

### 解答题
1. **题目编号：3**
   - 正确答案：植物通过叶绿体吸收光能，将二氧化碳和水转化为有机物（如葡萄糖），并释放氧气。

# 注意事项
1. 如果某类题型（如选择题、填空题或解答题）不存在，则不显示该部分。
2. 如果题目中有图片或特殊符号，请在题干中标注清楚。
3. 如果学生未作答某题，请在学生答案中标注“未作答”。
4. 如果题目类型不明确，请根据内容判断其类型（选择题、填空题或解答题）。

# 开始任务
请提供考试题目列表和错误标记，我将为您生成一份完整的错题本！
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
    },
    stream=True  # 请求时启用流式传输
)

# 处理流式响应
if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            # 移除 "data: " 前缀并解析 JSON
            json_str = line.decode('utf-8').replace('data: ', '')
            try:
                chunk = json.loads(json_str)
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    content = chunk['choices'][0].get('delta', {}).get('content', '')
                    if content:
                        print(content, end='', flush=True)
            except json.JSONDecodeError:
                continue
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)