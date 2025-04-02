import sys
import argparse
from pathlib import Path
from modules.image_processing.image_processor import ImageProcessor

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='测试图像处理模块')
    parser.add_argument('image_paths', nargs='+', help='要处理的图像文件路径')
    parser.add_argument('--api_key', default="CSW0YJEY0AJVXWFSOA6CKRI6H06UAJUYK7IS1LBZ", 
                        help='Gitee AI API密钥')
    parser.add_argument('--use_mock', action='store_true', help='使用模拟数据进行测试，不调用实际API')
    args = parser.parse_args()
    
    # 创建图像处理器
    processor = ImageProcessor(api_key=args.api_key, use_mock=args.use_mock)
    
    # 处理图像
    print(f"开始处理 {len(args.image_paths)} 个图像文件...")
    
    if args.use_mock:
        print("使用模拟数据进行测试，不会调用实际API")
        
    results = processor.process_images(args.image_paths)
    
    # 显示结果
    for i, result in enumerate(results.get("results", [])):
        image_path = result.get("image_path", "")
        print(f"\n处理结果 {i+1}: {image_path}")
        
        if "error" in result:
            print(f"错误: {result['error']}")
            continue
        
        print(result.get("display_text", ""))
        print(f"详细结果已保存到: {result.get('result_path', '')}")

if __name__ == "__main__":
    main()



# 测试结果

# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ python test_image_processor.py resources/1.png
# 2025-04-03 01:56:42,959 - modules.image_processing.api_client - INFO - 成功创建OpenAI客户端
# 开始处理 1 个图像文件...
# 2025-04-03 01:56:42,959 - modules.image_processing.image_processor - INFO - 正在处理图像: resources/1.png
# 2025-04-03 01:56:55,764 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 01:57:35,143 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 1073
# 2025-04-03 01:57:35,144 - modules.image_processing.api_client - ERROR - 第一次JSON解析失败: Expecting ':' delimiter: line 20 column 9 (char 1008)
# 2025-04-03 01:57:35,145 - modules.image_processing.api_client - ERROR - 激进修复JSON失败: Expecting ':' delimiter: line 20 column 9 (char 1008)
# 2025-04-03 01:57:35,364 - modules.image_processing.image_processor - INFO - 检测到 2 个手写区域
# 2025-04-03 01:57:35,401 - modules.image_processing.image_processor - INFO - 分割结果: 4 个大题

# 处理结果 1: resources/1.png
# 错误: 无法解析模型响应
# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ python test_image_processor.py resources/1.png
# 2025-04-03 01:59:01,015 - modules.image_processing.api_client - INFO - 成功创建OpenAI客户端
# 开始处理 1 个图像文件...
# 2025-04-03 01:59:01,015 - modules.image_processing.image_processor - INFO - 正在处理图像: resources/1.png
# 2025-04-03 01:59:10,960 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 01:59:10,986 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 214
# 2025-04-03 01:59:10,986 - modules.image_processing.api_client - INFO - 原始响应: {
#     ".sections": [
#         {
#             "section_number": "1",
#             "section_title": "",
#             "question_text": "",
#             "printed_text": "",
#             "handwritenotes": []
#         }
#     ]
# }
# 2025-04-03 01:59:10,986 - modules.image_processing.api_client - INFO - 成功直接解析JSON
# 2025-04-03 01:59:11,193 - modules.image_processing.image_processor - INFO - 检测到 2 个手写区域
# 2025-04-03 01:59:11,231 - modules.image_processing.image_processor - INFO - 分割结果: 4 个大题
# 2025-04-03 01:59:17,032 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 01:59:51,021 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 2419
# 2025-04-03 01:59:51,021 - modules.image_processing.api_client - INFO - 原始响应(前500个字符): 好的，我现在需要处理用户提供的这个JSON数据。首先，用户给了一个从试卷中提取的问题数据，看起来结构是sections数组里有一个对象，里面包含section_number、section_title、question_text、printed_text和handwritenotes。但问题在于，这些字段的内容都是空的，除了section_number是"1"，其他都是空字符串或空数组。

