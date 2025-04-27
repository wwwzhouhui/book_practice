import os
import re
import logging
from pathlib import Path
from .base_exporter import BaseExporter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.colors import black

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExporter(BaseExporter):
    """PDF导出器，直接生成PDF文件"""
    
    def __init__(self):
        """初始化PDF导出器"""
        super().__init__()
        self._setup_fonts()
        
    def _setup_fonts(self):
        """设置PDF使用的字体"""
        try:
            # 定义中文字体和数学字体
            self.chinese_font_name = None
            self.math_font_name = None
            self.fallback_font_name = None
            
            # 尝试加载中文字体
            chinese_fonts = [
                # Windows常见中文字体
                ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
                ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
                ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttc"),
                # 项目本地字体
                ("SimSun", os.path.join(os.getcwd(), "fonts", "simsun.ttc")),
                ("SimHei", os.path.join(os.getcwd(), "fonts", "simhei.ttf")),
                ("Microsoft YaHei", os.path.join(os.getcwd(), "fonts", "msyh.ttc")),
            ]
            
            # 尝试加载数学字体
            math_fonts = [
                # Windows常见数学字体
                ("STIXTwoMath", "C:/Windows/Fonts/STIXTWOMATH-REGULAR.TTF"),
                ("Cambria Math", "C:/Windows/Fonts/cambria.ttc"),
                ("Arial Unicode MS", "C:/Windows/Fonts/ARIALUNI.TTF"),
                # 项目本地字体
                ("STIXTwoMath", os.path.join(os.getcwd(), "fonts", "STIXTwoMath-Regular.ttf")),
                ("Cambria Math", os.path.join(os.getcwd(), "fonts", "cambria.ttc")),
                ("Arial Unicode MS", os.path.join(os.getcwd(), "fonts", "ARIALUNI.TTF")),
            ]
            
            # 注册并选择中文字体
            for font_name, font_path in chinese_fonts:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        logger.info(f"已注册中文字体: {font_name} ({font_path})")
                        if self.chinese_font_name is None:
                            self.chinese_font_name = font_name
                    except Exception as e:
                        logger.warning(f"注册字体 {font_name} 失败: {str(e)}")
            
            # 注册并选择数学字体
            for font_name, font_path in math_fonts:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        logger.info(f"已注册数学字体: {font_name} ({font_path})")
                        if self.math_font_name is None:
                            self.math_font_name = font_name
                    except Exception as e:
                        logger.warning(f"注册字体 {font_name} 失败: {str(e)}")
            
            # 如果没有找到中文字体，使用内置字体
            if self.chinese_font_name is None:
                logger.warning("未找到中文字体，使用默认字体")
                self.chinese_font_name = "Helvetica"
            
            # 如果没有找到数学字体，使用中文字体
            if self.math_font_name is None:
                logger.warning("未找到数学字体，使用中文字体代替")
                self.math_font_name = self.chinese_font_name
                
            # 设置通用回退字体
            self.fallback_font_name = "Helvetica"
            
            # 创建适用范围更广的符号映射
            self._create_symbol_mappings()
            
        except Exception as e:
            logger.error(f"设置PDF字体时出错: {str(e)}")
            # 出现错误时设置默认字体
            self.chinese_font_name = "Helvetica"
            self.math_font_name = "Helvetica"
            self.fallback_font_name = "Helvetica"
    
    def _create_symbol_mappings(self):
        """创建符号映射，用于识别特殊字符"""
        # 数学符号列表
        self.math_symbols = set('∫∑∏∂∇Δδεθλμπστφω∞±×÷=≠≈≤≥√∛∜¹²³⁴⁵⁶⁷⁸⁹⁰ⁿ₁₂₃₄₅₆₇₈₉₀∈∉∋∌⊂⊃⊆⊇⊄⊅⊊⊋∪∩⊎⊖⊕⊗⊘⊙∀∃∄∴∵∝')
        
        # 常见上标、下标、分数符号
        self.superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
            'n': 'ⁿ', 'i': 'ⁱ'
        }
        
        self.subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
            '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎'
        }
        
        # 特殊处理字符替换映射
        self.char_replacement = {
            '·': '*',     # 点乘号替换
            '×': '*',     # 乘号替换
            '÷': '/',     # 除号替换
            '−': '-',     # 减号替换
            '–': '-',     # 连字符替换
            ''': "'",     # 引号替换
            ''': "'",     # 引号替换
            '"': '"',     # 引号替换
            '"': '"',     # 引号替换
            '…': '...',   # 省略号替换
            # 可以添加更多的替换规则
        }
        
        # 创建中文字符范围集合
        self.cjk_ranges = [
            (0x4E00, 0x9FFF),   # CJK统一汉字
            (0x3400, 0x4DBF),   # CJK统一汉字扩展A
            (0x20000, 0x2A6DF), # CJK统一汉字扩展B
            (0x2A700, 0x2B73F), # CJK统一汉字扩展C
            (0x2B740, 0x2B81F), # CJK统一汉字扩展D
            (0x2B820, 0x2CEAF), # CJK统一汉字扩展E
            (0xF900, 0xFAFF),   # CJK兼容汉字
            (0x3000, 0x303F),   # CJK标点符号
            (0xFF00, 0xFFEF)    # 全角ASCII、全角标点
        ]
        
        # 特殊处理标点符号
        self.special_punctuation = set('，。、；：""''（）【】《》？！…—')
    
    def _create_styles(self):
        """创建文档样式"""
        styles = getSampleStyleSheet()
        
        # 创建自定义样式 - 中文
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=self.chinese_font_name,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=22  # 行间距增加
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading2',
            fontName=self.chinese_font_name,
            fontSize=14,
            textColor=colors.blue,
            spaceAfter=6,
            leading=18  # 行间距增加
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading3',
            fontName=self.chinese_font_name,
            fontSize=12,
            textColor=colors.green,
            spaceAfter=6,
            leading=16  # 行间距增加
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading3Blue',
            fontName=self.chinese_font_name,
            fontSize=12,
            textColor=colors.steelblue,
            spaceAfter=6,
            leading=16  # 行间距增加
        ))
        
        # 修改Normal样式以使用中文字体
        styles["Normal"].fontName = self.chinese_font_name
        styles["Normal"].leading = 16  # 增加行间距
        
        # 创建混合字体样式，增加行间距和字间距
        styles.add(ParagraphStyle(
            name='MixedContent',
            fontName=self.chinese_font_name,  # 默认使用中文字体
            fontSize=12,
            spaceAfter=6,
            leading=16,  # 增加行间距
            wordSpacing=1.2,  # 增加字间距
            charSpace=0.1,    # 增加字符间距
            allowWidows=1,    # 允许段落最后一行单独出现在下一页
            allowOrphans=1    # 允许段落第一行单独出现在上一页
        ))
        
        return styles
    
    def _is_chinese_char(self, char):
        """判断是否为中文字符"""
        if not char:
            return False
        
        # 检查是否是中文标点
        if char in self.special_punctuation:
            return True
        
        # 使用预定义的CJK范围检查
        codepoint = ord(char)
        for start, end in self.cjk_ranges:
            if start <= codepoint <= end:
                return True
        
        return False
    
    def _is_math_char(self, char):
        """判断是否为数学符号"""
        if not char:
            return False
        
        # 直接检查数学符号集
        if char in self.math_symbols:
            return True
        
        # 检查是否是上标或下标字符
        if char in set(self.superscript_map.values()) or char in set(self.subscript_map.values()):
            return True
        
        # 简单的判断是否可能是数学表达式的一部分
        if char in '+-*/^()[]{}|<>=.:,':
            return True
        
        return False
    
    def _is_math_context(self, text, pos, window=5):
        """检查字符是否处于数学上下文中"""
        if not text or pos >= len(text):
            return False
        
        start = max(0, pos - window)
        end = min(len(text), pos + window + 1)
        context = text[start:end]
        
        # 检查上下文中的数学符号数量
        math_count = sum(1 for c in context if self._is_math_char(c))
        
        # 特定数学表达式的模式
        math_patterns = [
            r'[a-zA-Z]\^[0-9]',     # 指数表示：a^2
            r'[a-zA-Z]_[0-9]',      # 下标表示：a_1
            r'[0-9]+\.[0-9]+',      # 小数：3.14
            r'[0-9]+/[0-9]+',       # 分数：1/2
            r'[+\-*/=<>]',          # 运算符
            r'\([^)]*\)',           # 括号表达式
            r'\[[^]]*\]',           # 方括号表达式
            r'\{[^}]*\}'            # 花括号表达式
        ]
        
        # 如果上下文中包含足够的数学符号或匹配数学模式
        if math_count >= 2:
            return True
        
        for pattern in math_patterns:
            if re.search(pattern, context):
                return True
        
        return False
    
    def _prepare_text_for_pdf(self, text):
        """预处理文本，使其适合PDF渲染"""
        if not text:
            return text
        
        # 替换特殊字符
        for old, new in self.char_replacement.items():
            text = text.replace(old, new)
        
        # 处理HTML特殊字符，防止被解释为标签
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # 确保上标下标符号正确显示
        # 这部分代码保留原样，不应替换成HTML实体
        
        return text
    
    def _segment_text(self, text):
        """将文本分段，识别中文、数学和混合部分"""
        if not text:
            return []
        
        # 预处理文本
        text = self._prepare_text_for_pdf(text)
        
        # 记录各段落及其类型
        segments = []
        current_segment = ""
        current_type = "normal"  # 默认为普通文本
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # 确定当前字符类型
            if self._is_chinese_char(char):
                char_type = "chinese"
            elif self._is_math_char(char) or self._is_math_context(text, i):
                char_type = "math"
            elif char.isalpha() or char.isdigit():
                # 判断英文和数字是否处于数学上下文
                if self._is_math_context(text, i):
                    char_type = "math"
                else:
                    char_type = "normal"
            else:
                char_type = "normal"
            
            # 如果类型变化，保存当前段落
            if char_type != current_type and current_segment:
                segments.append((current_segment, current_type))
                current_segment = ""
                current_type = char_type
            
            # 添加当前字符到段落
            current_segment += char
            i += 1
        
        # 添加最后一个段落
        if current_segment:
            segments.append((current_segment, current_type))
        
        return segments
    
    def _apply_font_to_segments(self, segments):
        """应用字体到已分段的文本"""
        result = []
        
        for segment, segment_type in segments:
            if not segment.strip():
                # 保留空白字符
                result.append(segment)
                continue
            
            if segment_type == "chinese":
                font_name = self.chinese_font_name
            elif segment_type == "math":
                font_name = self.math_font_name
            else:
                # 普通文本使用中文字体
                font_name = self.chinese_font_name
            
            # 添加字体标签
            result.append(f'<span fontName="{font_name}">{segment}</span>')
        
        return ''.join(result)
    
    def _robust_text_processing(self, text):
        """强健的文本处理流程，确保所有文本正确渲染"""
        if not text:
            return text
        
        try:
            # 1. 分段识别文本
            segments = self._segment_text(text)
            
            # 2. 应用合适的字体
            processed_text = self._apply_font_to_segments(segments)
            
            # 3. 添加额外的安全处理
            # 确保不会出现未关闭的标签
            tag_pattern = r'<span fontName="([^"]+)">([^<]*)<\/span>'
            if not all(re.match(tag_pattern, tag) for tag in re.findall(r'<span[^>]*>.*?</span>', processed_text)):
                # 如果有不匹配的标签，回退到更安全的处理方式
                logger.warning("检测到不匹配的标签，回退到安全模式")
                processed_text = f'<span fontName="{self.chinese_font_name}">{text}</span>'
            
            return processed_text
        except Exception as e:
            logger.error(f"文本处理过程中出错: {str(e)}")
            # 回退到最安全的处理方式
            return f'<span fontName="{self.chinese_font_name}">{text}</span>'
    
    def export_questions(self, questions, output_path=None, include_answers=False):
        """
        导出题目到PDF文件
        
        Args:
            questions: 题目数据列表
            output_path: 输出文件路径，如果为None则使用默认路径
            include_answers: 是否包含答案
            
        Returns:
            输出文件路径
        """
        try:
            # 如果未指定输出路径，使用默认路径
            if output_path is None:
                file_suffix = "题目和答案" if include_answers else "题目"
                output_path = self.get_default_filename(f"错题_{file_suffix}", "pdf")
            
            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                allowSplitting=1,  # 允许内容分页
                title="错题集",
                author="自动生成"
            )
            
            # 获取样式
            styles = self._create_styles()
            
            # 创建内容元素列表
            elements = []
            
            # 添加标题
            title_text = "错题集" if not include_answers else "错题集（含答案）"
            elements.append(Paragraph(title_text, styles["ChineseTitle"]))
            elements.append(Spacer(1, 12))
            
            # 遍历每道题目
            for i, question in enumerate(questions, 1):
                # 题目标题
                heading_text = f"{i}. [{question['subject']}] [{question['question_type']}] [难度: {'★' * question['difficulty']}]"
                heading_processed = self._robust_text_processing(heading_text)
                elements.append(Paragraph(heading_processed, styles["ChineseHeading2"]))
                
                # 题目内容
                question_text = question.get("question_text", "")
                processed_text = self._robust_text_processing(question_text)
                elements.append(Paragraph(processed_text, styles["MixedContent"]))
                elements.append(Spacer(1, 6))  # 添加额外空间
                
                # 如果包含答案
                if include_answers:
                    # 答案标题
                    elements.append(Paragraph(
                        self._robust_text_processing("正确答案:"), 
                        styles["ChineseHeading3"]
                    ))
                    
                    # 答案内容
                    answer_text = question.get("correct_answer", "")
                    processed_answer = self._robust_text_processing(answer_text)
                    elements.append(Paragraph(processed_answer, styles["MixedContent"]))
                    elements.append(Spacer(1, 6))  # 添加额外空间
                    
                    # 如果有解析
                    if question.get("explanation"):
                        # 解析标题
                        elements.append(Paragraph(
                            self._robust_text_processing("解析:"), 
                            styles["ChineseHeading3Blue"]
                        ))
                        
                        # 解析内容
                        explanation_text = question.get("explanation", "")
                        processed_explanation = self._robust_text_processing(explanation_text)
                        elements.append(Paragraph(processed_explanation, styles["MixedContent"]))
                        elements.append(Spacer(1, 6))  # 添加额外空间
                
                # 添加分隔线（除了最后一题）
                if i < len(questions):
                    elements.append(Paragraph("_" * 50, styles["Normal"]))
                    elements.append(Spacer(1, 12))
            
            # 构建PDF时添加错误处理
            try:
                doc.build(elements)
                logger.info(f"成功导出PDF到: {output_path}")
            except Exception as build_error:
                logger.error(f"构建PDF时出错: {str(build_error)}")
                # 尝试使用更安全的方式重建元素
                logger.info("尝试使用安全模式重建PDF...")
                
                # 重置元素列表
                safe_elements = []
                safe_elements.append(Paragraph(title_text, styles["ChineseTitle"]))
                safe_elements.append(Spacer(1, 12))
                
                # 使用最简单的处理方式
                for i, question in enumerate(questions, 1):
                    # 题目标题 - 只使用中文字体
                    heading_text = f"{i}. [{question['subject']}] [{question['question_type']}] [难度: {'★' * question['difficulty']}]"
                    safe_elements.append(Paragraph(
                        f'<span fontName="{self.chinese_font_name}">{heading_text}</span>', 
                        styles["ChineseHeading2"]
                    ))
                    
                    # 题目内容 - 只使用中文字体
                    safe_elements.append(Paragraph(
                        f'<span fontName="{self.chinese_font_name}">{question.get("question_text", "")}</span>', 
                        styles["MixedContent"]
                    ))
                    
                    if include_answers:
                        # 答案标题
                        safe_elements.append(Paragraph(
                            f'<span fontName="{self.chinese_font_name}">正确答案:</span>', 
                            styles["ChineseHeading3"]
                        ))
                        
                        # 答案内容
                        safe_elements.append(Paragraph(
                            f'<span fontName="{self.chinese_font_name}">{question.get("correct_answer", "")}</span>', 
                            styles["MixedContent"]
                        ))
                        
                        # 解析
                        if question.get("explanation"):
                            safe_elements.append(Paragraph(
                                f'<span fontName="{self.chinese_font_name}">解析:</span>', 
                                styles["ChineseHeading3Blue"]
                            ))
                            
                            safe_elements.append(Paragraph(
                                f'<span fontName="{self.chinese_font_name}">{question.get("explanation", "")}</span>', 
                                styles["MixedContent"]
                            ))
                    
                    # 分隔线
                    if i < len(questions):
                        safe_elements.append(Paragraph("_" * 50, styles["Normal"]))
                        safe_elements.append(Spacer(1, 12))
                
                # 尝试使用安全模式构建
                try:
                    doc = SimpleDocTemplate(
                        output_path,
                        pagesize=A4,
                        rightMargin=72,
                        leftMargin=72,
                        topMargin=72,
                        bottomMargin=72
                    )
                    doc.build(safe_elements)
                    logger.info(f"使用安全模式成功导出PDF到: {output_path}")
                except Exception as safe_build_error:
                    logger.error(f"安全模式构建PDF也失败: {str(safe_build_error)}")
                    raise
            
            return output_path
            
        except Exception as e:
            logger.error(f"导出PDF失败: {str(e)}")
            raise

