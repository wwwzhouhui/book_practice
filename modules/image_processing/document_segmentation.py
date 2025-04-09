import cv2
import numpy as np
from typing import List, Dict, Tuple, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentSegmenter:
    """分割文档，检测和提取大题和小题"""
    
    def __init__(self):
        """初始化文档分割器"""
        pass
    
    def detect_lines(self, image: np.ndarray) -> np.ndarray:
        """
        检测图像中的水平线，这些线通常分隔不同的题目
        
        Args:
            image: OpenCV格式的图像
            
        Returns:
            包含线条位置的数组
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
            # 应用高斯模糊减少噪点
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 使用Canny边缘检测
            edges = cv2.Canny(blur, 50, 150, apertureSize=3)
            
            # 使用霍夫变换检测直线
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=300, maxLineGap=10)
            
            # 过滤水平线
            horizontal_lines = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # 如果线条几乎是水平的
                    if abs(y2 - y1) < 10:
                        horizontal_lines.append(line[0])
            
            return np.array(horizontal_lines)
        except Exception as e:
            logger.error(f"检测线条出错: {e}")
            return np.array([])
    
    def detect_section_headers(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        尝试检测大题的标题或编号（如'一、'，'第一部分'等）
        
        Args:
            image: OpenCV格式的图像
            
        Returns:
            包含大题标题位置和文本信息的列表
        """
        try:
            # 此功能实际上需要OCR支持，这里只做位置检测
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 定义一个模式匹配的核，适合检测类似"一、"这样的标题
            # 这里简化为检测短而宽的文本块
            kernel = np.ones((5, 20), np.uint8)
            
            # 执行形态学操作
            dilated = cv2.dilate(binary, kernel, iterations=1)
            eroded = cv2.erode(dilated, kernel, iterations=1)
            
            # 查找轮廓
            contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 筛选合适的轮廓
            section_headers = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # 筛选短而宽的矩形，可能是大题标题
                if 10 < w < 100 and 10 < h < 50:
                    section_headers.append({
                        "bbox": (x, y, w, h),
                        "text": None  # 需要OCR填充
                    })
            
            return section_headers
        except Exception as e:
            logger.error(f"检测大题标题出错: {e}")
            return []
    
    def detect_question_numbers(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        检测小题的编号（如'1.'，'2.'等）
        
        Args:
            image: OpenCV格式的图像
            
        Returns:
            包含小题编号位置和文本信息的列表
        """
        try:
            # 此功能实际上需要OCR支持，这里只做位置检测
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 筛选合适的轮廓
            question_numbers = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # 筛选小而方的矩形，可能是小题编号
                if 5 < w < 30 and 5 < h < 30:
                    area = cv2.contourArea(contour)
                    if area > 50:  # 过滤掉太小的噪点
                        question_numbers.append({
                            "bbox": (x, y, w, h),
                            "text": None  # 需要OCR填充
                        })
            
            return question_numbers
        except Exception as e:
            logger.error(f"检测小题编号出错: {e}")
            return []
    
    def segment_document(self, image: np.ndarray) -> Dict[str, Any]:
        """
        分割文档为大题和小题
        
        Args:
            image: OpenCV格式的图像
            
        Returns:
            包含分割结果的字典
        """
        try:
            # 检测水平线
            horizontal_lines = self.detect_lines(image)
            
            # 检测大题标题
            section_headers = self.detect_section_headers(image)
            
            # 检测小题编号
            question_numbers = self.detect_question_numbers(image)
            
            # 如果没有检测到大题标题，创建一个默认的
            if not section_headers:
                logger.warning("未检测到大题标题，使用默认值")
                section_headers = [{
                    "bbox": (10, 10, 50, 30),
                    "text": None
                }]
            
            # 根据位置关系组织大题和小题
            sections = []
            
            # 对section_headers按y坐标排序
            section_headers.sort(key=lambda x: x["bbox"][1])
            
            for i, header in enumerate(section_headers):
                # 获取当前大题的y范围
                _, y_start, _, h = header["bbox"]
                
                # 计算下一个大题的y起点，如果是最后一个大题则使用图像底部
                if i < len(section_headers) - 1:
                    y_end = section_headers[i+1]["bbox"][1]
                else:
                    y_end = image.shape[0]
                
                # 筛选该范围内的小题编号
                section_questions = []
                for number in question_numbers:
                    q_y = number["bbox"][1]
                    if y_start < q_y < y_end:
                        section_questions.append(number)
                
                # 按x坐标排序
                section_questions.sort(key=lambda x: x["bbox"][0])
                
                # 添加到大题列表
                sections.append({
                    "header": header,
                    "questions": section_questions,
                    "y_range": (y_start, y_end)
                })
            
            return {
                "sections": sections,
                "horizontal_lines": horizontal_lines.tolist() if len(horizontal_lines) > 0 else []
            }
        except Exception as e:
            logger.error(f"分割文档出错: {e}")
            return {"sections": [], "horizontal_lines": []}
    
    def extract_question_regions(self, image: np.ndarray, sections: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        提取每个问题的图像区域
        
        Args:
            image: OpenCV格式的图像
            sections: 分割结果中的sections字段
            
        Returns:
            问题ID到图像区域的映射
        """
        try:
            question_regions = {}
            
            for section_idx, section in enumerate(sections):
                y_start, y_end = section["y_range"]
                
                # 提取整个大题区域
                section_image = image[y_start:y_end, :]
                question_regions[f"section_{section_idx+1}"] = section_image
                
                # 如果大题中有小题
                for question_idx, question in enumerate(section.get("questions", [])):
                    x, y, w, h = question["bbox"]
                    
                    # 计算小题的区域
                    # 如果是最后一题，区域延伸到大题的底部
                    if question_idx < len(section["questions"]) - 1:
                        next_q_y = section["questions"][question_idx+1]["bbox"][1]
                        q_region = image[y:next_q_y, :]
                    else:
                        q_region = image[y:y_end, :]
                    
                    question_regions[f"section_{section_idx+1}_question_{question_idx+1}"] = q_region
            
            return question_regions
        except Exception as e:
            logger.error(f"提取问题区域出错: {e}")
            return {} 