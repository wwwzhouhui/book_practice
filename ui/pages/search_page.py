import gradio as gr

def create_search_page():
    with gr.Column():
        gr.Markdown("## 错题查询")
        
        with gr.Row():
            with gr.Column(scale=2):
                search_input = gr.Textbox(
                    label="搜索关键词",
                    placeholder="输入学生姓名、题目类型或日期..."
                )
                search_button = gr.Button("开始搜索")
            
            with gr.Column(scale=3):
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
        
        with gr.Row():
            results = gr.Dataframe(
                headers=["题目ID", "科目", "题型", "错误类型", "提交时间"],
                label="搜索结果"
            )
            
        with gr.Row():
            export_button = gr.Button("导出结果")
            status = gr.Label(label="导出状态")