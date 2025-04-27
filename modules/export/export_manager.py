from modules.export.pdf_exporter import PDFExporter
from modules.export.csv_exporter import CSVExporter
from modules.export.word_exporter import WordExporter
# 移除对image_exporter的引用
import os
import time
import logging

logger = logging.getLogger(__name__)

class ExportManager:
    """导出管理器，统一管理各种格式的导出"""
    
    def __init__(self, db=None):
        """
        初始化导出管理器
        
        Args:
            db: 数据库实例，用于获取题目数据
        """
        self.db = db
        self.exporters = {
            "PDF": PDFExporter(),
            "CSV": CSVExporter(),
            "Word": WordExporter()
            # 移除"图片(A4)"格式
        }
        
        # 确保导出目录存在
        self.export_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(self.export_dir, exist_ok=True)
        
    def export_questions(self, questions, export_format, include_answers=False):
        """
        导出题目
        
        Args:
            questions: 题目数据列表
            export_format: 导出格式，可选 "PDF", "CSV", "Word"
            include_answers: 是否包含答案
            
        Returns:
            (output_path, status_message): 输出文件路径和状态消息
        """
        try:
            if not questions:
                return None, "没有可导出的题目"
            
            # 创建时间戳
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # 根据内容类型设置文件名
            file_prefix = "错题集"
            if include_answers:
                file_prefix += "_含答案"
            
            # 根据格式选择扩展名
            if export_format == "PDF":
                ext = "pdf"
            elif export_format == "CSV":
                ext = "csv"
            elif export_format == "Word":
                ext = "docx"
            else:
                return None, f"不支持的导出格式: {export_format}"
            
            # 构建输出路径
            output_path = os.path.join(self.export_dir, f"{file_prefix}_{timestamp}.{ext}")
            
            # 获取对应的导出器
            if export_format not in self.exporters:
                return None, f"不支持的导出格式: {export_format}"
            
            exporter = self.exporters[export_format]
            
            # 执行导出
            output_path = exporter.export_questions(questions, output_path, include_answers)
            
            # 返回结果
            status_message = f"✅ 成功导出 {len(questions)} 道题目到 {export_format} 文件"
            return output_path, status_message
            
        except ImportError as e:
            logger.error(f"导出失败，缺少依赖: {str(e)}")
            return None, f"导出失败，缺少依赖: {str(e)}"
        except Exception as e:
            logger.error(f"导出失败: {str(e)}")
            return None, f"导出失败: {str(e)}"