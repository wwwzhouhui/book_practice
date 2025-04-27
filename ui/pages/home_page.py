import gradio as gr
from modules.storage.database import Database
import pandas as pd
import time
import logging # 引入日志

logger = logging.getLogger(__name__)

# --- 将获取统计数据的函数移到 create_home_page 外部 ---
# 这样更容易从 create_home_page 返回它
# 它需要 db 实例，我们可以传递它或将其设为全局（传递更清晰）
def get_statistics(db: Database):
    """获取统计数据 (现在接收 db 实例作为参数)"""
    logger.info("开始获取统计数据...")
    try:
        stats = db.get_statistics()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        initial_msg = ""

        if stats["total_count"] == 0:
            # 如果没有数据，尝试生成示例数据
            logger.warning("数据库中未检测到数据，尝试生成示例数据。")
            try:
                #db.generate_sample_data(count=18)  # 每个学科每个难度至少一个
                stats = db.get_statistics()  # 重新获取统计数据
                initial_msg = "⚠️ 未检测到数据，已自动生成示例数据用于展示。"
                logger.info("示例数据生成成功。")
            except Exception as e:
                initial_msg = f"⚠️ 生成示例数据失败: {str(e)}"
                logger.error(f"生成示例数据失败: {e}", exc_info=True)
                # 返回默认空值和错误信息
                empty_df = pd.DataFrame(columns=["题目ID", "科目", "题型", "难度", "时间"])
                return "系统运行异常", current_time, "0", "0", initial_msg, empty_df
        else:
            logger.info(f"获取到 {stats['total_count']} 条错题数据。")


        # --- 生成统计文本 ---
        md_text = f"{initial_msg}\n\n### 错题统计\n\n**总错题数**: {stats['total_count']} 题\n\n"

        # 学科分布
        md_text += "#### 学科分布\n"
        if stats['subject_stats']:
            for subject, count in stats["subject_stats"].items():
                percent = (count / stats["total_count"]) * 100 if stats["total_count"] > 0 else 0
                md_text += f"- {subject}: {count}题 ({percent:.1f}%)\n"
        else:
            md_text += "- 暂无学科数据\n"

        # 难度分布
        md_text += "\n#### 难度分布\n"
        has_difficulty_data = False
        # 确保 difficulty_stats 是字典
        if isinstance(stats.get("difficulty_stats"), dict):
            for difficulty, count in stats["difficulty_stats"].items():
                if count > 0:
                    has_difficulty_data = True
                    stars = "⭐" * difficulty
                    percent = (count / stats["total_count"]) * 100 if stats["total_count"] > 0 else 0
                    md_text += f"- {stars}: {count}题 ({percent:.1f}%)\n"
        else:
             logger.warning("难度统计数据格式不正确或不存在。")


        if not has_difficulty_data:
            md_text += "- 暂无难度数据\n"

        # --- 准备最近错题数据 ---
        recent_df = pd.DataFrame(columns=["题目ID", "科目", "题型", "难度", "时间"]) # 默认空 DataFrame
        if stats["recent_questions"]:
            try:
                recent_data = {
                    "题目ID": [], "科目": [], "题型": [], "难度": [], "时间": []
                }
                for q in stats["recent_questions"]:
                    recent_data["题目ID"].append(q["id"])
                    recent_data["科目"].append(q.get("subject", "未知")) # 添加默认值
                    recent_data["题型"].append(q.get("question_type", "未知"))
                    recent_data["难度"].append("⭐" * q.get("difficulty", 0))
                    recent_data["时间"].append(q.get("created_at", "未知"))
                recent_df = pd.DataFrame(recent_data)
                logger.info(f"准备了 {len(stats['recent_questions'])} 条最近错题数据。")
            except Exception as df_e:
                logger.error(f"处理最近错题数据时出错: {df_e}", exc_info=True)
                md_text += f"\n\n⚠️ 处理最近错题时出错: {df_e}"


        # --- 返回更新所需的值 ---
        # 注意：processed_count 在当前的 get_statistics 中没有计算，暂时返回 "0"
        processed_val = "0" # 或者从 stats 中获取（如果数据库提供了的话）
        question_val = str(stats.get("total_count", 0))

        logger.info("统计数据获取和处理完成。")
        return "系统运行正常", current_time, processed_val, question_val, md_text, recent_df

    except Exception as e:
        error_msg = f"获取统计数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True) # 记录详细错误堆栈
        # 返回默认空值和错误信息
        empty_df = pd.DataFrame(columns=["题目ID", "科目", "题型", "难度", "时间"])
        return "系统运行异常", time.strftime("%Y-%m-%d %H:%M:%S"), "0", "0", error_msg, empty_df


