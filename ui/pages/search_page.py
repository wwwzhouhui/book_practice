import gradio as gr
import pandas as pd
import numpy as np
from modules.storage.database import Database
import json
import os
import csv
import time
import logging
import traceback

# 配置日志
logger = logging.getLogger(__name__)

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
            wrap=True
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
        status = gr.Label(label="状态", value="")
        
        # 错题详情展示区
        with gr.Group(visible=False) as question_detail_group:
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
                logger.error(f"加载数据错误: {str(e)}")
                logger.error(traceback.format_exc())
                empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                return f"加载数据出错: {str(e)}", empty_df
        
        # 搜索功能实现
        def search_questions(search_text, subjects, time_range):
            logger.info(f"搜索条件: {search_text}, {subjects}, {time_range}")
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
                else:
                    # 返回空DataFrame
                    df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                    query_status_text = "未找到符合条件的错题"
                
                return query_status_text, df
            
            except Exception as e:
                # 记录错误日志
                logger.error(f"搜索出错: {str(e)}")
                logger.error(traceback.format_exc())
                
                # 返回错误信息
                empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                query_status_text = f"搜索出错: {str(e)}"
                
                return query_status_text, empty_df
        
        # 处理DataFrame结构
        def process_dataframe_structure(df_value):
            """处理并转换非标准的DataFrame结构"""
            try:
                # 如果已经是标准DataFrame，检查是否含有所需列
                if isinstance(df_value, pd.DataFrame):
                    if "题目ID" in df_value.columns:
                        return df_value
                    
                    # 输出列信息便于调试
                    logger.info(f"DataFrame列: {df_value.columns.tolist()}")
                    
                    # 特殊情况：['headers', 'data', 'metadata']结构
                    if all(col in df_value.columns for col in ['headers', 'data']):
                        try:
                            # 尝试解析这种特殊结构
                            headers = df_value['headers'].tolist() if isinstance(df_value['headers'], pd.Series) else df_value['headers']
                            data = df_value['data'].tolist() if isinstance(df_value['data'], pd.Series) else df_value['data']
                            
                            # 记录这些数据的结构
                            logger.info(f"Headers type: {type(headers)}, Data type: {type(data)}")
                            
                            # 如果headers和data都是列表，可以尝试重构
                            if isinstance(headers, list) and isinstance(data, list):
                                # 确保headers中包含"题目ID"
                                if "题目ID" not in headers:
                                    logger.error("Headers中不包含'题目ID'列")
                                    return pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                                
                                # 构建新的DataFrame
                                # 假设data是一个行列表，每一行是与headers对应的值列表
                                new_data = {}
                                for i, header in enumerate(headers):
                                    # 提取每一列的数据
                                    column_data = []
                                    for row in data:
                                        if i < len(row):
                                            column_data.append(row[i])
                                        else:
                                            column_data.append(None)
                                    new_data[header] = column_data
                                
                                return pd.DataFrame(new_data)
                        except Exception as e:
                            logger.error(f"处理特殊DataFrame结构失败: {str(e)}")
                            logger.error(traceback.format_exc())
                
                # 处理字典类型
                elif isinstance(df_value, dict):
                    # 记录字典结构
                    for k, v in df_value.items():
                        logger.info(f"Key: {k}, Type: {type(v)}, Length: {len(v) if hasattr(v, '__len__') else 'N/A'}")
                    
                    # 处理特殊字典结构
                    if 'headers' in df_value and 'data' in df_value:
                        headers = df_value['headers']
                        data = df_value['data']
                        
                        if isinstance(headers, list) and isinstance(data, list):
                            # 同上，构建新的字典结构
                            new_data = {}
                            for i, header in enumerate(headers):
                                column_data = []
                                for row in data:
                                    if i < len(row):
                                        column_data.append(row[i])
                                    else:
                                        column_data.append(None)
                                new_data[header] = column_data
                            
                            return pd.DataFrame(new_data)
                    
                    # 尝试规范化普通字典
                    try:
                        normalized_dict = normalize_dict(df_value)
                        return pd.DataFrame(normalized_dict)
                    except Exception as e:
                        logger.error(f"规范化字典失败: {str(e)}")
                
                # 其他情况，返回空DataFrame
                logger.error(f"无法处理的数据类型: {type(df_value)}")
                return pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
            
            except Exception as e:
                logger.error(f"处理DataFrame结构时出错: {str(e)}")
                logger.error(traceback.format_exc())
                return pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
        
        # 规范化字典函数，确保所有键的值具有相同的长度
        def normalize_dict(d):
            # 找出字典中非空列表值的最大长度
            max_len = 0
            for v in d.values():
                if isinstance(v, list) and len(v) > max_len:
                    max_len = len(v)
                    
            # 规范化所有值为相同长度的列表
            result = {}
            for k, v in d.items():
                if isinstance(v, list):
                    # 如果是列表但长度不够，填充None
                    if len(v) < max_len:
                        result[k] = v + [None] * (max_len - len(v))
                    else:
                        result[k] = v
                else:
                    # 如果不是列表，创建一个填充了相同值的列表
                    result[k] = [v] * max_len if max_len > 0 else []
                    
            return result
        
        # 显示错题详情
        def show_question_detail(evt: gr.SelectData):
            try:
                if not evt or not hasattr(evt, 'index') or not evt.index:
                    logger.error("无效的选择事件")
                    return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
                
                row_index = evt.index[0]
                
                # 获取DataFrame元素并处理
                df_value = process_dataframe_structure(results.value)
                
                # 安全获取题目ID
                try:
                    # 确保索引有效
                    if row_index >= len(df_value):
                        logger.error(f"行索引超出范围: {row_index}, 总行数: {len(df_value)}")
                        return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
                    
                    # 确保列名存在
                    if "题目ID" not in df_value.columns:
                        logger.error(f"DataFrame缺少'题目ID'列: {df_value.columns.tolist()}")
                        return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
                    
                    question_id = df_value.iloc[row_index]["题目ID"]
                    
                except Exception as idx_error:
                    logger.error(f"获取题目ID时出错: {str(idx_error)}")
                    logger.error(traceback.format_exc())
                    return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
                
                # 查询问题详情
                question = db.get_error_question(question_id)
                
                if question:
                    # 构建详情显示
                    difficulty_stars = "⭐" * question["difficulty"]
                    detail_text = f"""
### 题目内容

{question["question_text"]}
"""
                    return [
                        gr.update(visible=True),           # question_detail_group
                        detail_text,                       # detail_markdown
                        question["subject"],               # subject_display
                        question["question_type"],         # question_type_display
                        difficulty_stars,                  # difficulty_display
                        question["created_at"],            # created_at_display
                        question["answer"],                # correct_answer
                        question["user_answer"],           # user_answer
                        question["explanation"] or "无解析", # explanation
                        row_index,                         # selected_row_index
                        question_id                        # selected_question_id
                    ]
                else:
                    return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
            
            except Exception as e:
                logger.error(f"显示详情错误: {str(e)}")
                logger.error(traceback.format_exc())
                return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
        
        # 导出功能
        def export_results(dataframe):
            if dataframe is None:
                return "没有可导出的数据"
            
            try:
                # 处理数据结构
                df = process_dataframe_structure(dataframe)
                
                if df.empty:
                    return "没有可导出的数据"
                
                # 获取所有ID对应的完整数据
                if "题目ID" not in df.columns:
                    return f"❌ 导出失败: 数据缺少'题目ID'列"
                
                ids = df["题目ID"].tolist()
                full_data = []
                
                for qid in ids:
                    if pd.isna(qid):  # 跳过NaN值
                        continue
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
                logger.error(f"导出失败: {str(e)}")
                logger.error(traceback.format_exc())
                return f"❌ 导出失败: {str(e)}"
        
        # 返回列表视图
        def back_to_list():
            return [gr.update(visible=False), "", "", "", "", "", "", "", "", -1, None]
        
        # 直接删除错题 - 不依赖选中行而是传入ID
        def direct_delete(question_id):
            if not question_id:
                return "请先选择要删除的错题", query_status.value, results.value, gr.update(visible=False)
            
            try:
                # 删除错题
                success = db.delete_error_question(question_id)
                
                # 获取最新数据
                refresh_msg, refreshed_data = load_all_data()
                
                if success:
                    status_msg = f"✅ 成功删除错题(ID: {question_id})"
                else:
                    status_msg = f"❌ 删除失败：未找到ID为 {question_id} 的错题"
                
                # 隐藏详情面板
                return status_msg, refresh_msg, refreshed_data, gr.update(visible=False)
            except Exception as e:
                logger.error(f"删除错题时出错: {str(e)}")
                logger.error(traceback.format_exc())
                
                # 尝试刷新数据
                try:
                    refresh_msg, refreshed_data = load_all_data()
                    return f"❌ 删除错题时出错: {str(e)}", refresh_msg, refreshed_data, gr.update(visible=False)
                except:
                    empty_df = pd.DataFrame(columns=["题目ID", "题目内容", "科目", "题型", "难度", "提交时间"])
                    return f"❌ 删除错题时出错: {str(e)}", "加载数据失败", empty_df, gr.update(visible=False)
        
        # 绑定事件
        search_button.click(
            search_questions,
            inputs=[search_input, filters, date_range],
            outputs=[query_status, results]
        )
        
        results.select(
            show_question_detail,
            None,
            [
                question_detail_group, 
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
                question_detail_group, 
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
        
        # 删除按钮使用直接删除函数
        delete_button.click(
            direct_delete,
            inputs=[selected_question_id],
            outputs=[status, query_status, results, question_detail_group]
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