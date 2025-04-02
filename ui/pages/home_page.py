import gradio as gr

def create_home_page():
    with gr.Column():
        gr.Markdown("""
        ## 欢迎使用智能作业识别系统
        
        本系统可以帮助您：
        - 自动识别和分析学生作业
        - 快速定位错题并进行分类
        - 生成个性化的练习题
        - 同步数据到飞书平台
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 系统状态")
                gr.Label(value="系统运行正常", label="状态")
            
            with gr.Column(scale=1):
                gr.Markdown("### 今日统计")
                gr.Label(value="0", label="已处理作业数")
                gr.Label(value="0", label="识别题目数")