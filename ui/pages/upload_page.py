import gradio as gr

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
                upload_button = gr.Button("开始上传")
            
            with gr.Column(scale=3):
                preview = gr.Image(label="预览", show_label=True)
                status = gr.Label(label="处理状态")
        
        with gr.Row():
            progress = gr.Progress(track_tqdm=True)
            result = gr.Label(label="识别结果")