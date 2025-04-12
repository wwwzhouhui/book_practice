import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from typing import List, Dict, Tuple, Any, Optional
import base64
import io
import logging
import json
import requests
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database_models import Base, ErrorQuestion  # 导入数据库模型
from modules.storage.database import Database
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 读取配置文件
config = configparser.ConfigParser()
# 在读取配置文件部分添加 COS 配置
#windows 路径
config.read('F:\\work\\code\\AIcode\\book_practice\\config.ini', encoding='utf-8')
#linux 路径
config.read('config.ini', encoding='utf-8')
# 从配置文件中获取API密钥
a302_api_key = config.get('302AI', '302_api_key')
a302_api_url = config.get('302AI', '302_api_url')
a302_model = config.get('302AI', '302_model')

# 添加代理配置读取
enable_proxy = config.getboolean('PROXY', 'enable_proxy', fallback=False)
http_proxy = config.get('PROXY', 'http_proxy') if enable_proxy else None
https_proxy = config.get('PROXY', 'https_proxy') if enable_proxy else None

class GiteeAIClient:
    """Gitee AI API客户端"""
    
    def __init__(self, api_key: str):
        """初始化客户端
        
        Args:
            api_key: API密钥
        """
        self.api_key = api_key
        logger.info("初始化Gitee AI客户端")
    
    def analyze_exam_paper(self, image_url: str) -> Dict[str, Any]:
        """分析试卷图像
        
        Args:
            image_url: 图像URL或Base64
            
        Returns:
            分析结果
        """
        logger.info("调用试卷分析API")
        # 这里简化处理，实际应该调用真正的API
        return {
            "sections": [
                {
                    "section_number": "1",
                    "section_title": "选择题",
                    "questions": [
                        {
                            "question_number": "1",
                            "question_text": "此处是检测到的题目文本",
                            "printed_text": "此处是印刷文本",
                            "handwritten_notes": []
                        }
                    ]
                }
            ]
        }
    
    def verify_and_answer_questions(self, questions_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证并回答问题
        
        Args:
            questions_data: 问题数据
            
        Returns:
            答案数据
        """
        logger.info("调用问题验证和回答API")
        # 这里简化处理，实际应该调用真正的API
        result = dict(questions_data)
        
        # 为问题添加模拟答案
        for section in result.get("sections", []):
            for question in section.get("questions", []):
                question["answer"] = "模拟答案"
                question["explanation"] = "模拟解析内容"
        
        return result

class ColorAnalyzer:
    """颜色分析器，用于检测手写区域"""
    
    def __init__(self):
        """初始化颜色分析器"""
        logger.info("初始化颜色分析器")
    
    def detect_handwritten_areas(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """检测图像中的手写区域
        
        Args:
            image: 图像数据
            
        Returns:
            手写区域列表
        """
        logger.info("检测手写区域")
        # 这里简化处理，实际应该进行更复杂的颜色分析
        return [
            {"color": "blue", "bbox": [100, 100, 200, 150]},
            {"color": "red", "bbox": [300, 200, 400, 250]}
        ]

class DocumentSegmenter:
    """文档分割器，用于分割试卷中的不同部分"""
    
    def __init__(self):
        """初始化文档分割器"""
        logger.info("初始化文档分割器")
    
    def segment_document(self, image: np.ndarray) -> Dict[str, Any]:
        """分割文档
        
        Args:
            image: 图像数据
            
        Returns:
            分割结果
        """
        logger.info("分割文档")
        # 这里简化处理，实际应该进行更复杂的文档分割
        return {
            "sections": [
                {"title": "选择题", "bbox": [50, 50, 500, 400]},
                {"title": "填空题", "bbox": [50, 450, 500, 800]}
            ]
        }

class ResultFormatter:
    """结果格式化器，用于格式化和保存结果"""
    
    def __init__(self, output_dir: str = "results"):
        """初始化结果格式化器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"初始化结果格式化器，输出目录: {output_dir}")
    
    def format_for_display(self, result: Dict[str, Any]) -> str:
        """格式化结果用于显示
        
        Args:
            result: 处理结果
            
        Returns:
            格式化的文本
        """
        logger.info("格式化结果用于显示")
        
        display_text = "识别结果汇总:\n\n"
        
        # 添加各部分内容
        for section in result.get("sections", []):
            section_title = section.get("section_title", "未知部分")
            display_text += f"## {section_title}\n\n"
            
            for question in section.get("questions", []):
                q_number = question.get("question_number", "")
                q_text = question.get("question_text", "")
                answer = question.get("answer", "未知")
                
                display_text += f"问题 {q_number}: {q_text}\n"
                display_text += f"答案: {answer}\n\n"
        
        return display_text
    
    def save_json_result(self, result: Dict[str, Any], filename: str) -> str:
        """保存JSON结果
        
        Args:
            result: 处理结果
            filename: 文件名
            
        Returns:
            保存路径
        """
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存至: {filepath}")
        return filepath

