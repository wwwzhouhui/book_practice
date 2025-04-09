import gradio as gr
from pathlib import Path
import sys
import os
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler('app.log', 'w', 'utf-8')  # 输出到文件
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ui.pages.home_page import create_home_page
from ui.pages.upload_page import create_upload_page
from ui.pages.search_page import create_search_page
from modules.storage.database import Database

# 确保数据目录和导出目录存在
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

exports_dir = project_root / "exports"
exports_dir.mkdir(exist_ok=True)

config_dir = project_root / "config"
config_dir.mkdir(exist_ok=True)

# 初始化数据库
db_path = data_dir / "homework.db"
db = Database(db_path)

def initialize_sample_data():
    """初始化示例数据，如果数据库为空"""
    try:
        # 检查是否有错题数据
        stats = db.get_statistics()
        if stats["total_count"] == 0:
            logger.info("数据库为空，生成示例数据...")
            db.generate_sample_data(count=15)  # 每个学科每个难度至少有一个错题
            logger.info("示例数据生成完成")
        else:
            logger.info(f"数据库已有 {stats['total_count']} 条错题数据")
    except Exception as e:
        logger.error(f"初始化示例数据时出错: {str(e)}")
        logger.error(traceback.format_exc())

def create_app():
    """创建Gradio应用"""
    # 初始化示例数据
    initialize_sample_data()
    
    # 创建Gradio应用主题
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
    )
    
    # 设置自定义CSS
    css = """
    .gradio-container {max-width: 1200px; margin: auto;}
    #error_questions_table {width: 100%;}
    .footer {text-align: center; margin-top: 20px; opacity: 0.7;}
    """
    
    app = gr.Blocks(
        title="智能作业识别系统", 
        theme=theme,
        css=css
    )
    
    with app:
        gr.Markdown("# 智能作业识别系统")
        
        with gr.Tabs() as tabs:
            with gr.TabItem("首页", id="home_tab"):
                home_page = create_home_page()
                
            with gr.TabItem("作业上传", id="upload_tab"):
                upload_page = create_upload_page()
                
            with gr.TabItem("错题查询", id="search_tab"):
                search_page = create_search_page()
        
        # 版权信息
        gr.Markdown("---\n© 2025 智能作业识别系统 | 版本: 1.0.0", elem_classes=["footer"])
    
    return app

if __name__ == "__main__":
    try:
        logger.info("启动智能作业识别系统...")
        app = create_app()
        app.launch(
            server_name="0.0.0.0", 
            server_port=7860, 
            show_error=True,
            debug=True
        )
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        logger.error(traceback.format_exc())