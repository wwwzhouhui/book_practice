-- 创建错题表
CREATE TABLE error_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL COMMENT '题目内容',
    subject VARCHAR(50) NOT NULL COMMENT '学科',
    question_type VARCHAR(50) NOT NULL COMMENT '题目类型',
    difficulty INTEGER NOT NULL COMMENT '难度等级(1-5)',
    answer TEXT COMMENT '答案',
    user_answer TEXT COMMENT '用户答案',
    explanation TEXT COMMENT '解析',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);