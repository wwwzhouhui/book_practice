import json
from typing import Dict, Any, List, Optional
import logging
import os
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResultFormatter:
    """格式化OCR和分析结果"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化结果格式化器
        
        Args:
            output_dir: 输出目录
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # 默认在项目根目录创建results文件夹
            self.output_dir = Path.cwd() / "results"
            
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_json_result(self, result: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        将结果保存为JSON文件
        
        Args:
            result: 要保存的结果字典
            filename: 文件名，可选
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            # 使用时间戳创建唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_{timestamp}.json"
        
        # 如果没有.json后缀，添加它
        if not filename.endswith(".json"):
            filename += ".json"
            
        # 完整文件路径
        file_path = self.output_dir / filename
        
        # 保存JSON
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        logger.info(f"结果已保存到: {file_path}")
        return str(file_path)
    
    def format_section_summary(self, sections: List[Dict[str, Any]]) -> str:
        """
        创建大题和小题的摘要文本
        
        Args:
            sections: 包含大题信息的列表
            
        Returns:
            摘要文本
        """
        summary = []
        
        for i, section in enumerate(sections):
            section_title = section.get("section_title", f"第{i+1}部分")
            section_number = section.get("section_number", str(i+1))
            
            questions = section.get("questions", [])
            question_count = len(questions)
            
            summary.append(f"{section_number}. {section_title} (包含{question_count}个小题)")
            
        return "\n".join(summary)
    
    def format_question_with_answer(self, question: Dict[str, Any]) -> str:
        """
        格式化单个问题及其答案
        
        Args:
            question: 包含问题信息的字典
            
        Returns:
            格式化的问题文本
        """
        question_number = question.get("question_number", "")
        question_text = question.get("question_text", "")
        answer = question.get("answer", "")
        explanation = question.get("explanation", "")
        
        # 格式化手写笔记
        handwritten_notes = []
        for note in question.get("handwritten_notes", []):
            note_text = note.get("text", "")
            note_color = note.get("color", "")
            if note_text:
                handwritten_notes.append(f"[{note_color}] {note_text}")
        
        notes_text = "\n".join(handwritten_notes) if handwritten_notes else ""
        
        # 组合结果
        result = []
        result.append(f"问题 {question_number}: {question_text}")
        
        if notes_text:
            result.append(f"\n手写笔记:\n{notes_text}")
            
        if answer:
            result.append(f"\n答案: {answer}")
            
        if explanation:
            result.append(f"\n解析: {explanation}")
            
        return "\n".join(result)
    
    def generate_summary_report(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成结果摘要报告
        
        Args:
            result: 处理结果
            
        Returns:
            摘要报告
        """
        summary = {}
        
        # 获取sections
        sections = result.get("sections", [])
        
        # 大题数量
        summary["section_count"] = len(sections)
        
        # 小题总数
        question_count = 0
        for section in sections:
            question_count += len(section.get("questions", []))
        summary["question_count"] = question_count
        
        # 大题摘要
        summary["section_summary"] = self.format_section_summary(sections)
        
        # 错题统计
        wrong_questions = []
        for section in sections:
            for question in section.get("questions", []):
                # 检查是否有手写笔记，有的话可能是错题
                if question.get("handwritten_notes"):
                    wrong_questions.append({
                        "section_number": section.get("section_number", ""),
                        "question_number": question.get("question_number", ""),
                        "question_text": question.get("question_text", "")
                    })
        
        summary["wrong_question_count"] = len(wrong_questions)
        summary["wrong_questions"] = wrong_questions
        
        return summary
    
    def format_for_display(self, result: Dict[str, Any]) -> str:
        """
        将结果格式化为显示文本
        
        Args:
            result: 处理结果
            
        Returns:
            格式化的显示文本
        """
        if "error" in result:
            return f"错误: {result['error']}"
            
        sections = result.get("sections", [])
        if not sections:
            return "未检测到任何题目"
            
        # 生成摘要报告
        summary = self.generate_summary_report(result)
        
        # 创建显示文本
        display_text = []
        display_text.append(f"共检测到 {summary['section_count']} 个大题，{summary['question_count']} 个小题")
        display_text.append(f"疑似错题数量: {summary['wrong_question_count']}")
        display_text.append("\n大题概览:")
        display_text.append(summary["section_summary"])
        
        return "\n".join(display_text) 