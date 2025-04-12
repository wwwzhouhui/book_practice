import gradio as gr
from modules.storage.database import Database
import pandas as pd
import time

def create_home_page():
    """创建首页"""
    # 初始化数据库
    db = Database()
    
    with gr.Column() as home_page:
        with gr.Row():
            gr.Markdown("""
            # 欢迎使用智能作业识别系统
            
            本系统可以帮助您:
            
            - 自动识别和分析学生作业
            - 快速定位错题并进行分类
            - 生成个性化的练习题
            """)
        
        # 系统状态卡片
        with gr.Row():
            with gr.Column(variant="panel", scale=1):
                gr.Markdown("### 系统状态")
                system_status = gr.Label(value="系统运行正常", label="状态", elem_id="system_status")
                last_refresh = gr.Label(value=time.strftime("%Y-%m-%d %H:%M:%S"), label="最后刷新")
            
            with gr.Column(variant="panel", scale=1):
                gr.Markdown("### 数据概览")
                processed_count = gr.Label(value="0", label="已处理作业数", elem_id="processed_count")
                question_count = gr.Label(value="0", label="错题总数", elem_id="question_count")
        
        # 错题统计部分
        with gr.Accordion("错题数据统计", open=True):
            refresh_btn = gr.Button("刷新统计数据", variant="primary")
            
            with gr.Tabs() as display_tabs:
                # 统计概览标签页
                with gr.TabItem("统计概览"):
                    stats_md = gr.Markdown(elem_id="stats_overview")
                
                # 最近错题标签页
                with gr.TabItem("最近错题"):
                    with gr.Row():
                        recent_questions = gr.DataFrame(
                            headers=["题目ID", "科目", "题型", "难度", "时间"],
                            label="最近添加的错题",
                            wrap=True
                        )
            
            # 获取统计数据
            def get_statistics():
                try:
                    stats = db.get_statistics()
                    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    if stats["total_count"] == 0:
                        # 如果没有数据，生成一些示例数据
                        try:
                            db.generate_sample_data(count=18)  # 每个学科每个难度至少一个
                            stats = db.get_statistics()  # 重新获取统计数据
                            initial_msg = "⚠️ 未检测到数据，已自动生成示例数据用于展示。"
                        except Exception as e:
                            initial_msg = f"⚠️ 生成示例数据失败: {str(e)}"
                            return "系统运行异常", current_time, "0", "0", initial_msg, pd.DataFrame()
                    else:
                        initial_msg = ""
                    
                    # 生成统计文本
                    md_text = f"{initial_msg}\n\n### 错题统计\n\n**总错题数**: {stats['total_count']} 题\n\n"
                    
                    # 学科分布
                    md_text += "#### 学科分布\n"
                    if stats['subject_stats']:
                        for subject, count in stats["subject_stats"].items():
                            percent = (count / stats["total_count"]) * 100
                            md_text += f"- {subject}: {count}题 ({percent:.1f}%)\n"
                    else:
                        md_text += "- 暂无学科数据\n"
                    
                    # 难度分布
                    md_text += "\n#### 难度分布\n"
                    has_difficulty_data = False
                    for difficulty, count in stats["difficulty_stats"].items():
                        if count > 0:
                            has_difficulty_data = True
                            stars = "⭐" * difficulty
                            percent = (count / stats["total_count"]) * 100
                            md_text += f"- {stars}: {count}题 ({percent:.1f}%)\n"
                    
                    if not has_difficulty_data:
                        md_text += "- 暂无难度数据\n"
                    
                    # 准备最近错题数据
                    if stats["recent_questions"]:
                        recent_data = {
                            "题目ID": [],
                            "科目": [],
                            "题型": [],
                            "难度": [],
                            "时间": []
                        }
                        
                        for q in stats["recent_questions"]:
                            recent_data["题目ID"].append(q["id"])
                            recent_data["科目"].append(q["subject"])
                            recent_data["题型"].append(q["question_type"])
                            recent_data["难度"].append("⭐" * q["difficulty"])
                            recent_data["时间"].append(q["created_at"])
                        
                        recent_df = pd.DataFrame(recent_data)
                        
                        return "系统运行正常", current_time, "0", str(stats["total_count"]), md_text, recent_df
                    
                    return "系统运行正常", current_time, "0", str(stats["total_count"]), md_text, pd.DataFrame()
                
                except Exception as e:
                    error_msg = f"获取统计数据失败: {str(e)}"
                    return "系统运行异常", time.strftime("%Y-%m-%d %H:%M:%S"), "0", "0", error_msg, pd.DataFrame()
            
            # 初始加载统计数据
            system_status_val, last_refresh_val, processed_val, question_val, stats_text, recent_df = get_statistics()
            system_status.value = system_status_val
            last_refresh.value = last_refresh_val
            processed_count.value = processed_val
            question_count.value = question_val
            stats_md.value = stats_text
            recent_questions.value = recent_df
            
            # 刷新按钮事件
            refresh_btn.click(
                get_statistics,
                outputs=[system_status, last_refresh, processed_count, question_count, stats_md, recent_questions]
            )
            
            # 点击最近错题
            def on_question_click(evt: gr.SelectData):
                if not evt:
                    return
                
                try:
                    row_index = evt.index[0]
                    question_id = recent_questions.value.iloc[row_index]["题目ID"]
                    
                    gr.Info(f"已选择错题ID: {question_id}，请前往「错题查询」页面查看详情")
                except Exception as e:
                    gr.Warning(f"查看错题详情失败: {str(e)}")
            
            recent_questions.select(on_question_click)
    
    return home_page