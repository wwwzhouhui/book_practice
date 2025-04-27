import csv
import logging
import os
from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)

class CSVExporter(BaseExporter):
    """CSV导出器"""
    
    def export_questions(self, questions, output_path=None, include_answers=False):
        """
        导出题目到CSV文件
        
        Args:
            questions: 题目数据列表
            output_path: 输出文件路径，如果为None则使用默认路径
            include_answers: 是否包含答案
            
        Returns:
            输出文件路径
        """
        try:
            # 如果未指定输出路径，使用默认路径
            if output_path is None:
                file_suffix = "题目和答案" if include_answers else "题目"
                output_path = self.get_default_filename(f"错题_{file_suffix}", "csv")
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                if include_answers:
                    # 导出题目和答案
                    fieldnames = ["id", "subject", "question_type", "difficulty", 
                                 "question_text", "correct_answer", "explanation"]
                else:
                    # 只导出题目
                    fieldnames = ["id", "subject", "question_type", "difficulty", "question_text"]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for question in questions:
                    # 筛选需要的字段
                    row = {field: question.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            return output_path
            
        except Exception as e:
            logger.error(f"导出CSV失败: {str(e)}")
            raise