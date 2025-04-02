import gradio as gr
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ui.pages.home_page import create_home_page
from ui.pages.upload_page import create_upload_page
from ui.pages.search_page import create_search_page

def create_app():
    # 创建Gradio应用
    app = gr.Blocks(title="作业识别系统", theme=gr.themes.Soft())
    
    with app:
        gr.Markdown("# 智能作业识别系统")
        
        with gr.Tabs() as tabs:
            with gr.TabItem("首页"):
                create_home_page()
            
            with gr.TabItem("作业上传"):
                create_upload_page()
            
            with gr.TabItem("错题查询"):
                create_search_page()
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860)