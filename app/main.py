import gradio as gr
from pathlib import Path
import sys
import logging # 引入日志

# 配置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent # 使用 resolve() 获取绝对路径
sys.path.append(str(project_root))
logger.info(f"项目根目录已添加到 sys.path: {project_root}")

# Import page creation functions
try:
    from ui.pages.home_page import create_home_page
    from ui.pages.upload_page import create_upload_page
    from ui.pages.search_page import create_search_page
    from ui.pages.similar_page import create_similar_page
    logger.info("页面创建函数导入成功。")
except ImportError as e:
    logger.error(f"导入页面模块失败: {e}。请确保 'ui/pages' 目录在 Python 路径中，并且文件存在。", exc_info=True)
    # 可以在这里退出或抛出异常，因为没有页面应用无法运行
    sys.exit(f"错误：无法导入页面模块 - {e}")


def create_app():
    logger.info("开始创建 Gradio 应用...")
    # 创建Gradio应用
    app = gr.Blocks(title="作业识别系统", theme=gr.themes.Soft())

    # --- 用于存储从页面创建函数返回的组件的占位符 ---
    # 这些将在 app.load 中作为输出目标
    home_system_status = None
    home_last_refresh = None
    home_processed_count = None
    home_question_count = None
    home_stats_md = None
    home_recent_questions = None
    home_get_statistics_func = None # 用于存储数据获取函数的占位符

    with app:
        gr.Markdown("# 辅导大师--基于AI教育的错题管理系统")

        with gr.Tabs() as tabs:
            with gr.TabItem("首页"):
                logger.info("创建首页 Tab...")
                # 调用 create_home_page 并捕获返回的元素
                try:
                    # 确保 create_home_page 返回了正确数量的元素
                    returned_values = create_home_page()
                    if len(returned_values) == 8:
                        (
                            home_page_ui, # home_page UI 块本身
                            home_system_status,
                            home_last_refresh,
                            home_processed_count,
                            home_question_count,
                            home_stats_md,
                            home_recent_questions,
                            home_get_statistics_func # 捕获数据获取函数
                        ) = returned_values
                        logger.info("首页组件和数据获取函数已成功捕获。")
                    else:
                        logger.error(f"create_home_page 返回了 {len(returned_values)} 个值，预期为 8 个。")
                        gr.Markdown("❌ 加载首页时返回了预期之外的数据结构。")

                except Exception as e:
                    logger.error(f"创建首页 UI 时出错: {e}", exc_info=True)
                    # 如果创建失败，放置一个错误消息
                    gr.Markdown(f"❌ 加载首页组件时出错: {e}")

            with gr.TabItem("作业上传"):
                logger.info("创建作业上传 Tab...")
                try:
                    create_upload_page()
                    logger.info("作业上传页面创建成功。")
                except Exception as e:
                    logger.error(f"创建作业上传页面时出错: {e}", exc_info=True)
                    gr.Markdown(f"❌ 加载作业上传页面时出错: {e}")

            with gr.TabItem("错题查询"):
                logger.info("创建错题查询 Tab...")
                try:
                    create_search_page()
                    logger.info("错题查询页面创建成功。")
                except Exception as e:
                    logger.error(f"创建错题查询页面时出错: {e}", exc_info=True)
                    gr.Markdown(f"❌ 加载错题查询页面时出错: {e}")

            # 添加同类题生成页面
            with gr.TabItem("同类题生成"):
                logger.info("创建同类题生成 Tab...")
                try:
                    create_similar_page()
                    logger.info("同类题生成页面创建成功。")
                except Exception as e:
                    logger.error(f"创建同类题生成页面时出错: {e}", exc_info=True)
                    gr.Markdown(f"❌ 加载同类题生成页面时出错: {e}")

        # --- 自动刷新首页数据 ---
        # 确保所有必要的组件和函数都已成功从 create_home_page 获取
        logger.info("尝试设置 app.load 事件...")
        if all([
            home_system_status, home_last_refresh, home_processed_count,
            home_question_count, home_stats_md, home_recent_questions,
            callable(home_get_statistics_func) # 检查 home_get_statistics_func 是否可调用
        ]):
            try:
                app.load(
                    fn=home_get_statistics_func, # 从 create_home_page 返回的 lambda 函数
                    inputs=None, # home_get_statistics_func 不需要参数
                    outputs=[
                        home_system_status,
                        home_last_refresh,
                        home_processed_count,
                        home_question_count,
                        home_stats_md,
                        home_recent_questions
                    ],
                    # api_name=False # 如果不需要 API 端点可以禁用
                )
                logger.info("app.load 事件设置成功，首页将在加载时自动刷新。")
            except Exception as e:
                 logger.error(f"设置 app.load 事件时出错: {e}", exc_info=True)
                 # 可以在 UI 中显示错误，或者仅记录日志
        else:
            logger.warning("未能获取所有首页组件或数据获取函数，无法设置自动刷新。请检查 create_home_page 的返回值。")
            # 你可以在这里添加一个 gr.Markdown 提示用户首页可能需要手动刷新


    logger.info("Gradio 应用创建完成。")
    return app

if __name__ == "__main__":
    logger.info("应用程序开始执行...")
    try:
        app = create_app()
        logger.info("准备启动 Gradio 应用...")
        # 尝试在7860-7866范围内寻找可用端口
        for port in range(7860, 7867):
            try:
                app.launch(server_name="0.0.0.0", server_port=port)
                logger.info(f"Gradio 应用已在端口 {port} 启动。")
                break
            except OSError as e:
                if "Cannot find empty port" in str(e):
                    logger.warning(f"端口 {port} 已被占用，尝试下一个端口...")
                    continue
                else:
                    raise e
        else:
            logger.critical("无法在7860-7866范围内找到可用端口")
            sys.exit("致命错误：无法找到可用端口")
    except Exception as e:
        logger.critical(f"应用程序启动失败: {e}", exc_info=True)
        sys.exit(f"致命错误：无法启动应用程序 - {e}")
