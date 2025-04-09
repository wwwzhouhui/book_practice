import gradio as gr
import pandas as pd

def create_search_component(db):
    """创建错题查询组件
    
    Args:
        db: 数据库操作实例
        
    Returns:
        Gradio组件
    """
    with gr.Column() as search_component:
        with gr.Row():
            subject = gr.Dropdown(
                choices=["全部", "数学", "语文", "英语", "物理", "化学"],
                value="全部",
                label="学科筛选"
            )
            question_type = gr.Dropdown(
                choices=["全部", "选择题", "填空题", "计算题", "解答题", "证明题"],
                value="全部",
                label="题型筛选"
            )
            search_btn = gr.Button("查询", variant="primary")
        
        # 错题列表表格
        error_questions_table = gr.DataFrame(
            headers=["ID", "学科", "题型", "难度", "创建时间"],
            label="错题列表",
            interactive=False
        )
        
        # 选中的错题详情
        with gr.Group(visible=False) as question_detail:
            gr.Markdown("## 错题详情")
            question_text = gr.Markdown(label="题目内容")
            with gr.Row():
                answer = gr.Textbox(label="正确答案", interactive=False)
                user_answer = gr.Textbox(label="你的答案", interactive=False)
            explanation = gr.Textbox(label="解析", interactive=False, lines=5)
            
            # 添加返回按钮
            back_btn = gr.Button("返回列表")
        
        # 处理查询按钮点击事件
        def search_questions(subject_val, question_type_val):
            # 转换"全部"为None
            subject_filter = None if subject_val == "全部" else subject_val
            question_type_filter = None if question_type_val == "全部" else question_type_val
            
            # 查询数据库
            questions = db.get_all_error_questions(
                subject=subject_filter,
                question_type=question_type_filter
            )
            
            # 转换为DataFrame显示格式
            if questions:
                data = {
                    "ID": [q["id"] for q in questions],
                    "学科": [q["subject"] for q in questions],
                    "题型": [q["question_type"] for q in questions],
                    "难度": [q["difficulty"] for q in questions],
                    "创建时间": [q["created_at"] for q in questions]
                }
                df = pd.DataFrame(data)
                return df
            else:
                # 返回空DataFrame
                return pd.DataFrame(columns=["ID", "学科", "题型", "难度", "创建时间"])
        
        # 处理表格行选择事件
        def show_question_detail(evt: gr.SelectData):
            # 获取选中行的ID
            row_index = evt.index[0]
            # 通过表格数据获取问题ID
            question_id = error_questions_table.value.iloc[row_index]["ID"]
            
            # 查询问题详情
            question = db.get_error_question(question_id)
            
            if question:
                # 设置难度星标显示
                difficulty_stars = "⭐" * question["difficulty"]
                
                # 更新详情组件
                return (
                    True,  # 显示详情组
                    f"### {question['subject']} - {question['question_type']} {difficulty_stars}\n\n{question['question_text']}",
                    question["answer"],
                    question["user_answer"],
                    question["explanation"]
                )
            else:
                return False, "", "", "", ""
        
        # 点击返回按钮隐藏详情
        def hide_detail():
            return False, "", "", "", ""
        
        # 绑定事件
        search_btn.click(search_questions, [subject, question_type], [error_questions_table])
        error_questions_table.select(show_question_detail, None, [question_detail, question_text, answer, user_answer, explanation])
        back_btn.click(hide_detail, None, [question_detail, question_text, answer, user_answer, explanation])
        
        # 初始加载数据
        search_btn.click(fn=None)
    
    return search_component