# 用户的要求是让我执行三个任务：1. 核对每个问题的文本，确保内容准确；2. 为每个问题提供详细的答案和解析；3. 返回修正和补充后的完整JSON，保持原有结构，但添加answer和explanation字段。同时，用户强调只返回JSON，不要其他文本，并且要确保JSON格式有效，键用双引号，没有多余的逗号。

# 首先，我需要分析用户提供的原始数据。看起来用户可能是在测试我的处理能力，或者他们提供的示例数据可能有问题，因为里面的问题文本都是空的。这种情况下，我应该如何处理呢？可能用户希望我假设存在一个问题，或者他们可能在示例中没有正确填充数据。但根据用户给出的输入，我必须严格按照他们提供的结构来处理。
# ...
# 2025-04-03 01:59:51,021 - modules.image_processing.api_client - INFO - 原始响应(后500个字符): notes": [],
#       "answer": "x = 2",
#       "explanation": "将方程两边减去3，得到2x = 4，然后两边除以2，得到x = 2。"
#     }
#   ]
# }

# 这样就满足了用户的所有要求：核对问题文本（假设的问题文本是合理的），添加了答案和解析，并且保持了原有结构，同时确保JSON格式正确。
# </think>

# ```json
# {
#   "sections": [
#     {
#       "section_number": "1",
#       "section_title": "",
#       "question_text": "假设问题文本：解方程2x + 3 = 7。",
#       "printed_text": "",
#       "handwritenotes": [],
#       "answer": "x = 2",
#       "explanation": "步骤1：将方程两边减去3，得到2x = 4。步骤2：两边除以2，解得x = 2。验证：代入原方程，2*(2)+3=7成立。"
#     }
#   ]
# }
# ```...
# 2025-04-03 01:59:51,022 - modules.image_processing.api_client - INFO - 使用```json代码块提取
# 2025-04-03 01:59:51,022 - modules.image_processing.api_client - INFO - 成功直接解析JSON
# 2025-04-03 01:59:51,022 - modules.image_processing.result_formatter - INFO - 结果已保存到: /home/cine/Documents/Github/book_practice/results/result_1.json

# 处理结果 1: resources/1.png
# 共检测到 1 个大题，0 个小题
# 疑似错题数量: 0

# 大题概览:
# 1.  (包含0个小题)
# 详细结果已保存到: /home/cine/Documents/Github/book_practice/results/result_1.json
# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ ^C
# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ python test_image_processor.py resources/1.png
# 2025-04-03 02:02:55,278 - modules.image_processing.api_client - INFO - 成功创建OpenAI客户端
# 开始处理 1 个图像文件...
# 2025-04-03 02:02:55,278 - modules.image_processing.image_processor - INFO - 正在处理图像: resources/1.png
# 2025-04-03 02:03:07,871 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 02:03:07,886 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 27
# 2025-04-03 02:03:07,886 - modules.image_processing.api_client - INFO - 原始响应: {
#     "answer": "无法完成任务。"
# }
# 2025-04-03 02:03:07,886 - modules.image_processing.api_client - INFO - 成功直接解析JSON
# 2025-04-03 02:03:08,148 - modules.image_processing.image_processor - INFO - 检测到 2 个手写区域
# 2025-04-03 02:03:08,184 - modules.image_processing.image_processor - INFO - 分割结果: 4 个大题
# 2025-04-03 02:03:11,884 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 02:04:39,625 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 4278
# 2025-04-03 02:04:39,626 - modules.image_processing.api_client - INFO - 原始响应(前500个字符): 好的，我现在需要处理用户提供的任务。首先，用户给了一个JSON数据，里面有一个问题，但答案是“无法完成任务。”。用户要求我检查每个问题的文本是否准确，然后为每个问题添加详细的答案和解析，并返回修正后的JSON，保持原有结构，同时添加"answer"和"explanation"字段。

# 首先，我需要确认用户提供的原始数据是否正确。用户给出的JSON结构是：

