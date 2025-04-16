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
-- 错题同类型题目表
CREATE TABLE similar_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 基本信息
    question_text TEXT NOT NULL COMMENT '题目内容',
    subject VARCHAR(50) NOT NULL COMMENT '学科',
    question_type VARCHAR(50) NOT NULL COMMENT '题目类型',
    difficulty INTEGER NOT NULL COMMENT '难度等级(1-5)',
    answer TEXT COMMENT '答案',
    explanation TEXT COMMENT '解析',
    
    -- 关联信息
    source_question_id INTEGER NOT NULL COMMENT '原始错题ID',
    
    -- 时间信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    FOREIGN KEY (source_question_id) REFERENCES error_questions(id)
);

-- 创建索引
CREATE INDEX idx_source_question ON similar_questions(source_question_id);
CREATE INDEX idx_subject_type ON similar_questions(subject, question_type);