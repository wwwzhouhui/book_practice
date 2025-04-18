import gradio as gr
import os
import tempfile
from pathlib import Path
import sys
import time
import pandas as pd
import logging

# 配置日志
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from modules.storage.database import Database
from modules.image_processing.image_processor import ImageProcessor

def process_images(files, subject, progress=gr.Progress()):
    """处理上传的图像文件

    Args:
        files: 上传的文件列表 (期望是列表)
        subject: 选择的学科
        progress: Gradio进度条

    Returns:
        预览图像和处理摘要
    """
    if not files:
        return None, "未选择文件"

    # 创建图像处理器 (使用默认值，默认使用模拟数据)
    processor = ImageProcessor()

    # 确保 files 是列表类型 (尽管错误发生在更早阶段，这里保留是好的实践)
    if not isinstance(files, list):
        logger.warning(f"process_images 收到的 files 不是列表，类型为: {type(files)}. 尝试转换为列表.")
        # 假设它可能是单个文件对象或路径
        if hasattr(files, 'name'): # Gradio 文件对象
             files = [files.name]
        elif isinstance(files, str): # 字符串路径
             files = [files]
        else:
            logger.error(f"无法将类型 {type(files)} 的 files 转换为列表。")
            return None, f"内部错误：无法处理输入文件类型 {type(files)}"


    # 获取文件路径列表
    file_paths = []
    for file_obj in files: # 迭代列表中的每个元素
        if isinstance(file_obj, str):
            file_paths.append(file_obj)  # 如果是字符串路径，直接添加
        elif hasattr(file_obj, 'name'):
            file_paths.append(file_obj.name)  # 如果是文件对象，获取name属性
        else:
             logger.warning(f"跳过无法识别的文件类型: {type(file_obj)}")


    if not file_paths:
        return None, "无法获取有效的文件路径"

    # 更新进度
    progress(0, desc=f"正在准备处理{subject}作业...")

    # 处理图像
    try:
        # 处理图像
        results = processor.process_images_gemini25_pro(file_paths, subject=subject)  # 传入subject参数

        # 更新进度
        progress(1, desc="处理完成")

        # 获取处理摘要
        summary = results.get("summary", f"成功处理了 {len(file_paths)} 个文件")

        # 提取详细信息用于显示
        details = ""
        for result in results.get("results", []):
            if "error" in result:
                details += f"❌ {Path(result['image_path']).name}: {result['error']}\n\n"
            else:
                details += f"✅ {Path(result['image_path']).name}: 成功处理\n"
                details += f"- 结果保存于: {result['result_path']}\n"
                if "display_text" in result:
                    details += f"- 识别内容预览:\n{result['display_text'][:200]}...\n\n"

        combined_summary = f"{summary}\n\n{details}"

        # 返回预览第一个图像和处理摘要
        # 确保返回的是有效路径，而不是文件对象
        preview_path = file_paths[0] if file_paths else None
        return preview_path, combined_summary
    except Exception as e:
        logger.error(f"处理图像时出错: {str(e)}")
        return None, f"处理失败: {str(e)}"

def get_example_images():
    """获取示例图片列表"""
    resources_path = Path(__file__).parent.parent.parent / "resources/错题本原始资料20250411"
    example_images = []
    if resources_path.exists():
        for file in resources_path.glob("*.png"):
            example_images.append(str(file))
    return example_images