# {
#   "answer": "无法完成任务。"
# }

# 看起来这个JSON可能不完整，因为通常一个问题应该包含更多字段，比如问题描述、选项等。但根据用户提供的信息，可能这个JSON是某个问题的片段，或者用户可能希望我根据这个答案来生成对应的解析。不过用户提到“从试卷中提取的问题数据”，可能这个JSON结构有问题，或者可能用户希望我根据现有的答案来补充其他字段？

# 不过根据用户的具体指示，我需要执行以下步骤：

# 1. 核对每个问题的文本，确保内容准确。但用户提供的JSON中只有"answer"字段，没有问题文本，这可能意味着原始数据可能不完整，或者用户可能希望我假设问题文本存在，但需要补充？

# 这里可能存在误解。用户可能提供的原始数据可...
# 2025-04-03 02:04:39,627 - modules.image_processing.api_client - INFO - 原始响应(后500个字符): 乏必要的资源、权限不足、步骤错误或外部条件限制。具体原因需根据任务的具体要求和当前环境分析。"
# }

# 但需要确保JSON格式正确，没有其他字段。用户要求保持原有结构，所以如果原结构只有"answer"，则添加"explanation"即可。

# 因此，最终的JSON应该是：

# {
#   "answer": "无法完成任务。",
#   "explanation": "任务无法完成可能由于缺乏必要的资源、权限不足、步骤错误或外部条件限制。具体原因需根据任务的具体要求和当前环境分析。"
# }

# 但需要确保没有其他错误，比如逗号或引号问题。例如，确保键名用双引号，没有多余的逗号。

# 现在，我需要确保这个JSON是有效的。检查：

# - 所有键名用双引号：是的。
# - 没有最后一个元素后的逗号：是的。
# - 结构正确：是的。

# 因此，最终的JSON应该如上所示。
# </think>

# ```json
# {
#   "answer": "无法完成任务。",
#   "explanation": "任务无法完成可能由于缺乏必要的资源、权限不足、步骤错误或外部条件限制。具体原因需根据任务的具体要求和当前环境分析。"
# }
# ```...
# 2025-04-03 02:04:39,627 - modules.image_processing.api_client - INFO - 使用```json代码块提取
# 2025-04-03 02:04:39,627 - modules.image_processing.api_client - INFO - 成功直接解析JSON
# 2025-04-03 02:04:39,628 - modules.image_processing.result_formatter - INFO - 结果已保存到: /home/cine/Documents/Github/book_practice/results/result_1.json

# 处理结果 1: resources/1.png
# 未检测到任何题目
# 详细结果已保存到: /home/cine/Documents/Github/book_practice/results/result_1.json
# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ ^C
# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ python test_image_processor.py resources/1.png
# 2025-04-03 02:06:01,177 - modules.image_processing.api_client - INFO - 成功创建OpenAI客户端
# 开始处理 1 个图像文件...
# 2025-04-03 02:06:01,177 - modules.image_processing.image_processor - INFO - 正在处理图像: resources/1.png
# 2025-04-03 02:06:14,539 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 02:06:43,722 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 931
# 2025-04-03 02:06:43,722 - modules.image_processing.api_client - INFO - 原始响应: {
#     "sheets": [
#         {
#             "section_number": "1",
#             "section_title": "",
#             "table_data": {
#                 "headers": ["节目", "A", "B", "C", "D"],
#                 "rows": [
#                     ["演员人数", 10, 2, 10, 1],
#                     ["彩排时長", 30, 10, 20, 10]
#                 ]
#             },
#             "question_text": [
#                 {
#                     "_id_": "_q_1",
#                     "_text_": [
#                         {"type": "printed_text", "_content_":"已知每位演员只参演一個节目。一位演员的彩排时间是从第一个彩排的节目彩排开始到位"},
#                         {"type":"handwriten","color":"red","content":"演員的節目的彩排開始的时间间隔（不含換場時間等其他因素）. 若節目的順後順先後顺序排列，則節目的D的演員的候場時間為"},
#                         {"type":"handwriten","color":"red","content":""},
#                         {"type":"handwriten","color":"blue","content":""}
#                     ]
#                 }
                
