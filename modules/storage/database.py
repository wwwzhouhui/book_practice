from sqlalchemy import create_engine, desc, func, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
import os
import datetime
import logging
from typing import List, Dict, Tuple, Any, Optional
from models.database_models import Base, ErrorQuestion

# 配置日志
logger = logging.getLogger(__name__)

class Database:
    """数据库操作类"""
    
    def __init__(self, db_path=None):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为项目根目录下的data/homework.db
        """
        if db_path is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            # 确保data目录存在
            os.makedirs(data_dir, exist_ok=True)
            db_path = data_dir / "homework.db"
        
        # 创建数据库引擎
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        # 创建会话工厂
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        
        # 创建表
        Base.metadata.create_all(self.engine)
        
        logger.info(f"数据库初始化完成: {db_path}")
        
        # 检查错题数量，如果为空则自动生成示例数据
        self.initialize_sample_data_if_empty()
    
    def initialize_sample_data_if_empty(self, min_count=5):
        """如果数据库为空，则初始化示例数据
        
        Args:
            min_count: 至少需要的错题数量
        """
        try:
            count = self.get_error_count()
            if count < min_count:
                logger.info(f"数据库错题数量不足({count}<{min_count})，自动生成示例数据")
                self.generate_sample_data(count=20)  # 生成20条示例错题
                logger.info("示例数据生成完成")
        except Exception as e:
            logger.error(f"初始化示例数据失败: {str(e)}")
    
    def get_error_count(self):
        """获取错题总数"""
        session = self.Session()
        try:
            count = session.query(ErrorQuestion).count()
            return count
        except Exception as e:
            logger.error(f"获取错题数量失败: {str(e)}")
            return 0
        finally:
            session.close()
    
    def add_error_question(self, question_data):
        """添加错题
        
        Args:
            question_data: 错题数据字典
            
        Returns:
            添加的错题ID
        """
        session = self.Session()
        try:
            error_question = ErrorQuestion(**question_data)
            session.add(error_question)
            session.commit()
            logger.info(f"添加错题成功: ID={error_question.id}")
            return error_question.id
        except Exception as e:
            session.rollback()
            logger.error(f"添加错题失败: {str(e)}")
            raise e
        finally:
            session.close()
    
    def get_error_question(self, question_id):
        """获取指定ID的错题
        
        Args:
            question_id: 错题ID
            
        Returns:
            错题字典，不存在则返回None
        """
        if question_id is None:
            logger.warning("获取错题时ID为None")
            return None
            
        session = self.Session()
        try:
            # 尝试转换ID为整数（如果是字符串）
            if isinstance(question_id, str):
                try:
                    question_id = int(question_id)
                except ValueError:
                    logger.error(f"无效的错题ID格式: {question_id}")
                    return None
                    
            logger.info(f"尝试获取错题: ID={question_id}")
            question = session.query(ErrorQuestion).filter_by(id=question_id).first()
            if question:
                logger.debug(f"成功获取错题: ID={question_id}")
                return question.to_dict()
            else:
                logger.warning(f"错题不存在: ID={question_id}")
                return None
        except Exception as e:
            logger.error(f"获取错题失败: ID={question_id}, 错误={str(e)}")
            return None
        finally:
            session.close()
    
    def get_all_error_questions(self, subject=None, question_type=None, limit=100, time_range=None):
        """获取错题列表
        
        Args:
            subject: 学科筛选（可以是列表）
            question_type: 题型筛选
            limit: 返回数量限制
            time_range: 时间范围，例如 "今天", "最近一周", "最近一月", "全部"
            
        Returns:
            错题字典列表
        """
        session = self.Session()
        try:
            query = session.query(ErrorQuestion)
            
            # 处理学科筛选
            if subject:
                if isinstance(subject, list) and subject:  # 如果是非空列表
                    query = query.filter(ErrorQuestion.subject.in_(subject))
                    logger.debug(f"按学科列表筛选: {subject}")
                elif isinstance(subject, str):  # 如果是单个字符串
                    query = query.filter_by(subject=subject)
                    logger.debug(f"按单个学科筛选: {subject}")
            
            # 处理题型筛选
            if question_type:
                query = query.filter_by(question_type=question_type)
                logger.debug(f"按题型筛选: {question_type}")
            
            # 处理时间范围筛选
            if time_range:
                today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                if time_range == "今天":
                    query = query.filter(ErrorQuestion.created_at >= today)
                    logger.debug("按今天筛选")
                elif time_range == "最近一周":
                    week_ago = today - datetime.timedelta(days=7)
                    query = query.filter(ErrorQuestion.created_at >= week_ago)
                    logger.debug("按最近一周筛选")
                elif time_range == "最近一月":
                    month_ago = today - datetime.timedelta(days=30)
                    query = query.filter(ErrorQuestion.created_at >= month_ago)
                    logger.debug("按最近一月筛选")
                # "全部" 不需要额外筛选
            
            # 按创建时间倒序
            query = query.order_by(desc(ErrorQuestion.created_at)).limit(limit)
            
            result = [q.to_dict() for q in query.all()]
            logger.info(f"查询到 {len(result)} 条错题")
            return result
        except Exception as e:
            logger.error(f"查询错题列表失败: {str(e)}")
            return []
        finally:
            session.close()
    
    def update_error_question(self, question_id, update_data):
        """更新错题
        
        Args:
            question_id: 错题ID
            update_data: 更新数据字典
            
        Returns:
            是否更新成功
        """
        if question_id is None:
            logger.warning("更新错题时ID为None")
            return False
            
        session = self.Session()
        try:
            # 尝试转换ID为整数（如果是字符串）
            if isinstance(question_id, str):
                try:
                    question_id = int(question_id)
                except ValueError:
                    logger.error(f"无效的错题ID格式: {question_id}")
                    return False
            
            # 先检查错题是否存在
            question = session.query(ErrorQuestion).filter_by(id=question_id).first()
            if not question:
                logger.warning(f"要更新的错题不存在: ID={question_id}")
                return False
                
            # 执行更新
            result = session.query(ErrorQuestion).filter_by(id=question_id).update(update_data)
            session.commit()
            
            if result > 0:
                logger.info(f"更新错题成功: ID={question_id}")
            else:
                logger.warning(f"更新错题失败: ID={question_id} 不存在")
            return result > 0
        except Exception as e:
            session.rollback()
            logger.error(f"更新错题异常: ID={question_id}, 错误={str(e)}")
            raise e
        finally:
            session.close()
    
    def delete_error_question(self, question_id):
        """删除错题
        
        Args:
            question_id: 错题ID
        
        Returns:
            是否删除成功
        """
        if question_id is None:
            logger.warning("删除错题时ID为None")
            return False
        
        session = self.Session()
        try:
            # 确保ID是整数
            if isinstance(question_id, str):
                try:
                    question_id = int(question_id)
                except ValueError:
                    logger.error(f"无效的错题ID格式: {question_id}")
                    return False
            
            # 执行删除
            result = session.query(ErrorQuestion).filter_by(id=question_id).delete()
            session.commit()
            
            if result > 0:
                logger.info(f"删除错题成功: ID={question_id}")
                return True
            else:
                logger.warning(f"删除错题失败: ID={question_id} 不存在")
                return False
            
        except Exception as e:
            session.rollback()
            logger.error(f"删除错题异常: ID={question_id}, 错误={str(e)}")
            return False
        finally:
            session.close()
            
    def generate_sample_data(self, count=10):
        """生成测试数据
        
        Args:
            count: 生成数量
            
        Returns:
            生成的错题ID列表
        """
        import random
        
        subjects = ["数学", "物理", "化学"]
        question_types = ["选择题", "填空题", "计算题", "解答题"]
        
        session = self.Session()
        question_ids = []
        
        try:
            logger.info(f"开始生成示例数据: count={count}")
            
            # 确保每个科目和难度都有数据
            for subject in subjects:
                for difficulty in range(1, 6):
                    # 每个科目和难度组合生成至少一个题目
                    question_type = random.choice(question_types)
                    
                    # 根据学科和题型生成不同的题目
                    if subject == "数学":
                        if question_type == "计算题":
                            a, b = random.randint(10, 100), random.randint(10, 100)
                            question_text = f"计算: {a} + {b} = ?"
                            answer = str(a + b)
                            explanation = f"将{a}与{b}相加得到{a+b}"
                        elif question_type == "解答题":
                            question_text = "证明：三角形内角和等于180度。"
                            answer = "证明过程略"
                            explanation = "可以通过内错角相等和同位角相等证明"
                        else:
                            question_text = f"数学{question_type}示例问题 (难度{difficulty})"
                            answer = f"答案示例"
                            explanation = f"解析说明示例"
                    elif subject == "物理":
                        if question_type == "选择题":
                            question_text = "以下哪种现象属于电磁感应？\nA. 电流产生磁场\nB. 导体切割磁感线产生电流\nC. 静电感应\nD. 电容充电"
                            answer = "B"
                            explanation = "导体切割磁感线产生电流是电磁感应的典型现象"
                        else:
                            question_text = f"物理{question_type}示例问题 (难度{difficulty})"
                            answer = f"答案示例"
                            explanation = f"解析说明示例"
                    else:
                        question_text = f"{subject}{question_type}示例问题 (难度{difficulty})"
                        answer = f"答案示例"
                        explanation = f"详细解析示例"
                    
                    # 创建用户错误答案
                    if question_type == "选择题":
                        options = ["A", "B", "C", "D"]
                        if answer in options:
                            options.remove(answer)
                        user_answer = random.choice(options)
                    else:
                        user_answer = f"错误答案示例"
                    
                    # 创建错题记录
                    error_question = ErrorQuestion(
                        question_text=question_text,
                        subject=subject,
                        question_type=question_type,
                        difficulty=difficulty,
                        answer=answer,
                        user_answer=user_answer,
                        explanation=explanation
                    )
                    
                    session.add(error_question)
                    session.flush()  # 获取新生成的ID
                    question_ids.append(error_question.id)
            
            # 如果需要生成更多数据，随机生成剩余的题目
            remaining = count - len(question_ids)
            for i in range(remaining):
                if i < 0:  # 防止生成过多数据
                    break
                    
                subject = random.choice(subjects)
                question_type = random.choice(question_types)
                difficulty = random.randint(1, 5)
                
                # 根据学科和题型生成不同的题目
                if subject == "数学":
                    if question_type == "计算题":
                        a, b = random.randint(10, 100), random.randint(10, 100)
                        question_text = f"计算: {a} + {b} = ?"
                        answer = str(a + b)
                        explanation = f"将{a}与{b}相加得到{a+b}"
                    else:
                        question_text = f"数学{question_type}额外示例问题{i+1}"
                        answer = f"答案{i+1}"
                        explanation = f"解析说明{i+1}"
                elif subject == "物理":
                    question_text = f"物理{question_type}额外示例问题{i+1}"
                    answer = f"答案{i+1}"
                    explanation = f"解析说明{i+1}"
                else:
                    question_text = f"{subject}{question_type}额外示例问题{i+1}"
                    answer = f"答案{i+1}"
                    explanation = f"详细解析{i+1}"
                
                # 创建用户错误答案
                if question_type == "选择题":
                    options = ["A", "B", "C", "D"]
                    if answer in options:
                        options.remove(answer)
                    user_answer = random.choice(options) if options else "C"
                else:
                    user_answer = f"错误答案{i+1}"
                
                # 创建错题记录
                error_question = ErrorQuestion(
                    question_text=question_text,
                    subject=subject,
                    question_type=question_type,
                    difficulty=difficulty,
                    answer=answer,
                    user_answer=user_answer,
                    explanation=explanation
                )
                
                session.add(error_question)
                session.flush()  # 获取新生成的ID
                question_ids.append(error_question.id)
            
            session.commit()
            logger.info(f"成功生成 {len(question_ids)} 条示例数据")
            return question_ids
        except Exception as e:
            session.rollback()
            logger.error(f"生成示例数据失败: {str(e)}")
            raise e
        finally:
            session.close()
    
    def verify_data_consistency(self):
        """验证数据一致性，删除无效记录
        
        Returns:
            已清理的记录数
        """
        session = self.Session()
        try:
            # 获取所有记录
            questions = session.query(ErrorQuestion).all()
            
            # 检查记录完整性
            cleaned_count = 0
            for q in questions:
                # 检查必要字段
                if not q.question_text or not q.subject:
                    logger.warning(f"删除无效错题记录: ID={q.id}, 原因=缺少必要字段")
                    session.delete(q)
                    cleaned_count += 1
                    continue
                
                # 规范化难度值
                if q.difficulty < 1 or q.difficulty > 5:
                    logger.warning(f"修正错题难度: ID={q.id}, 原值={q.difficulty}")
                    q.difficulty = max(1, min(5, q.difficulty))
            
            if cleaned_count > 0:
                session.commit()
                logger.info(f"数据一致性验证完成: 删除了 {cleaned_count} 条无效记录")
            return cleaned_count
        except Exception as e:
            session.rollback()
            logger.error(f"数据一致性验证失败: {str(e)}")
            return 0
        finally:
            session.close()
    
    def get_statistics(self):
        """获取统计数据
        
        Returns:
            统计数据字典
        """
        session = self.Session()
        try:
            # 获取总数
            total_count = session.query(ErrorQuestion).count()
            
            # 学科分布 - 使用正确的分组统计方法
            subject_stats = {}
            subject_query = session.query(
                ErrorQuestion.subject, 
                func.count(ErrorQuestion.id)
            ).group_by(ErrorQuestion.subject).all()
            
            for subject, count in subject_query:
                subject_stats[subject] = count
            
            # 难度分布 - 使用正确的分组统计方法
            difficulty_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            difficulty_query = session.query(
                ErrorQuestion.difficulty, 
                func.count(ErrorQuestion.id)
            ).group_by(ErrorQuestion.difficulty).all()
            
            for difficulty, count in difficulty_query:
                if 1 <= difficulty <= 5:  # 确保难度在有效范围内
                    difficulty_stats[difficulty] = count
            
            # 最近添加的错题
            recent_questions = [q.to_dict() for q in session.query(ErrorQuestion)
                               .order_by(desc(ErrorQuestion.created_at))
                               .limit(5).all()]
            
            # 按科目+难度组合的统计
            combined_stats = []
            combined_query = session.query(
                ErrorQuestion.subject,
                ErrorQuestion.difficulty,
                func.count(ErrorQuestion.id)
            ).group_by(
                ErrorQuestion.subject,
                ErrorQuestion.difficulty
            ).all()
            
            for subject, difficulty, count in combined_query:
                combined_stats.append({
                    "subject": subject,
                    "difficulty": difficulty,
                    "count": count
                })
                
            logger.info(f"获取统计数据: 总错题数={total_count}, 学科数={len(subject_stats)}")
            return {
                "total_count": total_count,
                "subject_stats": subject_stats,
                "difficulty_stats": difficulty_stats,
                "combined_stats": combined_stats,
                "recent_questions": recent_questions
            }
        except Exception as e:
            logger.error(f"获取统计数据失败: {str(e)}")
            return {
                "total_count": 0,
                "subject_stats": {},
                "difficulty_stats": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "combined_stats": [],
                "recent_questions": []
            }
        finally:
            session.close()

    def batch_add_error_questions(self, result_json: dict) -> None:
        """批量添加错题数据
        
        Args:
            result_json: 包含错题信息的字典
        """
        session = self.Session()
        try:
            # 解析结果并插入数据库
            for question in result_json.get("error_questions", []):
                error_question = ErrorQuestion(
                    question_text=question.get("question_text"),
                    subject=question.get("subject"),
                    question_type=question.get("question_type"),
                    difficulty=question.get("difficulty"),
                    answer=question.get("answer"),
                    user_answer=question.get("user_answer"),
                    explanation=question.get("explanation")
                )
                session.add(error_question)
            
            # 提交事务
            session.commit()
            logger.info("成功批量添加错题数据到数据库")
            
        except Exception as e:
            session.rollback()
            logger.error(f"批量添加错题失败: {str(e)}")
            raise e
        finally:
            session.close()