def create_upload_page():
    """创建作业上传页面"""
    db = Database()

    with gr.Column() as upload_page:
        gr.Markdown("## 作业上传与错题录入")

        with gr.Tabs() as upload_tabs:
            # 图片上传标签页
            with gr.TabItem("图片上传"):
                with gr.Column(variant="panel"):
                    subject_select = gr.Dropdown(
                        choices=["数学", "物理", "化学"],
                        label="选择学科",
                        value="数学"
                    )

                    with gr.Row(equal_height=True):
                        with gr.Column(scale=2, variant="panel"):
                            # 上传作业部分
                            file_input = gr.File(
                                label="上传作业图片",
                                file_types=["image"],
                                file_count="multiple" # 允许多文件
                            )
                            upload_button = gr.Button("开始处理", variant="primary")
                            
                            # 处理状态
                            status = gr.Textbox(label="处理状态", lines=8)

                            # 添加示例图片展示区域
                            example_gallery = gr.Gallery(
                                label="题库案例（双击选择）",
                                value=get_example_images(),
                                columns=4,
                                height=200,
                                show_label=True,
                                elem_id="example_gallery"
                            )

                        with gr.Column(scale=3, variant="panel"):
                            preview = gr.Image(label="预览", show_label=True)

                # 添加双击事件处理
                def gallery_select(evt: gr.SelectData):
                    """当用户点击示例库中的图片时调用"""
                    if evt.index is None: # 添加检查，防止evt.index为None
                        logger.warning("gallery_select 收到无效的 SelectData 事件")
                        # 可以返回空列表和 None，或者当前值（如果能获取）
                        return gr.update(), gr.update() # 使用 gr.update() 表示不改变当前值

                    try:
                        example_list = get_example_images()
                        if evt.index >= len(example_list):
                             logger.error(f"gallery_select 索引 {evt.index} 超出范围 (列表长度: {len(example_list)})")
                             return gr.update(), gr.update()

                        selected_path = example_list[evt.index]
                        logger.info(f"用户从 gallery 选择了: {selected_path}")
                        # --- 修改点 ---
                        # 返回一个包含单个路径的列表给 file_input
                        # 返回单个路径字符串给 preview
                        return [selected_path], selected_path
                    except Exception as e:
                         logger.error(f"gallery_select 处理出错: {e}")
                         return gr.update(), gr.update()


                example_gallery.select(
                    fn=gallery_select,
                    inputs=None,  # inputs 应为 None 或空列表 []
                    outputs=[file_input, preview]
                )
            # 手动录入标签页
            with gr.TabItem("手动录入"):
                with gr.Column(variant="panel"):
                    gr.Markdown("### 错题信息")

                    with gr.Row(equal_height=True):
                        with gr.Column(scale=5):
                            question_text = gr.Textbox(
                                label="题目内容",
                                placeholder="请输入题目内容...",
                                lines=6
                            )

                        with gr.Column(scale=1):
                            with gr.Row():
                                save_btn = gr.Button("保存错题", variant="primary")
                                clear_btn = gr.Button("清空表单", variant="secondary")

                    with gr.Row():
                        subject = gr.Dropdown(
                            choices=["数学", "物理", "化学"],
                            label="学科",
                            value="数学"
                        )
                        question_type = gr.Dropdown(
                            choices=["选择题", "填空题", "判断题", "问答题"],
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

                    save_result = gr.Markdown()

            # 批量导入标签页
            with gr.TabItem("批量导入"):
                with gr.Column(variant="panel"):
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
                            gen_sample_btn = gr.Button("生成示例错题", variant="primary", interactive=False)

                        gen_result = gr.Markdown()

                        # 显示生成的数据
                        gen_data_display = gr.DataFrame(
                            headers=["题目ID", "学科", "题型", "难度", "创建时间"],
                            label="生成的数据预览",
                            visible=False,
                            wrap=True
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

        # 生成示例数据
        def generate_samples(count):
            try:
                # 确保count是整数
                count = int(count)
                if count <= 0:
                    return "❌ 生成数量必须大于0", gr.update(visible=False)

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
                    return f"✅ 成功生成 {len(question_ids)} 条示例错题数据", gr.update(visible=True, value=df)

                return f"✅ 成功生成 {len(question_ids)} 条示例错题数据，但无法获取详细信息", gr.update(visible=False)

            except Exception as e:
                return f"❌ 生成示例数据失败: {str(e)}", gr.update(visible=False)

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

        # 使用Gradio 的进度条功能
        upload_button.click(
            fn=process_images,
            inputs=[file_input, subject_select],  # 添加subject_select作为输入
            outputs=[preview, status]
        )

        gen_sample_btn.click(
            generate_samples,
            inputs=[sample_count],
            outputs=[gen_result, gen_data_display]
        )

    return upload_page