#             ],
            
#         }
#     ]
# }
# 2025-04-03 02:06:43,723 - modules.image_processing.api_client - ERROR - 直接解析JSON失败: Expecting property name enclosed in double quotes: line 26 column 9 (char 922), 错误位置: 922, 行: 26, 列: 9
# 2025-04-03 02:06:43,723 - modules.image_processing.api_client - ERROR - 错误上下文: ...             
#             ],
            
#         }
#     ]
# }...
# 2025-04-03 02:06:43,725 - modules.image_processing.api_client - INFO - 通过基本修复成功解析JSON
# 2025-04-03 02:06:43,978 - modules.image_processing.image_processor - INFO - 检测到 2 个手写区域
# 2025-04-03 02:06:44,014 - modules.image_processing.image_processor - INFO - 分割结果: 4 个大题
# 2025-04-03 02:06:47,265 - httpx - INFO - HTTP Request: POST https://ai.gitee.com/v1/chat/completions "HTTP/1.1 200 OK"
# 2025-04-03 02:07:40,268 - modules.image_processing.api_client - INFO - 成功收到API响应，长度: 3147
# 2025-04-03 02:07:40,269 - modules.image_processing.api_client - INFO - 原始响应(前500个字符): 好的，我现在需要处理用户提供的这个JSON数据，然后按照要求进行核对、解答并生成正确的JSON输出。首先，我得仔细看看用户给的问题数据是什么样的。

# 首先，用户的问题数据是一个包含试卷信息的JSON结构。里面有一个sheets数组，里面有一个对象，里面包含section_number、section_title、table_data和question_text。table_data里有headers和rows，分别是节目、A、B、C、D四个列，然后两行数据：演员人数和彩排时长。演员人数分别是10、2、10、1，彩排时长是30、10、20、10分钟。

# 接下来是question_text，里面有一个问题，问题文本有点混乱，可能因为手写部分和打印部分混合。问题的大意是说，每位演员只参演一个节目。一位演员的彩排时间是从第一个彩排的节目开始到该演员节目开始的时间间隔，不考虑换场时间等因素。如果节目顺序排列，那么节目D的演员候场时间是多少？

# 首先，我需要确认问题的准确性。原问题中的手写部分可能有些地方需要仔细分析。比如，问题中的“順後順先後顺序排列”可能是笔误，应该是“顺序排列”或者“先后顺序...
# 2025-04-03 02:07:40,269 - modules.image_processing.api_client - INFO - 原始响应(后500个字符): 因素）. 若節目的順後順先後顺序排列，則節目的D的演員的候場時間為"
#             },
#             {
#               "type": "handwriten",
#               "color": "red",
#               "content": ""
#             },
#             {
#               "type": "handwriten",
#               "color": "blue",
#               "content": ""
#             }
#           ],
#           "answer": "60分钟",
#           "explanation": "假设节目按照A、B、C、D的顺序排列，节目D的候场时间是从第一个节目开始到D开始的时间间隔。因此，D的候场时间等于前三个节目彩排时间的总和：A的30分钟 + B的10分钟 + C的20分钟 = 60分钟。"
#         }
#       ]
#     }
#   ]
# }
# ```...
# 2025-04-03 02:07:40,269 - modules.image_processing.api_client - INFO - 使用```json代码块提取
# 2025-04-03 02:07:40,269 - modules.image_processing.api_client - INFO - 成功直接解析JSON
# 2025-04-03 02:07:40,270 - modules.image_processing.result_formatter - INFO - 结果已保存到: /home/cine/Documents/Github/book_practice/results/result_1.json

# 处理结果 1: resources/1.png
# 未检测到任何题目
# 详细结果已保存到: /home/cine/Documents/Github/book_practice/results/result_1.json
# (py39) cine@cine-WS-C621E-SAGE-Series:~/Documents/Github/book_practice$ 