import gradio as gr
import pandas as pd
from modules.storage.database import Database
import json
import os
import csv
import time

def create_search_page():
    """创建错题查询页面"""
    # 初始化数据库
    db = Database()
    
    with gr.Column() as search_page:
        gr.Markdown("## 错题查询")
        
        # 搜索条件区域
        with gr.Row():
            with gr.Column(scale=2):
                search_input = gr.Textbox(
                    label="搜索关键词",
                    placeholder="输入题号或题目内容关键词..."
                )
                
            with gr.Column(scale=3):
                with gr.Row():
                    filters = gr.CheckboxGroup(
                        choices=["数学", "物理", "化学"],
                        label="科目筛选",
                        value=[]
                    )
                    date_range = gr.Dropdown(
                        choices=["今天", "最近一周", "最近一月", "全部"],
                        label="时间范围",
                        value="全部"
                    )
                
                search_button = gr.Button("查询错题", variant="primary")
        
        # 添加查询状态指示器
        query_status = gr.Markdown('准备就绪，点击"显示所有错题"按钮加载数据')
        
        # 错题列表区域
        gr.Markdown("### 错题列表")
        
        # 错题列表表格
        results = gr.DataFrame(
            headers=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"],
            label="查询结果",
            wrap=True,
            height=300
        )
        
        # 操作按钮区
        with gr.Row():
            with gr.Column(scale=3):
                refresh_button = gr.Button("显示所有错题", variant="primary")
            
            with gr.Column(scale=2):
                export_button = gr.Button("导出结果", variant="secondary")
                
            with gr.Column(scale=2):
                delete_button = gr.Button("删除选中错题", variant="stop")
                
        # 操作状态
        status = gr.Label(label="状态")
        
        # 错题详情展示区 - 使用visible控制而不是Group组件
        detail_visible = gr.Checkbox(visible=False, value=False, label="详情可见性控制")
        
        with gr.Row(visible=False) as question_detail_row:
            gr.Markdown("## 错题详情")
            
            with gr.Tabs() as detail_tabs:
                with gr.TabItem("题目信息"):
                    detail_markdown = gr.Markdown()
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            subject_display = gr.Textbox(label="学科", interactive=False)
                            difficulty_display = gr.Textbox(label="难度", interactive=False)
                        
                        with gr.Column(scale=1):
                            question_type_display = gr.Textbox(label="题型", interactive=False)
                            created_at_display = gr.Textbox(label="创建时间", interactive=False)
                    
                    with gr.Row():
                        correct_answer = gr.Textbox(label="正确答案", interactive=False, lines=2)
                        user_answer = gr.Textbox(label="学生答案", interactive=False, lines=2)
                
                with gr.TabItem("解析"):
                    explanation = gr.Textbox(label="题目解析", lines=8, interactive=False)
            
            # 添加返回按钮
            back_button = gr.Button("返回列表", variant="secondary")
        
        # 记录当前选中的行
        selected_row_index = gr.State(-1)
        selected_question_id = gr.State(None)
        
        # 函数：切换详情可见性
        def toggle_detail_visibility(visible):
            return gr.update(visible=visible)
        
        # 加载所有错题数据
        def load_all_data():
            try:
                questions = db.get_all_error_questions(limit=100)
                
                if questions:
                    data = {
                        "题目ID": [q["id"] for q in questions],
                        "题目内容": [q["question_text"][:50] + "..." if len(q["question_text"]) > 50 else q["question_text"] for q in questions],
                        "科目": [q["subject"] for q in questions],
                        "题型": [q["question_type"] for q in questions],
                        "难度": [f"{'⭐' * q['difficulty']}" for q in questions],
                        "提交时间": [q["created_at"] for q in questions]
                    }
                    df = pd.DataFrame(data)
                    return f"显示所有错题，共 {len(questions)} 条", df
                else:
                    empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                    return "数据库中没有错题记录", empty_df
            except Exception as e:
                print(f"加载数据错误: {str(e)}")
                empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                return f"加载数据出错: {str(e)}", empty_df
        
        # 搜索功能实现
        def search_questions(search_text, subjects, time_range):
            try:
                # 更新查询状态
                query_status_text = "正在查询..."
                
                # 筛选条件
                subject_filter = subjects if subjects else None
                
                # 获取错题数据
                questions = db.get_all_error_questions(
                    subject=subject_filter,
                    time_range=time_range,
                    limit=100
                )
                
                # 如果有搜索关键词，进行简单过滤
                if search_text:
                    search_text = search_text.lower()
                    filtered_questions = []
                    for q in questions:
                        # 按题号搜索
                        if str(q["id"]) == search_text:
                            filtered_questions.append(q)
                            continue
                        
                        # 按题目内容搜索
                        if search_text in q["question_text"].lower():
                            filtered_questions.append(q)
                            continue
                    
                    questions = filtered_questions
                
                # 转换为DataFrame显示格式
                if questions:
                    data = {
                        "题目ID": [q["id"] for q in questions],
                        "题目内容": [q["question_text"][:50] + "..." if len(q["question_text"]) > 50 else q["question_text"] for q in questions],
                        "科目": [q["subject"] for q in questions],
                        "题型": [q["question_type"] for q in questions],
                        "难度": [f"{'⭐' * q['difficulty']}" for q in questions],
                        "提交时间": [q["created_at"] for q in questions]
                    }
                    df = pd.DataFrame(data)
                    query_status_text = f"找到 {len(questions)} 条结果"
                    
                    # 返回所有输出
                    return (query_status_text, df, True, True, "", "", "", "", "", "", "", -1, None)
                else:
                    # 返回空DataFrame
                    empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                    query_status_text = "未找到符合条件的错题"
                    
                    # 返回所有输出
                    return (query_status_text, empty_df, False, False, "", "", "", "", "", "", "", -1, None)
            
            except Exception as e:
                # 返回错误信息
                empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                query_status_text = f"搜索出错: {str(e)}"
                
                # 返回所有输出
                return (query_status_text, empty_df, False, False, "", "", "", "", "", "", "", -1, None)
        
        # 显示错题详情
        def show_question_detail(evt: gr.SelectData):
            if not evt:
                return False, False, "", "", "", "", "", "", "", -1, None
            
            try:
                row_index = evt.index[0]
                question_id = results.value.iloc[row_index]["题目ID"]
                
                # 查询问题详情
                question = db.get_error_question(question_id)
                
                if question:
                    # 构建详情显示
                    difficulty_stars = "⭐" * question["difficulty"]
                    detail_text = f"""
### 题目内容

{question["question_text"]}
"""
                    return True, True, detail_text, question["subject"], question["question_type"], difficulty_stars, question["created_at"], question["answer"], question["user_answer"], question["explanation"] or "无解析", row_index, question_id
                else:
                    return False, False, "", "", "", "", "", "", "", -1, None
            except Exception as e:
                print(f"显示详情错误: {str(e)}")
                return False, False, "", "", "", "", "", "", "", -1, None
        
        # 导出功能
        def export_results(dataframe):
            if dataframe is None or dataframe.empty:
                return "没有可导出的数据"
            
            try:
                # 获取所有ID对应的完整数据
                ids = dataframe["题目ID"].tolist()
                full_data = []
                
                for qid in ids:
                    question = db.get_error_question(qid)
                    if question:
                        full_data.append(question)
                
                # 创建导出目录
                export_dir = os.path.join(os.getcwd(), "exports")
                os.makedirs(export_dir, exist_ok=True)
                
                # 导出为CSV
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                csv_path = os.path.join(export_dir, f"错题数据_{timestamp}.csv")
                
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    fieldnames = ["id", "subject", "question_type", "difficulty", 
                                  "question_text", "answer", "user_answer", 
                                  "explanation", "created_at"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for item in full_data:
                        writer.writerow(item)
                
                return f"✅ 已成功导出 {len(full_data)} 条数据至：{csv_path}"
            except Exception as e:
                return f"❌ 导出失败: {str(e)}"
        
        # 删除错题功能
        def delete_question(selected_id):
            if not selected_id:
                return "请先选择要删除的错题"
            
            try:
                # 删除错题
                success = db.delete_error_question(selected_id)
                
                if success:
                    # 返回成功信息
                    return f"✅ 成功删除错题(ID: {selected_id})"
                else:
                    return f"❌ 删除失败：未找到ID为 {selected_id} 的错题"
            except Exception as e:
                return f"❌ 删除错题时出错: {str(e)}"
        
        # 返回列表视图
        def back_to_list():
            return False, False, "", "", "", "", "", "", "", -1, None
        
        # 删除后刷新
        def delete_and_refresh(selected_id):
            # 先删除
            status_msg = delete_question(selected_id)
            
            # 再刷新数据
            refresh_msg, refreshed_data = load_all_data()
            
            # 返回状态和刷新的数据
            return status_msg, refreshed_data, False, False, "", "", "", "", "", "", "", -1, None
        
        # 监听详情可见性变化
        detail_visible.change(
            toggle_detail_visibility,
            inputs=[detail_visible],
            outputs=[question_detail_row]
        )
        
        # 绑定事件
        search_button.click(
            search_questions,
            inputs=[search_input, filters, date_range],
            outputs=[
                query_status,
                results, 
                detail_visible,
                question_detail_row,
                detail_markdown, 
                subject_display,
                question_type_display,
                difficulty_display,
                created_at_display,
                correct_answer, 
                user_answer, 
                explanation,
                selected_row_index,
                selected_question_id
            ]
        )
        
        results.select(
            show_question_detail,
            None,
            [
                detail_visible,
                question_detail_row, 
                detail_markdown, 
                subject_display,
                question_type_display,
                difficulty_display,
                created_at_display,
                correct_answer, 
                user_answer, 
                explanation,
                selected_row_index,
                selected_question_id
            ]
        )
        
        back_button.click(
            back_to_list,
            None,
            [
                detail_visible,
                question_detail_row, 
                detail_markdown, 
                subject_display,
                question_type_display,
                difficulty_display,
                created_at_display,
                correct_answer, 
                user_answer, 
                explanation,
                selected_row_index,
                selected_question_id
            ]
        )
        
        export_button.click(
            export_results,
            inputs=[results],
            outputs=[status]
        )
        
        # 删除按钮使用新的删除并刷新函数
        delete_button.click(
            delete_and_refresh,
            inputs=[selected_question_id],
            outputs=[
                status, 
                results,
                detail_visible,
                question_detail_row,
                detail_markdown, 
                subject_display,
                question_type_display,
                difficulty_display,
                created_at_display,
                correct_answer, 
                user_answer, 
                explanation,
                selected_row_index,
                selected_question_id
            ]
        )
        
        refresh_button.click(
            load_all_data,
            outputs=[query_status, results]
        )
        
        # 初始加载所有数据
        try:
            initial_status, initial_data = load_all_data()
            query_status.value = initial_status
            results.value = initial_data
        except Exception as e:
            query_status.value = f"加载初始数据失败: {str(e)}"
    
    return search_page

