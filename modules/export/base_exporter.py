import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseExporter(ABC):
    """导出器基类，定义导出接口"""
    
    def __init__(self):
        """初始化导出器"""
        # 确保导出目录存在
        self.export_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(self.export_dir, exist_ok=True)
    
    @abstractmethod
    def export_questions(self, questions, output_path, include_answers=False):
        """
        导出题目到指定格式
        
        Args:
            questions: 题目数据列表
            output_path: 输出文件路径
            include_answers: 是否包含答案
            
        Returns:
            输出文件路径
        """
        pass
    
    def get_default_filename(self, prefix, extension):
        """
        获取默认文件名
        
        Args:
            prefix: 文件名前缀
            extension: 文件扩展名
            
        Returns:
            完整的文件路径
        """
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        return os.path.join(self.export_dir, filename)