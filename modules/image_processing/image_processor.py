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

from .api_client import GiteeAIClient
from .color_analysis import ColorAnalyzer
from .document_segmentation import DocumentSegmenter
from .result_formatter import ResultFormatter

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        
    def preprocess_image(self, image_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        预处理图像以提高OCR和问题识别的质量
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            处理后的图像和原始图像
        """
        # 读取图像
        img = cv2.imread(image_path)
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
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        使用Qwen2.5-VL-32B-Instruct从图像中提取文本和问题
        
        Args:
            image_path: 图像文件路径
            
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
    
    def process_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        处理多张试卷图像
        
        Args:
            image_paths: 图像文件路径列表
            
        Returns:
            处理结果
        """
        results = []
        
        for image_path in image_paths:
            logger.info(f"正在处理图像: {image_path}")
            
            # 1. 从图像中提取文本和问题
            extraction_result = self.extract_text_from_image(image_path)
            
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
        
        return {"results": results} 