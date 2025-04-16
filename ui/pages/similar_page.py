import gradio as gr
import pandas as pd
from modules.storage.database import Database
from modules.ai_generator.question_generator import QuestionGenerator
import logging

logger = logging.getLogger(__name__)

def create_similar_page():
    """创建同类题生成页面"""
    
    # 初始化数据库和生成器
    db = Database()
    generator = QuestionGenerator()
    
    with gr.Tab("生成同类题"):
        with gr.Row():
            with gr.Column(scale=1):
                # 筛选条件
                subject = gr.Dropdown(
                    choices=["数学", "物理", "化学"],
                    label="学科",
                    value="数学"
                )
                question_type = gr.Dropdown(
                    choices=["","选择题", "填空题", "判断题", "问答题"],
                    label="题型"
                )
                # difficulty = gr.Dropdown(
                #     choices=["", "简单", "中等", "困难"],
                #     label="难度",
                #     value=""
                # )
                date_range = gr.Dropdown(
                    choices=["全部", "最近一周", "最近一月"],
                    label="时间范围",
                    value="全部"
                )
                search_btn = gr.Button("查询错题")
            
            with gr.Column(scale=2):
                # 错题列表
                question_table = gr.Dataframe(
                    headers=["题目ID", "题目内容", "学科", "题型", "难度", "创建时间"],
                    interactive=True,
                    label="错题列表"
                )
                
                with gr.Row():
                    selected_count = gr.Text(label="已选择题目数", value="0", interactive=False)
                    gen_count = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=1,
                        step=1,
                        label="生成数量"
                    )
                    generate_btn = gr.Button("生成同类题", interactive=False)
                
                # 生成结果
                with gr.Row():
                    result_status = gr.Text(label="生成状态", interactive=False)
                    save_btn = gr.Button("保存生成结果", interactive=False)
                
                result_table = gr.Dataframe(
                    headers=["题目内容", "答案", "解析"],
                    label="生成结果",
                    visible=False
                )

        # 定义事件处理函数
        def search_questions(subject, question_type, date_range):
            """查询错题"""
            try:
                # 根据 Database 类的实际方法参数进行查询
                questions = db.get_all_error_questions(
                    subject=subject,
                    question_type=question_type if question_type else None,
                    time_range=date_range
                )
                
                if not questions:
                    return gr.update(value=pd.DataFrame()), "未找到符合条件的错题"
                
                # 在内存中根据难度进行过滤
                # if difficulty:
                #     questions = [q for q in questions if q["difficulty"] == difficulty]
                
                df = pd.DataFrame({
                    "题目ID": [q["id"] for q in questions],
                    "题目内容": [q["question_text"] for q in questions],
                    "学科": [q["subject"] for q in questions],
                    "题型": [q["question_type"] for q in questions],
                    "难度": [q["difficulty"] for q in questions],
                    "创建时间": [q["created_at"] for q in questions]
                })
                
                return gr.update(value=df, interactive=True), ""
                
            except Exception as e:
                logger.error(f"查询错题失败: {str(e)}")
                return gr.update(value=pd.DataFrame()), f"查询失败: {str(e)}"

        def update_selection(evt: gr.SelectData):
            """更新选择状态"""
            return str(len(evt.index))

        def generate_similar_questions(selected_rows, gen_count):
            """生成同类题"""
            try:
                if not selected_rows or len(selected_rows) == 0:
                    return "请先选择错题", gr.update(visible=False), gr.update(interactive=False)
                
                # 获取选中的错题
                question_ids = [row["题目ID"] for row in selected_rows]
                source_questions = [db.get_error_question(qid) for qid in question_ids]
                
                # 生成同类题
                generated = generator.generate_similar_questions(
                    source_questions,
                    count=gen_count
                )
                
                if not generated:
                    return "生成失败", gr.update(visible=False), gr.update(interactive=False)
                
                # 转换为DataFrame
                df = pd.DataFrame({
                    "题目内容": [q["question_text"] for q in generated],
                    "答案": [q["answer"] for q in generated],
                    "解析": [q["explanation"] for q in generated]
                })
                
                return "生成成功", gr.update(value=df, visible=True), gr.update(interactive=True)
                
            except Exception as e:
                logger.error(f"生成同类题失败: {str(e)}")
                return f"生成失败: {str(e)}", gr.update(visible=False), gr.update(interactive=False)

        def save_generated_questions(result_df):
            """保存生成的题目"""
            try:
                if result_df is None or len(result_df) == 0:
                    return "没有可保存的题目"
                
                # 保存到数据库
                for _, row in result_df.iterrows():
                    db.save_similar_question({
                        "question_text": row["题目内容"],
                        "answer": row["答案"],
                        "explanation": row["解析"]
                    })
                
                return f"成功保存 {len(result_df)} 道题目"
                
            except Exception as e:
                logger.error(f"保存生成题目失败: {str(e)}")
                return f"保存失败: {str(e)}"

        # 绑定事件处理函数
        search_btn.click(
            search_questions,
            inputs=[subject, question_type, date_range],
            outputs=[question_table, result_status]
        )
        
        question_table.select(
            update_selection,
            outputs=[selected_count]
        )
        
        generate_btn.click(
            generate_similar_questions,
            inputs=[question_table, gen_count],
            outputs=[result_status, result_table, save_btn]
        )
        
        save_btn.click(
            save_generated_questions,
            inputs=[result_table],
            outputs=[result_status]
        )

    return "生成同类题"






