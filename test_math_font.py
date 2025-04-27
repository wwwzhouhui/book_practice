import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import numpy as np
from io import BytesIO
import logging
import tempfile
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MathFontTester:
    """测试STIX数学字体渲染各种数学公式的能力"""
    
    def __init__(self, font_path, chinese_font_path=None):
        """初始化字体测试器"""
        self.font_path = font_path
        self.chinese_font_path = chinese_font_path
        self.setup_font()
        
    def setup_font(self):
        """设置STIX字体和中文字体，增加检查确保字体加载"""
        stix_font_found = False
        # 设置STIX数学字体
        if self.font_path and os.path.exists(self.font_path):
            try:
                # 检查文件是否是有效的字体文件 (基本检查)
                if not self.font_path.lower().endswith(('.ttf', '.otf')):
                     logger.warning(f"提供的STIX字体路径可能不是有效的字体文件: {self.font_path}")
                
                # 添加STIX字体到matplotlib的字体管理器
                font_files = font_manager.findSystemFonts(fontpaths=os.path.dirname(self.font_path))
                for font_file in font_files:
                    if os.path.basename(font_file) == os.path.basename(self.font_path):
                        font_manager.fontManager.addfont(font_file)
                        logger.info(f"尝试添加STIX字体: {font_file}")
                        stix_font_found = True
                        break
                
                if stix_font_found:
                    logger.info(f"成功添加STIX字体: {self.font_path}")
                    # 强制重建字体缓存，确保新添加的字体被识别
                    # 注意：这可能会比较慢，只在首次设置或字体更改时执行可能更好
                    try:
                        font_manager._load_fontmanager(try_read_cache=False)
                        logger.info("Matplotlib 字体缓存已强制重建。")
                    except Exception as e:
                        logger.warning(f"重建字体缓存时出错: {e}")

                    # 验证字体是否真的被添加到管理器中
                    stix_font_prop = font_manager.FontProperties(fname=self.font_path)
                    found_in_manager = font_manager.findfont(stix_font_prop, fallback_to_default=False)
                    if found_in_manager:
                         logger.info(f"验证成功：STIX字体 '{stix_font_prop.get_name()}' 已在 Matplotlib 字体管理器中找到。")
                    else:
                         logger.warning(f"验证失败：STIX字体 '{stix_font_prop.get_name()}' 未在 Matplotlib 字体管理器中找到，渲染可能失败。")

                else:
                     logger.error(f"未能将STIX字体添加到管理器: {self.font_path}")

            except Exception as e:
                logger.error(f"添加或验证STIX字体时发生异常: {str(e)}", exc_info=True)
        else:
            logger.error(f"STIX字体文件不存在或路径未提供: {self.font_path}")

        # --- 修改中文字体设置逻辑 ---
        chinese_font_set = False
        # 优先使用指定路径的中文字体
        if self.chinese_font_path and os.path.exists(self.chinese_font_path):
            try:
                # 添加中文字体到matplotlib的字体管理器
                font_manager.fontManager.addfont(self.chinese_font_path)
                logger.info(f"尝试添加指定中文字体: {self.chinese_font_path}")
                
                # 获取字体名称并设置为 sans-serif 的首选
                chinese_font_prop = font_manager.FontProperties(fname=self.chinese_font_path)
                font_name = chinese_font_prop.get_name()
                
                # 验证字体是否被管理器识别
                found_chinese = font_manager.findfont(chinese_font_prop, fallback_to_default=False)
                if found_chinese:
                    logger.info(f"验证成功：中文字体 '{font_name}' 已在管理器中找到。")
                    # 将找到的字体名放在列表最前面
                    current_sans_serif = mpl.rcParams['font.sans-serif']
                    if font_name not in current_sans_serif:
                         mpl.rcParams['font.sans-serif'].insert(0, font_name)
                    logger.info(f"已将 '{font_name}' 设置为首选 sans-serif 字体。当前列表: {mpl.rcParams['font.sans-serif']}")
                    chinese_font_set = True
                else:
                    logger.warning(f"验证失败：指定的中文字体 '{font_name}' 未在管理器中找到，将尝试系统字体。")

            except Exception as e:
                logger.error(f"添加或设置指定中文字体失败: {str(e)}")
        
        # 如果未设置指定字体，则尝试系统字体
        if not chinese_font_set:
            logger.info("未指定有效中文字体路径或设置失败，尝试查找系统字体...")
            system_fonts = ['SimHei', 'SimSun', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'sans-serif'] # 添加 'sans-serif' 作为最终备选
            
            for font in system_fonts:
                try:
                    # 检查字体是否可用
                    font_manager.findfont(font, fallback_to_default=False)
                    # 将找到的系统字体设置为首选
                    current_sans_serif = mpl.rcParams['font.sans-serif']
                    if font not in current_sans_serif:
                         mpl.rcParams['font.sans-serif'].insert(0, font)
                    logger.info(f"找到并设置系统字体 '{font}' 为首选 sans-serif 字体。当前列表: {mpl.rcParams['font.sans-serif']}")
                    chinese_font_set = True
                    break # 找到一个就停止
                except Exception:
                    logger.debug(f"系统字体 '{font}' 未找到或不可用。")
                    continue
            
            if not chinese_font_set:
                logger.warning("未能找到并设置任何可用的中文字体，中文可能无法正确显示。")
        # --- 中文字体设置逻辑结束 ---

        # 设置matplotlib参数
        if stix_font_found:
             mpl.rcParams['mathtext.fontset'] = 'stix'  # 使用STIX字体集
             logger.info("已设置 mathtext.fontset 为 'stix'")
        else:
             logger.warning("由于STIX字体加载失败，未设置 mathtext.fontset 为 'stix'，将使用默认数学字体。")

        # 设置 font.family 为 sans-serif，这样就会使用上面配置好的列表
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        logger.info("字体设置完成。")
    
    def render_formula(self, formula, filename=None, dpi=300, is_chinese=False):
        """渲染数学公式为图像"""
        # 创建一个图形
        fig = plt.figure(figsize=(10, 1.5))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        
        try:
            if is_chinese:
                # 直接渲染中文文本
                ax.text(0.5, 0.5, formula, 
                        size=16, ha='center', va='center')
            else:
                # 渲染数学公式
                ax.text(0.5, 0.5, f"${formula}$", 
                        size=16, ha='center', va='center', 
                        usetex=False)  # 使用matplotlib的mathtext而不是LaTeX
            
            # 保存图像
            if filename:
                # 确保目录存在
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0.1)
                logger.info(f"公式已保存到: {filename}")
            
            # 显示图像
            plt.show()
            
        except Exception as e:
            logger.error(f"渲染公式失败: {str(e)}")
        finally:
            plt.close(fig)
    
    def test_all_formulas(self, output_dir=None):
        """测试所有数学公式"""
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 测试数学公式
        self.test_math_formulas(output_dir)
        
        # 测试物理公式
        self.test_physics_formulas(output_dir)
        
        # 测试化学公式
        self.test_chemistry_formulas(output_dir)
    
    def test_math_formulas(self, output_dir=None):
        """测试数学公式"""
        math_formulas = [
            # 基本运算
            "1 + 2 = 3",
            "4 - 3 = 1",
            "2 \\times 3 = 6",
            "6 \\div 2 = 3",
            
            # 分数
            "\\frac{1}{2} + \\frac{1}{3} = \\frac{5}{6}",
            "\\frac{a+b}{c+d}",
            
            # 指数和对数
            "a^2 + b^2 = c^2",
            "2^3 = 8",
            "\\log_2 8 = 3",
            "\\log_{10} 100 = 2",
            
            # 根号
            "\\sqrt{4} = 2",
            "\\sqrt{a^2 + b^2}",
            "\\sqrt[3]{8} = 2",
            
            # 代数表达式
            "(a+b)^2 = a^2 + 2ab + b^2",
            "a^2 - b^2 = (a+b)(a-b)",
            
            # 方程和不等式
            "ax^2 + bx + c = 0",
            "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
            "a > b \\Rightarrow a + c > b + c",
            
            # 集合
            "A \\cup B",
            "A \\cap B",
            "x \\in A",
            "A \\subset B",
            
            # 几何
            "\\angle ABC = 90^{\\circ}",
            "\\triangle ABC",
            "\\overline{AB} = \\overline{CD}",
            
            # 三角函数
            "\\sin^2 \\theta + \\cos^2 \\theta = 1",
            "\\tan \\theta = \\frac{\\sin \\theta}{\\cos \\theta}",
            
            # 极限和导数
            "\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1",
            "\\frac{d}{dx}(x^2) = 2x",
            
            # 积分
            "\\int x^2 dx = \\frac{x^3}{3} + C",
            "\\int_0^1 x^2 dx = \\frac{1}{3}"
        ]
        
        logger.info("开始测试数学公式...")
        for i, formula in enumerate(math_formulas):
            logger.info(f"测试数学公式 {i+1}/{len(math_formulas)}: {formula}")
            if output_dir:
                filename = os.path.join(output_dir, f"math_{i+1}.png")
                self.render_formula(formula, filename)
            else:
                self.render_formula(formula)
    
    def test_physics_formulas(self, output_dir=None):
        """测试物理公式"""
        physics_formulas = [
            # 运动学
            "v = \\frac{s}{t}",
            "a = \\frac{\\Delta v}{\\Delta t}",
            "s = v_0 t + \\frac{1}{2}at^2",
            "v^2 - v_0^2 = 2as",
            
            # 牛顿定律
            "F = ma",
            "F = G\\frac{m_1 m_2}{r^2}",
            "F = k\\frac{q_1 q_2}{r^2}",
            
            # 功和能
            "W = Fs\\cos\\theta",
            "E_k = \\frac{1}{2}mv^2",
            "E_p = mgh",
            "P = \\frac{W}{t}",
            
            # 电学
            "I = \\frac{U}{R}",
            "R = \\rho\\frac{l}{S}",
            "P = UI",
            
            # 热学
            "Q = cm\\Delta t",
            "\\Delta E = Q + W",
            
            # 光学
            "\\frac{1}{f} = \\frac{1}{u} + \\frac{1}{v}",
            "n = \\frac{c}{v}",
            
            # 波动
            "v = \\lambda f",
            "f = \\frac{1}{T}"
        ]
        
        logger.info("开始测试物理公式...")
        for i, formula in enumerate(physics_formulas):
            logger.info(f"测试物理公式 {i+1}/{len(physics_formulas)}: {formula}")
            if output_dir:
                filename = os.path.join(output_dir, f"physics_{i+1}.png")
                self.render_formula(formula, filename)
            else:
                self.render_formula(formula)
    
    def test_chemistry_formulas(self, output_dir=None):
        """测试化学公式"""
        chemistry_formulas = [
            # 化学式
            "H_2O",
            "H_2SO_4",
            "Ca(OH)_2",
            "CuSO_4 \\cdot 5H_2O",
            
            # 化学反应方程式
            "2H_2 + O_2 \\rightarrow 2H_2O",
            "CaCO_3 \\rightarrow CaO + CO_2",
            "2NaOH + H_2SO_4 \\rightarrow Na_2SO_4 + 2H_2O",
            "Cu + 4HNO_3 \\rightarrow Cu(NO_3)_2 + 2NO_2 + 2H_2O",
            
            # 电离方程式
            "NaCl \\rightarrow Na^+ + Cl^-",
            "H_2SO_4 \\rightarrow 2H^+ + SO_4^{2-}",
            
            # 氧化还原反应
            "Fe^{2+} \\rightarrow Fe^{3+} + e^-",
            "MnO_4^- + 8H^+ + 5e^- \\rightarrow Mn^{2+} + 4H_2O",
            
            # 化学平衡
            "K_c = \\frac{[C]^c[D]^d}{[A]^a[B]^b}",
            "K_p = K_c(RT)^{\\Delta n}",
            
            # 热化学方程式
            "C + O_2 \\rightarrow CO_2 \\quad \\Delta H = -393.5 \\text{ kJ/mol}",
            
            # 气体定律
            "pV = nRT",
            "p_1V_1/T_1 = p_2V_2/T_2"
        ]
        
        logger.info("开始测试化学公式...")
        for i, formula in enumerate(chemistry_formulas):
            logger.info(f"测试化学公式 {i+1}/{len(chemistry_formulas)}: {formula}")
            if output_dir:
                filename = os.path.join(output_dir, f"chemistry_{i+1}.png")
                self.render_formula(formula, filename)
            else:
                self.render_formula(formula)

    def test_specific_line(self, output_dir=None):
        """测试特定的一行文本"""
        # 确保输出目录存在
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # 重新排版的公式文本，使用多行格式提高可读性
        specific_line = """取对数得：
$b\\ln(a)=\\ln(2)$, 
$a\\ln(b)=\\ln(3)$. 

故有：
$\\ln(a)/a = \\ln(2)/(ab)$, 
$\\ln(b)/b = \\ln(3)/(ab)$. 

因为$\\ln(3) > \\ln(2)$，
故$\\ln(b)/b > \\ln(a)/a$. 

9. [数学] [问答题] [难度: ★★★]
先化简, 再求值: a³ ⋅ (-b³)² + (-1/2 ab²)³, 其中 a=-2, b=1.
正确答案:

解析:
错误在于化简步骤，合并同类项时出错：a³b⁶ + (-1/8 a³b⁶) 应为 (1 - 1/8)a³b⁶ = 7/8 a³b⁶，学生误算为 -1/8 a³b⁶。
考虑函数$g(x) = (\\ln x)/x$在$(1,e)$上单调递增, 
且可证$a,b$均属于$(1,e)$, 
因此$b > a$."""
        
        logger.info("测试特定的一行文本...")
        if output_dir:
            filename = os.path.join(output_dir, "specific_line.png")
            self.render_mixed_content(specific_line, filename)
        else:
            self.render_mixed_content(specific_line)

    def test_mixed_content(self, output_dir=None):
        """测试中文和数学公式混合的内容"""
        # 确保输出目录存在
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        mixed_examples = [
            # 只保留用户指定的测试数据
            "错误在于化简步骤，合并同类项时出错：$a^3b^6 + (-1/8 a^3b^6)$ 应为 $(1 - 1/8)a^3b^6 = 7/8 a^3b^6$，学生误算为 $-1/8 a^3b^6$。"
        ]
        
        logger.info("开始测试指定的中文和数学公式混合内容...")
        for i, text in enumerate(mixed_examples): # 修正变量名 mixed_examles -> mixed_examples
            logger.info(f"测试混合内容 {i+1}/{len(mixed_examples)}")
            if output_dir:
                # 保存到特定文件名，方便查找
                filename = os.path.join(output_dir, f"mixed_error_analysis.png")
                self.render_mixed_content(text, filename)
            else:
                self.render_mixed_content(text)
    
    def render_mixed_content(self, text, filename=None, dpi=300):
        """渲染中文和数学公式混合的内容，增强的自适应布局避免挤压
           修改：移除函数内部的字体设置，依赖全局设置"""
        # --- 移除以下字体设置代码 ---
        # plt.rcParams.update(plt.rcParamsDefault)
        
        # # 设置中文字体
        # if self.chinese_font_path and os.path.exists(self.chinese_font_path):
        #     font_name = os.path.basename(self.chinese_font_path).split('.')[0]
        #     mpl.rcParams['font.sans-serif'] = [font_name, 'SimHei', 'SimSun', 'Microsoft YaHei']
        # else:
        #     mpl.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
        
        # # 设置数学字体
        # mpl.rcParams['mathtext.fontset'] = 'stix'
        # mpl.rcParams['font.family'] = 'sans-serif'
        # mpl.rcParams['axes.unicode_minus'] = False
        # --- 移除结束 ---

        # 记录当前生效的字体设置 (用于调试)
        logger.info(f"render_mixed_content - 当前 mathtext.fontset: {mpl.rcParams['mathtext.fontset']}")
        logger.info(f"render_mixed_content - 当前 font.sans-serif: {mpl.rcParams['font.sans-serif']}")
        logger.info(f"render_mixed_content - 当前 font.family: {mpl.rcParams['font.family']}")

        try:
            import re
            import traceback
            
            # 将文本拆分为行
            lines = text.split('\n')
            
            # 设置基本参数
            font_size = 14  # 基本字体大小
            max_width = 0.85  # 最大宽度比例（相对于图形宽度）- 减小以避免挤压
            margin = 0.08  # 增加左右边距
            line_spacing = 1.8  # 增加行间距倍数
            
            # 创建临时图形用于测量文本尺寸 - 使用更大的尺寸以获得更准确的度量
            temp_fig = plt.figure(figsize=(15, 2)) # 测量基于此尺寸
            temp_ax = temp_fig.add_subplot(111)
            temp_ax.set_axis_off()
            
            # 预处理每行，计算所需宽度和高度
            processed_lines = []
            max_line_width = 0
            total_height = 0
            
            for line in lines:
                # 分割行中的数学公式和普通文本
                parts = re.split(r'(\$[^$]+\$)', line)
                line_parts = []
                line_width = 0
                
                for part in parts:
                    if not part.strip():
                        continue
                        
                    if part.startswith('$') and part.endswith('$'):
                        # 数学公式
                        formula = part[1:-1]
                        text = f"${formula}$"
                        is_formula = True
                    else:
                        # 普通文本
                        text = part
                        is_formula = False
                    
                    # 测量文本宽度
                    t = temp_ax.text(0, 0, text, size=font_size, usetex=False)
                    renderer = temp_fig.canvas.get_renderer()
                    bbox = t.get_window_extent(renderer=renderer)
                    width_ratio = bbox.width / temp_fig.get_window_extent().width
                    height_ratio = bbox.height / temp_fig.get_window_extent().height
                    
                    # 给公式增加额外的空间
                    if is_formula:
                        width_ratio *= 1.1  # 给公式增加10%的宽度
                        height_ratio *= 1.1  # 给公式增加10%的高度
                    
                    t.remove()  # 移除临时文本
                    
                    line_parts.append({
                        'text': text,
                        'width': width_ratio,
                        'height': height_ratio,
                        'is_formula': is_formula
                    })
                    
                    line_width += width_ratio
                
                # 进行自动换行处理
                wrapped_lines = []
                current_line = []
                current_width = 0
                
                for part in line_parts:
                    # 处理非常长的单个部分 (如果单个部分超过最大宽度，暂时保留)
                    if part['width'] > max_width and not current_line:
                        # 把这个长部分当做单独的一行处理
                        wrapped_lines.append([part])
                        continue
                    
                    # 如果添加这部分后超过最大宽度，则开始新行
                    if current_width + part['width'] > max_width and current_line:
                        wrapped_lines.append(current_line)
                        current_line = []
                        current_width = 0
                    
                    current_line.append(part)
                    current_width += part['width']
                
                # 添加最后一行
                if current_line:
                    wrapped_lines.append(current_line)
                
                # 更新处理后的行
                for wrapped_line in wrapped_lines:
                    processed_lines.append(wrapped_line)
                    line_width = sum(part['width'] for part in wrapped_line)
                    max_line_width = max(max_line_width, line_width)
                    
                    # 计算行高 - 考虑每行中最高的元素并添加额外空间
                    line_height = max(part['height'] for part in wrapped_line) * 1.2
                    total_height += line_height
            
            # 关闭临时图形
            plt.close(temp_fig)
            
            # 根据内容比例调整图形宽高
            fig_width = 12  # 固定宽度
            
            # 计算合适的高度，确保有足够空间，但不会过高
            if len(processed_lines) <= 1:
                fig_height = 2  # 单行使用最小高度
            else:
                # 根据行数和行高确定合适的图高
                fig_height = max(3, total_height * line_spacing * 10)  # 确保足够高但不过高
            
            fig = plt.figure(figsize=(fig_width, fig_height))
            
            # 创建子图，使用全部空间
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 计算实际行高和间距
            total_rows = len(processed_lines)
            
            # 如果只有一行，简化处理
            if total_rows == 1:
                y_position = 0.5  # 居中放置
                line_height = 0.8  # 使用固定高度
            else:
                top_margin = 0.05  # 顶部留白
                bottom_margin = 0.05  # 底部留白
                available_height = 1.0 - top_margin - bottom_margin
                
                # 计算行间距和起始位置
                y_position = 1.0 - top_margin
                # 每行平均高度，包含间距
                effective_line_height = available_height / total_rows
            
            # 渲染每一行
            for i, line_parts in enumerate(processed_lines):
                # 对于多行内容，每行逐步递减位置
                if total_rows > 1:
                    y_position = 1.0 - top_margin - i * effective_line_height
                
                # 确定当前行的水平起始位置 (左对齐)
                x_position = margin
                
                # 对于居中对齐，可以计算当前行宽度并居中放置
                # 当前行总宽度
                line_width = sum(part['width'] for part in line_parts)
                # 如果行宽小于最大宽度，可以考虑居中放置
                if line_width < max_width and len(processed_lines) == 1:  # 只在单行情况下居中
                    x_position = (1 - line_width) / 2
                
                # 渲染行中的每一部分
                for part in line_parts:
                    # 渲染文本
                    if part['is_formula']:
                        # 渲染数学公式
                        text_obj = ax.text(x_position, y_position, part['text'], 
                                size=font_size, ha='left', va='center', 
                                usetex=False, color='black')
                    else:
                        # 渲染普通文本
                        text_obj = ax.text(x_position, y_position, part['text'], 
                                size=font_size, ha='left', va='center', 
                                family='sans-serif', color='black')
                    
                    # 获取实际渲染后的文本尺寸
                    renderer = fig.canvas.get_renderer()
                    bbox = text_obj.get_window_extent(renderer=renderer)
                    width_ratio = bbox.width / fig.get_window_extent().width
                    
                    # 更新位置，添加更多间距避免挤压
                    x_position += width_ratio * 1.05  # 增加间距系数
            
            # 保存图像
            if filename:
                # 确保目录存在
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0.15)  # 增加边距
                logger.info(f"混合内容已保存到: {filename}")
            
            # 显示图像
            plt.show()
            
        except Exception as e:
            logger.error(f"渲染混合内容失败: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            plt.close('all')  # 确保关闭所有图形
def main():
    """主函数"""
    # STIX字体路径 - 请确保这个路径是正确的！
    font_path = "d:/chat/xm/book_practice/fonts/STIXTwoMath-Regular.ttf"
    
    # --- 尝试找到中文字体路径 ---
    chinese_font_path = None  # 首先初始化为 None
    # 检查常见的 Windows 字体路径
    simhei_path = "C:/Windows/Fonts/simhei.ttf"
    simsun_path = "C:/Windows/Fonts/simsun.ttc"
    yahei_path = "C:/Windows/Fonts/msyh.ttc" # Microsoft YaHei

    if os.path.exists(simhei_path):
        chinese_font_path = simhei_path
        logger.info(f"找到中文字体: {chinese_font_path}")
    elif os.path.exists(simsun_path):
        chinese_font_path = simsun_path
        logger.info(f"找到中文字体: {chinese_font_path}")
    elif os.path.exists(yahei_path):
         chinese_font_path = yahei_path
         logger.info(f"找到中文字体: {chinese_font_path}")
    else:
        logger.warning("在常见路径中未找到 SimHei, SimSun 或 Microsoft YaHei 字体。将尝试系统默认。")
    # --- 中文字体路径查找结束 ---

    # 创建输出目录
    output_dir = "d:/chat/xm/book_practice/test_results/mixed_content" # 使用单独的子目录
    os.makedirs(output_dir, exist_ok=True)
    
    # --- 清除Matplotlib缓存（可选，但推荐在字体问题时尝试）---
    try:
        cache_dir = mpl.get_cachedir()
        if os.path.exists(cache_dir):
            import shutil
            # shutil.rmtree(cache_dir) # 谨慎使用：会删除所有缓存
            # 更安全的方式是删除字体列表缓存文件
            font_cache_files = [f for f in os.listdir(cache_dir) if 'fontlist' in f]
            for f_cache in font_cache_files:
                try:
                    os.remove(os.path.join(cache_dir, f_cache))
                    logger.info(f"已删除 Matplotlib 字体缓存文件: {f_cache}")
                except OSError as e:
                    logger.warning(f"无法删除字体缓存文件 {f_cache}: {e}")
            logger.info(f"Matplotlib 缓存目录: {cache_dir}")
        else:
            logger.info("Matplotlib 缓存目录未找到，无需清理。")
    except Exception as e:
        logger.warning(f"清理 Matplotlib 缓存时出错: {e}")
    # --- 清除缓存结束 ---

    # 创建字体测试器 - 现在 chinese_font_path 肯定已被定义
    tester = MathFontTester(font_path, chinese_font_path)
    
    # --- 单独测试指定的混合内容 ---
    logger.info("开始测试指定的混合内容渲染...")
    tester.test_mixed_content(output_dir) # 调用混合内容测试方法
    # --- 测试结束 ---

    # 注释掉其他测试
    # tester.test_math_formulas(output_dir)
    # tester.test_specific_line(output_dir)
    # tester.test_real_examples(output_dir)
    # tester.test_specific_formulas(output_dir)
    
    logger.info(f"混合内容测试完成，结果保存在: {output_dir}")

if __name__ == "__main__":
    main()