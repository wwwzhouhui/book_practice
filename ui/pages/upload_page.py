import gradio as gr
from modules.storage.database import Database
import os
from pathlib import Path
import time
import pandas as pd

def create_upload_page():
    """创建作业上传页面"""
    # 初始化数据库
    db = Database()
    
    with gr.Column() as upload_page:
        gr.Markdown("## 作业上传与错题录入")
        
        with gr.Tabs() as upload_tabs:
            # 图片上传标签页
            with gr.TabItem("图片上传"):
                # 上传作业部分
                with gr.Row():
                    with gr.Column(scale=2):
                        file_input = gr.File(
                            label="上传作业图片",
                            file_types=["image"],
                            file_count="multiple"
                        )
                        upload_button = gr.Button("开始上传", variant="primary")
                    
                    with gr.Column(scale=3):
                        preview = gr.Image(label="预览", show_label=True)
                        status = gr.Label(label="处理状态")
                
                with gr.Row():
                    progress = gr.Progress(track_tqdm=True)
                    result = gr.Label(label="识别结果")
            
            # 手动录入标签页
            with gr.TabItem("手动录入"):
                with gr.Group():
                    gr.Markdown("### 错题信息")
                    
                    question_text = gr.Textbox(
                        label="题目内容",
                        placeholder="请输入题目内容...",
                        lines=4
                    )
                    
                    with gr.Row():
                        subject = gr.Dropdown(
                            choices=["数学", "物理", "化学"],
                            label="学科",
                            value="数学"
                        )
                        question_type = gr.Dropdown(
                            choices=["选择题", "填空题", "计算题", "解答题"],
                            label="题型",
                            value="选择题"
                        )
                        difficulty = gr.Slider(
                            minimum=1, 
                            maximum=5, 
                            value=3, 
                            step=1, 
                            label="难度"
                        )
                    
                    gr.Markdown("### 答案与解析")
                    with gr.Row():
                        answer = gr.Textbox(
                            label="正确答案",
                            placeholder="请输入正确答案..."
                        )
                        user_answer = gr.Textbox(
                            label="我的答案",
                            placeholder="请输入你的答案..."
                        )
                    
                    explanation = gr.Textbox(
                        label="解析",
                        placeholder="请输入解析说明...",
                        lines=3
                    )
                    
                    with gr.Row():
                        save_btn = gr.Button("保存错题", variant="primary")
                        clear_btn = gr.Button("清空表单", variant="secondary")
                    
                    save_result = gr.Markdown()
            
            # 批量导入标签页
            with gr.TabItem("批量导入"):
                with gr.Group():
                    gr.Markdown("### 批量导入错题")
                    
                    with gr.Accordion("生成示例数据", open=True):
                        gr.Markdown("""
                        使用此功能可以快速生成示例错题数据，便于测试系统功能。
                        生成的数据将包含随机的题目内容、学科、题型、难度等信息。
                        """)
                        
                        with gr.Row():
                            sample_count = gr.Slider(
                                minimum=1, 
                                maximum=50, 
                                value=3, 
                                step=1, 
                                label="生成数量"
                            )
                            gen_sample_btn = gr.Button("生成示例错题", variant="primary")
                        
                        gen_result = gr.Markdown()
                        
                        # 显示生成的数据
                        gen_data_display = gr.DataFrame(
                            headers=["题目ID", "学科", "题型", "难度", "创建时间"],
                            label="生成的数据预览",
                            visible=False,
                            height=250
                        )
        
        # 处理保存错题
        def save_error_question(question_text, subject, question_type, difficulty, answer, user_answer, explanation):
            if not question_text or not subject or not question_type or not answer:
                return "❌ 请填写必填字段：题目内容、学科、题型、正确答案"
            
            question_data = {
                "question_text": question_text,
                "subject": subject,
                "question_type": question_type,
                "difficulty": int(difficulty),
                "answer": answer,
                "user_answer": user_answer,
                "explanation": explanation
            }
            
            try:
                question_id = db.add_error_question(question_data)
                return f"✅ 错题保存成功！ID: {question_id}\n\n保存时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            except Exception as e:
                return f"❌ 保存失败: {str(e)}"
        
        # 清空表单
        def clear_form():
            return "", "数学", "选择题", 3, "", "", "", ""
        
        # 处理上传图片
        def process_upload(files):
            if not files:
                return None, "请先上传文件"
            
            # 只处理第一个文件作为预览
            preview_file = files[0]
            status_text = f"已上传 {len(files)} 个文件，准备处理..."
            
            return preview_file, status_text
        
        # 生成示例数据
        def generate_samples(count):
            try:
                # 确保count是整数
                count = int(count)
                if count <= 0:
                    return "❌ 生成数量必须大于0", gr.update(visible=False), None
                
                # 调用数据库生成示例数据
                question_ids = db.generate_sample_data(count=count)
                
                # 获取生成的数据
                questions = []
                for qid in question_ids:
                    q = db.get_error_question(qid)
                    if q:
                        questions.append(q)
                
                # 准备显示数据
                if questions:
                    data = {
                        "题目ID": [q["id"] for q in questions],
                        "学科": [q["subject"] for q in questions],
                        "题型": [q["question_type"] for q in questions],
                        "难度": [f"{'⭐' * q['difficulty']}" for q in questions],
                        "创建时间": [q["created_at"] for q in questions]
                    }
                    df = pd.DataFrame(data)
                    
                    # 显示数据框并返回成功消息
                    return f"✅ 成功生成 {len(question_ids)} 条示例错题数据", gr.update(visible=True), df
                
                return f"✅ 成功生成 {len(question_ids)} 条示例错题数据，但无法获取详细信息", gr.update(visible=False), None
            
            except Exception as e:
                return f"❌ 生成示例数据失败: {str(e)}", gr.update(visible=False), None
        
        # 绑定事件
        save_btn.click(
            save_error_question, 
            inputs=[question_text, subject, question_type, difficulty, answer, user_answer, explanation],
            outputs=[save_result]
        )
        
        clear_btn.click(
            clear_form,
            outputs=[question_text, subject, question_type, difficulty, answer, user_answer, explanation, save_result]
        )
        
        upload_button.click(
            process_upload,
            inputs=[file_input],
            outputs=[preview, status]
        )
        
        gen_sample_btn.click(
            generate_samples,
            inputs=[sample_count],
            outputs=[gen_result, gen_data_display, gen_data_display]
        )
    
    return upload_page