import logging
from typing import List, Dict, Any
from modules.storage.database import Database
from openai import OpenAI
import configparser
import json

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 从配置文件中获取API密钥
base_url = config.get('gitee', 'base_url')
api_key = config.get('gitee', 'api_key')
model = config.get('gitee', 'model')
max_tokens = int(config.get('gitee', 'max_tokens'))
temperature = float(config.get('gitee', 'temperature'))
top_p = float(config.get('gitee', 'top_p'))
top_k = int(config.get('gitee', 'top_k'))
logger = logging.getLogger(__name__)

class QuestionGenerator:
    """同类题目生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.db = Database()
        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
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
                prompt = self._build_generation_prompt(source, count)
                
                # 调用AI生成
                generated_list = self._call_ai_model(source, prompt)
                if generated_list:
                    # 遍历生成的题目列表
                    for generated in generated_list:
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
    
    def _build_generation_prompt(self, question: Dict[str, Any],count:int) -> str:
        """构建生成提示词
        
        Args:
            question: 原始题目
            
        Returns:
            提示词文本
        """
        return f"""# Role: 错题同类型生成专家

## Profile

- Author: Assistant
- Version: 1.1
- Language: 中文
- Description: 我是一位专门生成同类型错题的AI助手。我能根据给定的原始题目生成多个相似的新题目，涵盖多种题型和学科。

## Background

在教育领域，练习相似题目对于巩固知识点和提高解题能力至关重要。本专家旨在帮助教育工作者和学生快速生成与原题相似的多个新题目，以便进行更有效的学习和复习。

## Skills

- 深入理解各学科知识点和题型特征
- 能够准确分析原始题目的结构、难度和考察重点
- 具备创造性思维，能够灵活变换题目场景和数值
- 熟练掌握多种题型的出题技巧
- 能够提供清晰、详细的答案和解析
- 能够批量生成多个相似题目

## Goals

- 根据用户提供的原始题目生成{count}相似的新题目
- 保持与原题相同的题型和难度级别
- 确保新生成的题目在数值、场景或具体内容上有所变化
- 为每个新题目提供准确的答案和详细的解析

## Constraints

- 严格遵守教育伦理，不生成具有争议或不适当的内容
- 确保生成的题目难度适中，符合原题的难度水平
- 不得直接复制原题，必须进行创造性的改编
- 生成的题目必须有明确的答案和合理的解析
- 生成的多个题目之间应有足够的差异性

## Skills

- 中小学各学科知识储备
- 题目分析与结构化能力
- 创意思维和灵活应用能力
- 清晰的文字表达能力
- 批量生成相似题目的能力

## Workflows

1. 接收并分析用户输入的原始题目
2. 识别题目的类型、学科和难度级别
3. 提取题目的核心知识点和考察重点
4. 确定要生成的新题目数量{count}
5. 对每个新题目：
   a. 创造性地设计新的题目场景或更换数值
   b. 生成新的题目，确保与原题类型和难度相当
   c. 编写详细的答案和解析
6. 检查所有生成的题目，确保它们之间有足够的差异性
7. 将生成的多个题目整理为指定的JSON格式
8. 输出最终结果

## Output Format
生成一份JSON格式的题目，结构如下：
{{
  "original_question": "{question['question_text']}",
  "generated_questions": [
    {{
      "question_text": "新生成的题目文本1",
      "question_type": "{question['question_type']}",
      "subject": "{question['subject']}",
      "difficulty_level": "{question['difficulty']}",
      "answer": "正确答案",
      "explanation": "详细的解答过程和解析"
    }}
  ]
}}
"""
    
    def _call_ai_model(self, question: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """调用AI模型生成题目
        
        Args:
            question: 原始题目数据
            prompt: 提示词
            
        Returns:
            生成的题目数据列表
        """
        try:
            # 调用模型
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": question['question_text']
                    }
                ],
                stream=True,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=0
            )

            # 收集完整响应
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content

            # 清理JSON标记
            clean_response = full_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            try:
                # 解析JSON响应
                response_data = json.loads(clean_response)
                
                # 返回生成的题目列表
                if response_data and "generated_questions" in response_data:
                    return response_data["generated_questions"]
                return None
            
            except json.JSONDecodeError as je:
                logger.error(f"JSON解析失败: {str(je)}, 原始响应: {clean_response}")
                return None
            
            logger.warning("AI模型未返回有效题目")
            return None
            
        except Exception as e:
            logger.error(f"AI模型调用失败: {str(e)}")
            return None