def main():
    """测试函数"""
    exporter = PDFExporter()
    
    # 测试数据 - 包含各种情况的混合文本
    questions = [
        {
            "id": 1,
            "subject": "数学",
            "question_type": "选择题",
            "difficulty": 3,
            "question_text": "已知函数f(x) = 1/(x^2 + 1)，求∫_0^1 f(x) dx的值。",
            "correct_answer": "π/4",
            "explanation": "解：∫_0^1 1/(x^2 + 1) dx = arctan(x)|_0^1 = arctan(1) - arctan(0) = π/4 - 0 = π/4"
        },
        {
            "id": 2,
            "subject": "物理",
            "question_type": "填空题",
            "difficulty": 2,
            "question_text": "一个质量为m的物体从高度h处自由落下，落地时的速度为多少？",
            "correct_answer": "v = √(2gh)",
            "explanation": "根据能量守恒定律，重力势能转化为动能：mgh = 1/2mv^2，解得v = √(2gh)"
        },
        {
            "id": 3,
            "subject": "数学",
            "question_type": "问答题", 
            "difficulty": 3,
            "question_text": "先化简, 再求值: a³ · (-b³)² + (-1/2 ab²)³, 其中 a=-2, b=1.",
            "correct_answer": "-5",
            "explanation": "解析:\n错误在于化简步骤，合并同类项时出错：a³b⁶ + (-1/8 a³b⁶) 应为 (1 - 1/8)a³b⁶ = 7/8 a³b⁶。\n学生误算为 -1/8 a³b⁶。"
        },
        {
            "id": 4,
            "subject": "数学",
            "question_type": "问答题",
            "difficulty": 4,
            "question_text": "已知 a^b = 2, b^a = 3, 比较a, b的大小。(a, b均为大于1的数)",
            "correct_answer": "b > a",
            "explanation": "取对数得 b*ln(a)=ln(2), a*ln(b)=ln(3), 故 ln(a)/a = ln(2)/(ab), ln(b)/b = ln(3)/(ab)。因 ln(3) > ln(2), 故 ln(b)/b > ln(a)/a. 考虑函数 g(x) = (ln x)/x 在(1,e)上单调递增, 且可证 a,b 均属于(1, e), 因此 b > a."
        },
        {
            "id": 5,
            "subject": "数学",
            "question_type": "计算题",
            "difficulty": 1,
            "question_text": "当m=-1时, y = 3 + 4^m = 3 + 4^(-1) = 3 + 1/4 = 12/4 + 1/4 = 13/4.",
            "correct_answer": "13/4",
            "explanation": "当m=-1时, y = 3 + 4^m = 3 + 4^(-1) = 3 + 1/4 = 12/4 + 1/4 = 13/4."
        }
    ]
    
    # 导出测试
    output_path = exporter.export_questions(questions, include_answers=True)
    print(f"PDF已导出到: {output_path}")

if __name__ == "__main__":
    main()