def create_home_page():
    """创建首页"""
    # 初始化数据库 (每次页面创建时独立获取实例，或考虑单例模式)
    # 在这里创建 db 实例，确保它在 lambda 函数创建时可用
    db = Database()
    logger.info("创建首页 UI...")

    with gr.Column() as home_page:
        with gr.Row():
            gr.Markdown("""
            ### 欢迎使用辅导大师错题管理系统

            本系统可以帮助您:

            - 自动识别和分析学生作业
            - 快速定位错题并进行分类
            - 生成个性化的练习题
            """)

        # 系统状态卡片和数据预览
        with gr.Row(equal_height=True):
            with gr.Column(variant="panel", scale=1):
                gr.Markdown("### 系统状态")
                # 设置初始值为"加载中..."或默认值，将由 app.load 更新
                system_status = gr.Label(value="加载中...", label="状态", elem_id="system_status")
                last_refresh = gr.Label(value="-", label="最后刷新")

            with gr.Column(variant="panel", scale=1):
                gr.Markdown("### 数据概览")
                # 设置初始值为"-"或默认值
                processed_count = gr.Label(value="-", label="已处理作业数", elem_id="processed_count")
                question_count = gr.Label(value="-", label="错题总数", elem_id="question_count")

            # 错题数据统计部分
            with gr.Column(variant="panel", scale=2):
                gr.Markdown("### 错题数据统计")
                refresh_btn = gr.Button("刷新统计数据", variant="primary")

                with gr.Tabs() as display_tabs:
                    # 统计概览标签页
                    with gr.TabItem("统计概览"):
                        # 设置初始值为"正在加载..."或默认值
                        stats_md = gr.Markdown("正在加载统计数据...", elem_id="stats_overview")

                    # 最近错题标签页
                    with gr.TabItem("最近错题"):
                        with gr.Row():
                            # 设置初始值为空 DataFrame
                            recent_questions = gr.DataFrame(
                                headers=["题目ID", "科目", "题型", "难度", "时间"],
                                label="最近添加的错题",
                                wrap=True,
                                value=pd.DataFrame(columns=["题目ID", "科目", "题型", "难度", "时间"]) # 初始空 DF
                            )

                # 刷新按钮事件 (现在需要传递 db 实例)
                # 使用 lambda 来捕获当前的 db 实例给 get_statistics
                refresh_btn.click(
                    lambda: get_statistics(db), # 使用 lambda 捕获此作用域中的 db 实例
                    outputs=[system_status, last_refresh, processed_count, question_count, stats_md, recent_questions]
                )

                # 点击最近错题 (逻辑基本不变，但需要确保能从 DataFrame 获取数据)
                def on_question_click(evt: gr.SelectData, current_df: pd.DataFrame): # 接收当前 DataFrame 作为输入
                    if not evt or evt.index is None:
                        logger.warning("on_question_click: 无效的点击事件或索引。")
                        return

                    try:
                        row_index = evt.index[0]
                        # 从传入的 DataFrame 中获取 ID (检查非空和索引有效性)
                        if current_df is not None and not current_df.empty and 0 <= row_index < len(current_df):
                            question_id = current_df.iloc[row_index]["题目ID"]
                            gr.Info(f"已选择错题ID: {question_id}，请前往「错题查询」页面查看详情")
                            logger.info(f"用户点击了最近错题列表中的 ID: {question_id}")
                        else:
                             warning_msg = "无法获取选中的错题信息"
                             if current_df is None or current_df.empty:
                                 warning_msg += "，数据为空，请先刷新。"
                             else:
                                 warning_msg += f"，索引 {row_index} 无效。"
                             gr.Warning(warning_msg)
                             logger.warning(f"on_question_click: {warning_msg} (DataFrame is None or empty: {current_df is None or current_df.empty}, index: {row_index}, len: {len(current_df) if current_df is not None else 'N/A'})")
                    except Exception as e:
                        gr.Warning(f"查看错题详情失败: {str(e)}")
                        logger.error(f"on_question_click 处理出错: {e}", exc_info=True)

                # select 事件现在需要将 DataFrame 组件本身作为输入传递给处理函数
                recent_questions.select(
                    on_question_click,
                    inputs=[recent_questions], # 传递 DataFrame 组件，其 value 会作为参数传入
                    outputs=None # select 事件通常不直接更新输出，而是触发通知或状态变化
                )

    # --- 返回需要被 app.load 更新的组件 和 获取数据的函数 ---
    # 创建一个无参数的 lambda 函数，它在执行时会调用 get_statistics 并传入先前创建的 db 实例
    get_statistics_func = lambda: get_statistics(db)
    logger.info("首页 UI 创建完成，返回组件和数据获取函数。")

    # 返回 UI 块、所有需要更新的组件、以及用于加载数据的函数
    return home_page, system_status, last_refresh, processed_count, question_count, stats_md, recent_questions, get_statistics_func
