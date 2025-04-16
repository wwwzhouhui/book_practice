import logging
from typing import List, Dict, Any
from modules.storage.database import Database

logger = logging.getLogger(__name__)

class QuestionGenerator:
    """同类题目生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.db = Database()
        logger.info("初始化题目生成器")
    
    def generate_similar_questions(
        self,
        source_questions: List[Dict[str, Any]],
        count: int = 1
    ) -> List[Dict[str, Any]]:
        """生成同类型题目
        
        Args:
            source_questions: 原始错题列表
            count: 每道题生成的数量
            
        Returns:
            生成的题目列表
        """
        try:
            generated_questions = []
            
            for source in source_questions:
                # 构建提示词
                prompt = self._build_generation_prompt(source)
                
                # 调用AI生成
                for _ in range(count):
                    generated = self._call_ai_model(prompt)
                    if generated:
                        # 添加关联信息
                        generated["source_question_id"] = source["id"]
                        generated["subject"] = source["subject"]
                        generated["question_type"] = source["question_type"]
                        generated["difficulty"] = source["difficulty"]
                        generated_questions.append(generated)
            
            return generated_questions
            
        except Exception as e:
            logger.error(f"生成同类题失败: {str(e)}")
            return []
    
    def _build_generation_prompt(self, question: Dict[str, Any]) -> str:
        """构建生成提示词
        
        Args:
            question: 原始题目
            
        Returns:
            提示词文本
        """
        return f"""
        请根据以下题目生成一道同类型的新题目：
        
        原始题目：{question['question_text']}
        题目类型：{question['question_type']}
        难度等级：{question['difficulty']}
        
        要求：
        1. 保持相同的题型和难度
        2. 更换具体数值和场景
        3. 提供详细的答案和解析
        4. 返回JSON格式，包含question_text、answer、explanation字段
        """
    
    def _call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """调用AI模型生成题目
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的题目数据
        """
        try:
            # TODO: 实现实际的AI模型调用
            # 这里使用模拟数据
            import random
            
            templates = [
                {
                    "question_text": "在△ABC中，已知角A=30°，角B=60°，边AB=4，求边BC的长度。",
                    "answer": "BC = 4√3",
                    "explanation": "1. 根据三角形内角和为180°，角C=90°\n2. 根据正弦定理，BC = AB×sin(A)/sin(C)"
                },
                {
                    "question_text": "计算：∫(x²+1)dx",
                    "answer": "(x³/3)+x+C",
                    "explanation": "1. 使用幂函数求导公式的逆运算\n2. 常数项积分为x\n3. 添加积分常数C"
                }
            ]
            
            return random.choice(templates)
            
        except Exception as e:
            logger.error(f"AI模型调用失败: {str(e)}")
            return None