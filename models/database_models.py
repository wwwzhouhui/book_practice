from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class ErrorQuestion(Base):
    """错题模型"""
    __tablename__ = 'error_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False, comment="题目内容")
    subject = Column(String(50), nullable=False, comment="学科")
    question_type = Column(String(50), nullable=False, comment="题目类型")
    difficulty = Column(Integer, nullable=False, comment="难度等级(1-5)")
    answer = Column(Text, nullable=True, comment="答案")
    user_answer = Column(Text, nullable=True, comment="用户答案")
    explanation = Column(Text, nullable=True, comment="解析")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "subject": self.subject,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "answer": self.answer,
            "user_answer": self.user_answer,
            "explanation": self.explanation,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class SimilarQuestion(Base):
    """同类题模型"""
    __tablename__ = 'similar_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False, comment="题目内容")
    subject = Column(String(50), nullable=False, comment="学科")
    question_type = Column(String(50), nullable=False, comment="题目类型")
    difficulty = Column(Integer, nullable=False, comment="难度等级(1-5)")
    answer = Column(Text, comment="答案")
    explanation = Column(Text, comment="解析")
    source_question_id = Column(Integer, ForeignKey('error_questions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "question_text": self.question_text,
            "subject": self.subject,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "answer": self.answer,
            "explanation": self.explanation,
            "source_question_id": self.source_question_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }