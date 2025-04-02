import gradio as gr
import os
import tempfile
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from modules.image_processing.image_processor import ImageProcessor

def process_images(files, progress=gr.Progress()):
    """处理上传的图像文件"""
    if not files:
        return None, "未选择文件"
    
    # 创建图像处理器
    processor = ImageProcessor()
    
    # 获取文件路径列表
    file_paths = [file.name for file in files]
    
    # 更新进度
    progress(0, desc="正在准备处理...")
    
    # 处理图像
    try:
        results = processor.process_images(file_paths)
        
        # 更新进度
        progress(1, desc="处理完成")
        
        # 处理结果
        summary = f"成功处理了 {len(file_paths)} 个文件"
        
        # 返回预览第一个图像
        return files[0], summary
    except Exception as e:
        return None, f"处理失败: {str(e)}"

def create_upload_page():
    with gr.Column():
        gr.Markdown("## 作业上传")
        
        with gr.Row():
            with gr.Column(scale=2):
                file_input = gr.File(
                    label="上传作业文件",
                    file_types=["image"],
                    file_count="multiple"
                )
                upload_button = gr.Button("开始处理", variant="primary")
            
            with gr.Column(scale=3):
                preview = gr.Image(label="预览", show_label=True)
                status = gr.Label(label="处理状态")
        
        with gr.Row():
            progress = gr.Progress(track_tqdm=True)
            result_text = gr.Textbox(label="识别概况", lines=3)
            
        # 设置处理函数
        upload_button.click(
            fn=process_images,
            inputs=[file_input, progress],
            outputs=[preview, result_text]
        )