class ImageProcessor:
    """处理考试试卷图片，提取文本和问题"""
    
    
    def __init__(self, api_key: str = "CSW0YJEY0AJVXWFSOA6CKRI6H06UAJUYK7IS1LBZ", use_mock: bool = False):
        """
        初始化图像处理器
        
        Args:
            api_key: Gitee AI API密钥
            use_mock: 是否使用模拟数据（用于测试）
        """
        self.api_key = api_key
        self.use_mock = use_mock
        self.api_client = GiteeAIClient(api_key)
        self.color_analyzer = ColorAnalyzer()
        self.document_segmenter = DocumentSegmenter()
        self.result_formatter = ResultFormatter()
        self.db = Database()  # 初始化数据库实例
        logger.info(f"初始化图像处理器，使用模拟数据: {use_mock}")
    
    def preprocess_image(self, image_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        预处理图像以提高OCR和问题识别的质量
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            处理后的图像和原始图像
        """
        # 使用numpy读取图像以支持中文路径
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
            
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 应用自适应阈值处理增强对比度
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 降噪
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised, img
    
    def image_to_base64(self, image_path: str) -> str:
        """
        将图像转换为base64编码
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            base64编码的图像
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def pil_image_to_base64(self, pil_image: Image.Image) -> str:
        """
        将PIL图像转换为base64编码
        
        Args:
            pil_image: PIL图像对象
            
        Returns:
            base64编码的图像
        """
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def _get_mock_extraction_result(self, image_path: str) -> Dict[str, Any]:
        """
        生成模拟的提取结果（用于测试）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            模拟的提取结果
        """
        logger.info(f"使用模拟数据代替API调用: {image_path}")
        return {
            "sections": [
                {
                    "section_number": "1",
                    "section_title": "选择题",
                    "questions": [
                        {
                            "question_number": "1",
                            "question_text": "在三角形ABC中，如果sinA:sinB:sinC=1:2:3，则该三角形的三个内角A、B、C的大小关系是？",
                            "printed_text": "A. A<B<C  B. A>B>C  C. B<A<C  D. C<A<B",
                            "handwritten_notes": [
                                {"text": "选A", "color": "blue"}
                            ]
                        },
                        {
                            "question_number": "2",
                            "question_text": "已知某几何体的三视图如图所示，则该几何体的体积是？",
                            "printed_text": "A. 12  B. 18  C. 24  D. 36",
                            "handwritten_notes": [
                                {"text": "选C", "color": "red"}
                            ]
                        }
                    ]
                },
                {
                    "section_number": "2",
                    "section_title": "填空题",
                    "questions": [
                        {
                            "question_number": "3",
                            "question_text": "已知函数f(x)=2x^3-ax^2+x+1在x=1处取得极值，则a=________。",
                            "printed_text": "",
                            "handwritten_notes": [
                                {"text": "a=6", "color": "blue"}
                            ]
                        }
                    ]
                }
            ]
        }
    
    def _get_mock_answer_result(self, questions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成模拟的答案结果（用于测试）
        
        Args:
            questions_data: 问题数据
            
        Returns:
            模拟的答案结果
        """
        logger.info("使用模拟数据生成答案")
        result = dict(questions_data)
        
        # 为问题添加答案和解析
        for section in result.get("sections", []):
            for question in section.get("questions", []):
                question_number = question.get("question_number", "")
                
                # 根据问题编号添加不同的模拟答案
                if question_number == "1":
                    question["answer"] = "A. A<B<C"
                    question["explanation"] = "在三角形中，正弦值的比例与对应角度成正比。所以sinA:sinB:sinC=1:2:3意味着A<B<C。"
                elif question_number == "2":
                    question["answer"] = "C. 24"
                    question["explanation"] = "根据三视图分析，该几何体的体积为3×4×2=24立方单位。"
                elif question_number == "3":
                    question["answer"] = "a=6"
                    question["explanation"] = "对f(x)=2x^3-ax^2+x+1求导，得f'(x)=6x^2-2ax+1。在x=1处取极值，则f'(1)=0，即6-2a+1=0，解得a=7/2。"
                else:
                    question["answer"] = "模拟答案"
                    question["explanation"] = "这是一个模拟的解析，实际中会根据问题内容生成相应答案。"
        
        return result
    
    def extract_text_from_image(self, image_path: str, subject: str = "数学") -> Dict[str, Any]:
        """
        使用Qwen2.5-VL-32B-Instruct从图像中提取文本和问题
        
        Args:
            image_path: 图像文件路径
            subject: 学科名称，默认为"数学"
            
        Returns:
            包含提取文本和结构的字典
        """
        try:
            # 如果使用模拟数据，直接返回
            if self.use_mock:
                extraction_result = self._get_mock_extraction_result(image_path)
            else:
                # 将图像转换为base64
                base64_image = self.image_to_base64(image_path)
                
                # 构建图像URL
                image_url = f"data:image/jpeg;base64,{base64_image}"
                
                # 调用API客户端分析试卷
                extraction_result = self.api_client.analyze_exam_paper(image_url)
            
            # 预处理图像
            denoised_img, original_img = self.preprocess_image(image_path)
            
            # 检测颜色区域
            handwritten_areas = self.color_analyzer.detect_handwritten_areas(original_img)
            logger.info(f"检测到 {len(handwritten_areas)} 个手写区域")
            
            # 分割文档
            segmentation_result = self.document_segmenter.segment_document(original_img)
            logger.info(f"分割结果: {len(segmentation_result.get('sections', []))} 个大题")
            
            # 增强提取结果
            self._enhance_extraction_result(extraction_result, handwritten_areas, segmentation_result)
            
            return extraction_result
                
        except Exception as e:
            logger.error(f"提取文本时出错: {e}")
            return {"error": str(e)}
    
    def _enhance_extraction_result(self, extraction_result: Dict[str, Any], 
                                 handwritten_areas: List[Dict[str, Any]], 
                                 segmentation_result: Dict[str, Any]) -> None:
        """
        使用图像处理结果增强API提取的结果
        
        Args:
            extraction_result: API提取的结果
            handwritten_areas: 检测到的手写区域
            segmentation_result: 文档分割结果
        """
        # 如果API返回了错误或没有正确结构，则不处理
        if "error" in extraction_result or "sections" not in extraction_result:
            return
            
        # 根据检测到的手写区域增强手写笔记识别
        for section in extraction_result.get("sections", []):
            for question in section.get("questions", []):
                # 如果没有手写笔记字段，添加空列表
                if "handwritten_notes" not in question:
                    question["handwritten_notes"] = []
                    
                # 如果笔记为空但我们检测到了手写区域，可能需要更新
                if len(question["handwritten_notes"]) == 0 and handwritten_areas:
                    # 获取问题编号
                    q_number = question.get("question_number", "")
                    # 我们这里的逻辑简化了，实际上需要更精确地匹配问题和手写区域
                    matching_areas = [area for area in handwritten_areas 
                                     if area["color"] != "black"]  # 假设非黑色是手写笔记
                    
                    # 如果有匹配的区域，添加到手写笔记
                    for area in matching_areas[:2]:  # 简化处理，最多添加2个
                        question["handwritten_notes"].append({
                            "text": f"[图像处理检测到的手写区域]",
                            "color": area["color"]
                        })
    
    def verify_and_answer_questions(self, questions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用QwQ-32B验证问题并生成答案
        
        Args:
            questions_data: 包含问题数据的字典
            
        Returns:
            添加了答案的问题数据
        """
        try:
            # 如果使用模拟数据，直接返回模拟答案
            if self.use_mock:
                return self._get_mock_answer_result(questions_data)
            
            # 调用API客户端验证和回答问题
            return self.api_client.verify_and_answer_questions(questions_data)
                
        except Exception as e:
            logger.error(f"验证和回答问题时出错: {e}")
            return {"error": str(e)}
    
    def process_images(self, image_paths: List[str], subject: str = "数学") -> Dict[str, Any]:
        """
        处理多张试卷图像
        
        Args:
            image_paths: 图像文件路径列表
            subject: 学科名称，默认为"数学"
            
        Returns:
            处理结果
        """
        results = []
        
        for image_path in image_paths:
            logger.info(f"正在处理{subject}科目图像: {image_path}")
            
            try:
                # 1. 从图像中提取文本和问题
                extraction_result = self.extract_text_from_image(image_path, subject)
                
                if "error" in extraction_result:
                    results.append({
                        "image_path": image_path,
                        "error": extraction_result["error"]
                    })
                    continue
                
                # 2. 验证问题并生成答案
                answered_result = self.verify_and_answer_questions(extraction_result)
                
                # 3. 格式化结果用于显示
                display_text = self.result_formatter.format_for_display(answered_result)
                
                # 4. 保存结果
                result_path = self.result_formatter.save_json_result(
                    answered_result, 
                    f"result_{Path(image_path).stem}.json"
                )
                
                # 5. 添加结果
                results.append({
                    "image_path": image_path,
                    "data": answered_result,
                    "display_text": display_text,
                    "result_path": result_path
                })
            except Exception as e:
                logger.error(f"处理图像时出错: {str(e)}")
                results.append({
                    "image_path": image_path,
                    "error": str(e)
                })
        
        summary = f"成功处理了 {len([r for r in results if 'error' not in r])} 个文件"
        return {"results": results, "summary": summary}

    def process_images_gemini25_pro(self, image_paths: List[str], subject: str = "数学") -> Dict[str, Any]:
        """
        使用 Gemini-2.5-Pro 处理试卷图像
        
        Args:
            image_paths: 图像文件路径列表
            subject: 学科名称，默认为"数学"
            
        Returns:
            处理结果
        """
        results = []

        for image_path in image_paths:
            logger.info(f"正在处理{subject}科目图像: {image_path}")
        
        try:
            # 将图片转换为base64
            base64_image = self.image_to_base64(image_path)
            mime_type = get_mime_type(image_path)
            image_url = f"data:{mime_type};base64,{base64_image}"
            #logger.info(f"image_url: {image_url}")
            #image_url = "https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/Obsidian/%E5%8E%9F%E5%A7%8B%E8%AF%95%E5%8D%B71.png"
            proxies = {
                'http': http_proxy,
                'https': https_proxy
            } if enable_proxy else None
            # 设置是否使用流式输出
            use_stream = False
           # 发送请求
            response = requests.post(
                #url="https://openrouter.ai/api/v1/chat/completions",
                url = a302_api_url,
                headers={
                    "Authorization": f"Bearer {a302_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    #"model": "google/gemini-2.5-pro-exp-03-25:free",
                    #"model": "google/gemini-2.0-flash-exp:free",
                    "model": a302_model,
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
                full_content=process_stream_response(response)
            else:
                full_content=process_normal_response(response)
                # 尝试从响应内容中提取 JSON 部分
            try:
                result_json = json.loads(full_content)
                logger.info(f"result_json: {result_json}")
                
                # 保存json文件
                result_path = self.result_formatter.save_json_result(
                    result_json,
                    f"result_{Path(image_path).stem}.json"
                )
                
                # 插入数据库
                self.db.batch_add_error_questions(result_json)
                
                # 添加结果
                results.append({
                    "image_path": image_path,
                    "data": result_json,
                    "result_path": result_path,
                    "raw_response": full_content  # 保存原始响应以供调试
                 })
                    
            except json.JSONDecodeError as e:
                logger.error(f"无法解析Gemini响应为JSON格式: {str(e)}\n响应内容: {full_content[:200]}...")
                results.append({
                "image_path": image_path,
                "error": "无法解析响应为JSON格式",
                "raw_response": full_content  # 保存原始响应以供调试
                })
                
        except Exception as e:
            logger.error(f"处理图像时出错: {str(e)}")
            results.append({
                "image_path": image_path,
                "error": str(e)
            })
    
        # 检查results是否为空列表
        if not results:
            summary = "没有处理任何文件"
        else:
            summary = f"成功处理了 {len([r for r in results if 'error' not in r])} 个文件"
        return {"results": results, "summary": summary}


def process_stream_response(response):
    """处理流式响应
    
    Args:
        response: API响应对象
        
    Returns:
        str: 完整的响应内容
    """
    full_content = ""
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                json_str = line.decode('utf-8').replace('data: ', '')
                try:
                    chunk = json.loads(json_str)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        content = chunk['choices'][0].get('delta', {}).get('content', '')
                        if content:
                            logger.info(content)
                            full_content += content
                except json.JSONDecodeError:
                    continue
        
        # 处理完整的响应内容，提取JSON部分
        try:
            start_idx = full_content.find('{')
            end_idx = full_content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_content = full_content[start_idx:end_idx + 1]
                # 尝试解析JSON
                parsed_json = json.loads(json_content)
                return json.dumps(parsed_json, ensure_ascii=False, indent=2)
            else:
                return full_content
        except json.JSONDecodeError:
            logger.warning(f"JSON解析失败，返回原始内容")
            return full_content
    else:
        error_msg = f"请求失败: {response.status_code}"
        logger.error(error_msg)
        logger.error(response.text)
        return error_msg

def process_normal_response(response):
    """处理非流式响应
    
    Args:
        response: API响应对象
        
    Returns:
        str: 响应内容
    """
    if response.status_code == 200:
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            content = response_json['choices'][0].get('message', {}).get('content', '')
            # 提取JSON内容
            try:
                # 查找JSON内容的开始和结束位置
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_content = content[start_idx:end_idx + 1]
                    # 尝试解析JSON
                    parsed_json = json.loads(json_content)
                    return json.dumps(parsed_json, ensure_ascii=False, indent=2)
                else:
                    return content
            except json.JSONDecodeError:
                logger.warning(f"JSON解析失败，返回原始内容")
                return content
    else:
        error_msg = f"请求失败: {response.status_code}"
        logger.error(error_msg)
        logger.error(response.text)
        return error_msg

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