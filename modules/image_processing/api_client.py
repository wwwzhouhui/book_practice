import logging
import json
import os
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GiteeAIClient:
    """与Gitee AI API交互的客户端"""
    
    def __init__(self, api_key: str = "CSW0YJEY0AJVXWFSOA6CKRI6H06UAJUYK7IS1LBZ"):
        """
        初始化Gitee AI客户端
        
        Args:
            api_key: Gitee AI API密钥
        """
        self.api_key = api_key
        self.base_url = "https://ai.gitee.com/v1"
        
        # 完全按照文档格式创建客户端
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=api_key,
            )
            logger.info("成功创建OpenAI客户端")
        except Exception as e:
            logger.error(f"创建OpenAI客户端失败: {e}")
            self.client = None
            logger.warning("无法创建OpenAI客户端，将使用模拟数据")
        
    def _fix_json_format(self, json_text: str) -> str:
        """
        修复常见的JSON格式错误
        
        Args:
            json_text: 可能包含错误的JSON文本
            
        Returns:
            修复后的JSON文本
        """
        # 移除末尾的逗号
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        # 移除末尾的注释
        json_text = re.sub(r'//.*?(\n|$)', '\n', json_text)
        
        # 在键值对中添加缺失的引号
        json_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_text)
        
        # 修复无效的Date对象
        json_text = re.sub(r'_type_\d+_questions_[\d\-T:.Z]+', '"questions"', json_text)
        
        return json_text
        
    def call_qwen_vl(self, prompt: str, image_url: str, temperature: float = 0.2) -> str:
        """
        调用Qwen2.5-VL-32B-Instruct模型进行图像分析
        
        Args:
            prompt: 提示词
            image_url: 图像URL或base64编码
            temperature: 温度参数，控制创造性
            
        Returns:
            模型响应文本
        """
        if self.client is None:
            logger.warning("OpenAI客户端未初始化，返回模拟数据")
            return """
            {
                "sections": [
                    {
                        "section_number": "1",
                        "section_title": "选择题",
                        "questions": [
                            {
                                "question_number": "1",
                                "question_text": "模拟问题1",
                                "printed_text": "A. 选项A B. 选项B",
                                "handwritten_notes": [
                                    {"text": "选A", "color": "blue"}
                                ]
                            }
                        ]
                    }
                ]
            }
            """
            
        try:
            # 构建更明确的提示词，要求模型返回JSON格式
            enhanced_prompt = f"""
            {prompt}
            
            严格遵循以下要求：
            1. 只返回有效的JSON格式数据，不要返回任何其他文本或解释
            2. 确保键名使用双引号，如 "key": "value"
            3. 不要在数组或对象的最后一个元素后加逗号
            4. 不要使用 ```json 或 ``` 标记，直接返回原始JSON
            5. 确保每个JSON对象的键值对格式正确
            
            输出格式样例：
            {{
                "sections": [
                    {{
                        "section_number": "1",
                        "section_title": "选择题",
                        "questions": [
                            {{
                                "question_number": "1",
                                "question_text": "题目内容...",
                                "printed_text": "印刷文本...",
                                "handwritten_notes": [
                                    {{"text": "手写内容...", "color": "blue"}}
                                ]
                            }}
                        ]
                    }}
                ]
            }}
            
            请直接返回有效的JSON，不要包含其他文本。
            """
            
            # 严格按照用户提供的格式创建请求，但减小max_tokens值
            response = self.client.chat.completions.create(
                model="Qwen2.5-VL-32B-Instruct",
                stream=True,
                max_tokens=4000,  # 减小为更合理的值
                temperature=temperature,
                top_p=1,
                extra_body={
                    "top_k": -1,
                },
                frequency_penalty=1.2,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个图像分析助手，只返回有效的JSON格式数据，不要包含任何其他文本或解释。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": enhanced_prompt
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
            )
            
            # 处理流式响应
            result_text = ""
            try:
                for chunk in response:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                            content = chunk.choices[0].delta.content
                            if content:
                                result_text += content
            except Exception as stream_error:
                logger.error(f"处理流式响应时出错: {stream_error}")
                # 如果已经收集了一些内容，就使用它，否则抛出异常
                if not result_text:
                    raise stream_error
            
            logger.info(f"成功收到API响应，长度: {len(result_text)}")
            return result_text
            
        except Exception as e:
            logger.error(f"调用Qwen VL模型失败: {e}")
            # 返回一个JSON格式的错误
            return '{"error": "调用模型失败", "message": "' + str(e).replace('"', '\\"') + '"}'
    
    def call_qwq(self, prompt: str, temperature: float = 0.2, system_prompt: Optional[str] = None) -> str:
        """
        调用QwQ-32B模型进行文本处理
        
        Args:
            prompt: 提示词
            temperature: 温度参数，控制创造性
            system_prompt: 系统提示词，可选
            
        Returns:
            模型响应文本
        """
        if self.client is None:
            logger.warning("OpenAI客户端未初始化，返回模拟数据")
            return """
            {
                "sections": [
                    {
                        "section_number": "1",
                        "section_title": "选择题",
                        "questions": [
                            {
                                "question_number": "1",
                                "question_text": "模拟问题1",
                                "printed_text": "A. 选项A B. 选项B",
                                "handwritten_notes": [
                                    {"text": "选A", "color": "blue"}
                                ],
                                "answer": "A. 选项A",
                                "explanation": "这是模拟的解析"
                            }
                        ]
                    }
                ]
            }
            """
            
        try:
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加用户提示词 - 加强对JSON格式的要求
            enhanced_prompt = prompt + """
            务必确保返回的是有效的JSON格式，特别注意：
            1. 不要在对象或数组的最后一个元素后面添加逗号
            2. 所有键名必须用双引号包围
            3. 不要在JSON中包含注释或特殊格式
            """
            
            messages.append({
                "role": "user",
                "content": enhanced_prompt
            })
            
            # 按照文档格式创建请求
            response = self.client.chat.completions.create(
                model="QwQ-32B",
                stream=True,
                max_tokens=4000,  # 减小为更合理的值
                temperature=temperature,
                top_p=0.2,
                extra_body={
                    "top_k": 50,
                },
                frequency_penalty=0,
                messages=messages
            )
            
            # 处理流式响应
            result_text = ""
            try:
                for chunk in response:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                            content = chunk.choices[0].delta.content
                            if content:
                                result_text += content
            except Exception as stream_error:
                logger.error(f"处理流式响应时出错: {stream_error}")
                # 如果已经收集了一些内容，就使用它，否则抛出异常
                if not result_text:
                    raise stream_error
            
            logger.info(f"成功收到API响应，长度: {len(result_text)}")
            return result_text
            
        except Exception as e:
            logger.error(f"调用QwQ模型失败: {e}")
            # 返回一个JSON格式的错误
            return '{"error": "调用模型失败", "message": "' + str(e).replace('"', '\\"') + '"}'
    
    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        从模型响应中提取JSON
        
        Args:
            response_text: 模型响应文本
            
        Returns:
            解析后的JSON字典
        """
        try:
            # 检查是否是错误响应
            if response_text.startswith('{"error"'):
                try:
                    return json.loads(response_text)
                except:
                    return {"error": "调用模型失败"}
                
            # 清理可能的非JSON内容
            json_str = response_text.strip()
            
            # 记录原始响应方便调试
            if len(json_str) > 1000:
                logger.info(f"原始响应(前500个字符): {json_str[:500]}...")
                logger.info(f"原始响应(后500个字符): {json_str[-500:]}...")
            else:
                logger.info(f"原始响应: {json_str}")
            
            # 首先尝试寻找JSON代码块
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
                logger.info("使用```json代码块提取")
            elif "```" in json_str:
                try:
                    # 尝试找到第一个和最后一个```之间的内容
                    start_idx = json_str.find("```") + 3
                    temp_str = json_str[start_idx:]
                    end_idx = temp_str.find("```")
                    if end_idx > 0:
                        json_str = temp_str[:end_idx].strip()
                        logger.info("使用```代码块提取")
                    else:
                        # 找不到结束标记时，尝试其他提取方法
                        parts = json_str.split("```")
                        if len(parts) >= 3:  # 至少有开始和结束标记
                            json_str = parts[1].strip()
                            logger.info("使用```分割提取")
                except Exception as e:
                    logger.warning(f"尝试提取```代码块失败: {e}")
            
            # 如果响应以自然语言开始，尝试寻找第一个JSON对象
            # 提取第一个 '{' 和最后一个 '}' 之间的内容
            start_idx = json_str.find("{")
            end_idx = json_str.rfind("}")
            
            if start_idx >= 0 and end_idx > start_idx:
                original_json_str = json_str
                json_str = json_str[start_idx:end_idx + 1]
                if json_str != original_json_str:
                    logger.info(f"提取了JSON对象，长度从 {len(original_json_str)} 变为 {len(json_str)}")
            else:
                logger.error("无法在响应中找到完整的JSON对象")
                return {
                    "error": "无法找到有效的JSON结构",
                    "original_response": response_text[:500] + ("..." if len(response_text) > 500 else ""),
                    "sections": [
                        {
                            "section_number": "1",
                            "section_title": "错误",
                            "questions": [
                                {
                                    "question_number": "1",
                                    "question_text": "无法从响应中提取JSON",
                                    "printed_text": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                                    "handwritten_notes": []
                                }
                            ]
                        }
                    ]
                }
            
            # 首先尝试直接解析
            try:
                result_dict = json.loads(json_str)
                logger.info("成功直接解析JSON")
                return result_dict
            except json.JSONDecodeError as first_error:
                logger.error(f"直接解析JSON失败: {first_error}, 错误位置: {first_error.pos}, 行: {first_error.lineno}, 列: {first_error.colno}")
                
                # 记录错误周围的内容
                error_pos = first_error.pos
                start_pos = max(0, error_pos - 50)
                end_pos = min(len(json_str), error_pos + 50)
                error_context = json_str[start_pos:end_pos]
                logger.error(f"错误上下文: ...{error_context}...")
                
                # 修复常见的JSON格式错误
                json_str = self._fix_json_format(json_str)
                
                # 尝试再次解析
                try:
                    result_dict = json.loads(json_str)
                    logger.info("通过基本修复成功解析JSON")
                    return result_dict
                except json.JSONDecodeError as second_error:
                    logger.error(f"基本修复后解析JSON失败: {second_error}")
                    
                    # 尝试更激进的修复方法
                    try:
                        # 移除所有注释和多余的空白
                        json_str = re.sub(r'//.*?(\n|$)', '\n', json_str)
                        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                        
                        # 修复单引号问题
                        json_str = json_str.replace("'", '"')
                        
                        # 修复错误的布尔值和null值
                        json_str = re.sub(r':\s*True\b', ': true', json_str)
                        json_str = re.sub(r':\s*False\b', ': false', json_str)
                        json_str = re.sub(r':\s*None\b', ': null', json_str)
                        
                        # 修复尾部逗号问题
                        json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)
                        
                        # 修复缺少引号的键名
                        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_str)
                        
                        # 尝试再次解析
                        result_dict = json.loads(json_str)
                        logger.info("通过激进修复成功解析JSON")
                        return result_dict
                    except Exception as repair_error:
                        logger.error(f"激进修复JSON失败: {repair_error}")
                        
                        # 尝试逐行修复
                        try:
                            lines = json_str.split("\n")
                            for i in range(len(lines)):
                                logger.debug(f"行 {i+1}: {lines[i]}")
                                if ":" in lines[i] and "\"" not in lines[i]:
                                    # 可能是缺少引号的键
                                    key_part = lines[i].split(":")[0].strip()
                                    value_part = ":".join(lines[i].split(":")[1:])
                                    lines[i] = f'"{key_part}": {value_part}'
                            
                            json_str = "\n".join(lines)
                            result_dict = json.loads(json_str)
                            logger.info("通过逐行修复成功解析JSON")
                            return result_dict
                        except Exception as line_repair_error:
                            logger.error(f"逐行修复JSON失败: {line_repair_error}")
                
                # 如果所有解析尝试都失败，则尝试提取有效的部分
                try:
                    # 创建一个标准格式的返回结构
                    standard_format = {
                        "sections": [
                            {
                                "section_number": "1",
                                "section_title": "试卷内容",
                                "questions": []
                            }
                        ]
                    }
                    
                    # 尝试提取JSON对象或数组
                    object_matches = re.findall(r'{[^{}]*}', json_str)
                    for match in object_matches:
                        try:
                            partial_json = json.loads(match)
                            if isinstance(partial_json, dict):
                                # 将有效的部分合并到标准格式中
                                logger.info(f"找到有效的部分JSON: {list(partial_json.keys())}")
                                break
                        except:
                            continue
                    
                    # 尝试手动构建内容
                    # 搜索题目和问题
                    question_pattern = r'"question[^"]*":\s*"([^"]*)"'
                    printed_pattern = r'"printed[^"]*":\s*"([^"]*)"'
                    handwritten_pattern = r'"handwritten[^"]*":\s*\[(.*?)\]'
                    
                    questions = re.findall(question_pattern, json_str)
                    printed = re.findall(printed_pattern, json_str)
                    handwritten = re.findall(handwritten_pattern, json_str, re.DOTALL)
                    
                    if questions:
                        logger.info(f"找到 {len(questions)} 个问题文本")
                        for i, q in enumerate(questions):
                            question = {
                                "question_number": str(i+1),
                                "question_text": q,
                                "printed_text": printed[i] if i < len(printed) else "",
                                "handwritten_notes": []
                            }
                            standard_format["sections"][0]["questions"].append(question)
                        
                        logger.info("成功构建部分内容")
                        return standard_format
                        
                except Exception as extract_error:
                    logger.error(f"尝试提取部分内容失败: {extract_error}")
                
                # 尝试简单重构响应
                if "模拟问题" in response_text:
                    mock_data = {
                        "sections": [
                            {
                                "section_number": "1",
                                "section_title": "选择题",
                                "questions": [
                                    {
                                        "question_number": "1",
                                        "question_text": "模拟问题1",
                                        "printed_text": "A. 选项A B. 选项B",
                                        "handwritten_notes": [
                                            {"text": "选A", "color": "blue"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                    logger.info("返回模拟数据结构")
                    return mock_data
            
            # 所有尝试都失败，返回错误
            return {
                "error": "无法解析模型响应",
                "original_response": response_text[:500] + ("..." if len(response_text) > 500 else ""),
                "sections": [
                    {
                        "section_number": "1",
                        "section_title": "API响应",
                        "questions": [
                            {
                                "question_number": "1",
                                "question_text": "API原始响应",
                                "printed_text": response_text[:300] + ("..." if len(response_text) > 300 else ""),
                                "handwritten_notes": []
                            }
                        ]
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"提取JSON时出错: {e}")
            return {
                "error": "提取JSON失败",
                "message": str(e),
                "original_response": response_text[:500] + ("..." if len(response_text) > 500 else ""),
                "sections": [
                    {
                        "section_number": "1",
                        "section_title": "错误",
                        "questions": [
                            {
                                "question_number": "1",
                                "question_text": f"错误: {str(e)}",
                                "printed_text": "",
                                "handwritten_notes": []
                            }
                        ]
                    }
                ]
            }
    
    def analyze_exam_paper(self, image_url: str) -> Dict[str, Any]:
        """
        分析考试试卷图像
        
        Args:
            image_url: 图像URL或base64编码
            
        Returns:
            分析结果
        """
        # 构建分析试卷的提示词
        prompt = """
        分析这张试卷图像，完成以下任务：
        1. 识别出所有文本内容，包括印刷体和手写体
        2. 区分不同类型的文本（试题文本、印刷体答案、手写笔记等）
        3. 识别手写笔记的不同颜色（如蓝色、红色、黑色等）
        4. 将试卷划分为大题和小题
        5. 按照以下JSON格式返回结果:
        {
            "sections": [
                {
                    "section_number": "1",
                    "section_title": "选择题",
                    "questions": [
                        {
                            "question_number": "1",
                            "question_text": "...",
                            "printed_text": "...",
                            "handwritten_notes": [
                                {"text": "...", "color": "blue"},
                                {"text": "...", "color": "red"}
                            ]
                        }
                    ]
                }
            ]
        }
        只返回JSON格式，不要有其他文本。确保JSON格式有效，所有键必须用双引号，不要在最后一个元素后添加逗号。
        """
        
        # 调用模型
        response = self.call_qwen_vl(prompt, image_url)
        
        # 提取JSON
        result = self.extract_json_from_response(response)
        
        return result
    
    def verify_and_answer_questions(self, questions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证问题并生成答案
        
        Args:
            questions_data: 问题数据
            
        Returns:
            添加了答案的问题数据
        """
        # 将问题数据转换为JSON字符串
        questions_json = json.dumps(questions_data, ensure_ascii=False)
        
        # 构建系统提示词
        system_prompt = """You are a helpful assistant specialized in educational content and exam questions. 
        You should analyze questions carefully and provide accurate answers with detailed explanations."""
        
        # 构建用户提示词
        prompt = f"""
        以下是从试卷中提取的问题数据:
        {questions_json}
        
        请执行以下任务:
        1. 核对每个问题的文本，确保内容准确
        2. 为每个问题提供详细的答案和解析
        3. 返回修正和补充后的完整JSON，保持原有结构，但为每个问题添加"answer"和"explanation"字段
        
        只返回JSON格式，不要有其他文本。确保JSON格式有效，所有键必须用双引号，不要在最后一个元素后添加逗号。
        """
        
        # 调用模型
        response = self.call_qwq(prompt, system_prompt=system_prompt)
        
        # 提取JSON
        result = self.extract_json_from_response(response)
        
        return result 