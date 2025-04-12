import requests
import json
import base64
from pathlib import Path

def encode_image_to_base64(image_path):
    """将图片文件转换为base64编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_mime_type(file_path):
    """根据文件扩展名获取MIME类型"""
    extension = Path(file_path).suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/png')

# 读取本地图片并转换为base64
image_path = "f:\\work\\code\\AIcode\\book_practice\\resources\\错题本原始资料20250411\\原始试卷1.png"
base64_image = encode_image_to_base64(image_path)
mime_type = get_mime_type(image_path)
image_url = f"data:{mime_type};base64,{base64_image}"
#image_url2 = "https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/Obsidian/%E5%8E%9F%E5%A7%8B%E8%AF%95%E5%8D%B71.png"  # 移除多余的右括号
proxies = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
}

def process_stream_response(response):
    """处理流式响应"""
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
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

def process_normal_response(response):
    """处理非流式响应"""
    if response.status_code == 200:
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            content = response_json['choices'][0].get('message', {}).get('content', '')
            print(content)
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)

# 设置是否使用流式输出
use_stream = False

# 发送请求
response = requests.post(
    url="https://api.302.ai/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-Udf6lsiyUIExHTrE0kXxAXpYemjY9SzvU0EXmYbgbUSlzCeE",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/traefan/book_practice",
    },
    json={
        "model": "gemini-2.0-flash-lite-preview-02-05",
        "stream": use_stream,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
# 角色定义
你是一位中小学错题收集与整理专家，擅长从学生的考试题目中提取错误题目，并按照题型（选择题、填空题、判断题、问答题）进行分类归纳。你会为每道错题提供正确答案，并生成一份结构化的错题本，以JSON格式呈现，便于学生复习和存入数据库。

# 任务目标
根据用户提供的考试题目和错误信息，完成以下任务：
1. **提取错误题目**：识别并提取所有答错的题目。
2. **分类整理**：将错误题目按照以下四类进行分类：
   - **选择题**
   - **填空题**
   - **判断题**
   - **问答题**
3. **JSON格式输出**：
   - 生成一个包含所有题目的JSON对象。
   - 即使某类题型没有错题，也保留该类型的空数组。
4. **符合数据库结构**：确保输出的JSON格式符合给定的数据库表结构。

# 输入格式
请提供以下信息：
- 考试题目列表（包括题干、选项（如有）、学生答案和正确答案）。
- 学生的错误标记（哪些题目是错误的）。
- 学科信息。
- 难度等级（1-5）。

# 输出格式
生成一份JSON格式的错题本，结构如下：

```json
{
  "error_questions": [
    {
      "question_text": "题目内容",
      "subject": "学科名称",
      "question_type": "题目类型",
      "difficulty": 难度等级,
      "answer": "正确答案",
      "user_answer": "用户答案",
      "explanation": "解析（如有）"
    },
    // ... 更多题目
  ]
}
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
    proxies=proxies,
)

# 根据模式选择处理方式
if use_stream:
    process_stream_response(response)
else:
    process_normal_response(response)